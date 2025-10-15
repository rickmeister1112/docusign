from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import uvicorn
import time
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import SQLAlchemyError

from . import crud, models, schemas, auth
from .database import engine, get_db
from .config import settings
from .rate_limit import limiter, rate_limit_auth, rate_limit_write, rate_limit_read
from .validators import PasswordValidator, EmailValidator
from .middleware import RequestLoggingMiddleware
from .logging_config import log_auth_attempt, app_logger

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="A CRUD API for managing feedback submissions with user authentication and upvote functionality",
    version=settings.APP_VERSION,
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add database error handler
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Global handler for database errors.
    Returns a clean error message without exposing database details.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A database error occurred. Please try again later."}
    )

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Configure CORS from environment variables
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/")
def read_root():
    """
    Root endpoint providing API information.
    """
    return {
        "message": "Feedback CRUD API with Authentication",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/auth/password-requirements")
def get_password_requirements():
    """
    Get current password policy requirements.
    Useful for client-side validation and user guidance.
    
    Returns:
        Dictionary containing password requirements
    """
    return PasswordValidator.get_password_requirements()


@app.post("/admin/sync-upvote-counts")
def sync_all_upvote_counts(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Admin endpoint: Sync all feedback upvote counts with actual Upvote table data.
    Fixes any inconsistencies between stored counts and actual upvotes.
    
    Note: In production, this should be restricted to admin users only.
    
    Args:
        current_user: Current authenticated user
        db: Database session dependency
        
    Returns:
        Summary of synced feedback counts
    """
    try:
        # Get all feedback
        all_feedback = db.query(models.Feedback).all()
        
        synced_count = 0
        fixed_count = 0
        
        for feedback in all_feedback:
            actual_count = crud.get_actual_upvote_count(db, feedback.id)
            if feedback.upvotes != actual_count:
                old_count = feedback.upvotes
                feedback.upvotes = actual_count
                fixed_count += 1
                app_logger.info(f"Fixed upvote count for feedback {feedback.id}: {old_count} -> {actual_count}")
            synced_count += 1
        
        if fixed_count > 0:
            db.commit()
        
        return {
            "message": "Upvote count sync completed",
            "total_feedback": synced_count,
            "fixed_count": fixed_count,
            "status": "success"
        }
    except SQLAlchemyError as e:
        db.rollback()
        app_logger.error(f"Error syncing all upvote counts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync upvote counts"
        )


# Authentication endpoints
@app.post(
    "/auth/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit(rate_limit_auth())
def register_user(request: Request, user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account with validation and rate limiting (5/min).

    Args:
        user: User registration data
        db: Database session dependency

    Returns:
        Created user account details

    Raises:
        HTTPException: If email already exists or validation fails
    """
    # Validate email format
    email_valid, email_error = EmailValidator.validate_email(user.email)
    if not email_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=email_error
        )
    
    # Validate password strength
    password_valid, password_error = PasswordValidator.validate_password(user.password)
    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=password_error
        )
    
    # Check if user already exists
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    return crud.create_user(db=db, user=user)


@app.post("/auth/login", response_model=schemas.Token)
@limiter.limit(rate_limit_auth())
def login_user(request: Request, user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user and return JWT token with rate limiting (5/min).

    Args:
        user_credentials: User login credentials
        db: Database session dependency

    Returns:
        JWT access token

    Raises:
        HTTPException: If credentials are invalid
    """
    # Get client IP for logging
    client_ip = request.client.host if request.client else "unknown"
    
    user = auth.authenticate_user(
        db, email=user_credentials.email, password=user_credentials.password
    )
    if not user:
        # Log failed authentication attempt
        log_auth_attempt(user_credentials.email, success=False, ip_address=client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Log successful authentication
    log_auth_attempt(user.email, success=True, ip_address=client_ip)
    
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me", response_model=schemas.UserResponse)
def get_current_user_info(
    current_user: models.User = Depends(auth.get_current_active_user),
):
    """
    Get current authenticated user information.

    Args:
        current_user: Current authenticated user dependency

    Returns:
        Current user account details
    """
    return current_user


# Feedback endpoints (now protected with authentication)
@app.post(
    "/feedback/",
    response_model=schemas.FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit(rate_limit_write())
def create_feedback(
    request: Request,
    feedback: schemas.FeedbackCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new feedback entry with rate limiting (20/min).

    Args:
        feedback: Feedback data to create
        current_user: Current authenticated user
        db: Database session dependency

    Returns:
        Created feedback entry with full details
    """
    db_feedback = crud.create_feedback(
        db=db, feedback=feedback, user_id=current_user.id
    )

    # Return feedback with user information
    return {**db_feedback.__dict__, "user_email": current_user.email, "has_upvoted": False}


@app.get("/feedback/", response_model=List[schemas.FeedbackResponse])
@limiter.limit(rate_limit_read())
def read_feedback_list(
    request: Request,
    skip: int = 0, 
    limit: int = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_optional)
):
    """
    Retrieve a list of feedback entries with validated pagination and rate limiting (100/min).
    Ordered by upvotes (descending) then by creation date (newest first).

    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return (max: {MAX_PAGE_SIZE})
        db: Database session dependency
        current_user: Optional current authenticated user

    Returns:
        List of feedback entries ordered by upvotes and creation date
        
    Raises:
        HTTPException: If pagination parameters are invalid
    """
    # Validate skip parameter
    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skip parameter must be non-negative"
        )
    
    # Set default limit if not provided
    if limit is None:
        limit = settings.DEFAULT_PAGE_SIZE
    
    # Validate limit parameter
    if limit < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be at least 1"
        )
    
    if limit > settings.MAX_PAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Limit cannot exceed {settings.MAX_PAGE_SIZE}"
        )
    
    feedback_list = crud.get_feedback_list(db, skip=skip, limit=limit)

    result = []
    for feedback in feedback_list:
        user = crud.get_user(db, feedback.user_id)
        feedback_dict = feedback.__dict__.copy()
        feedback_dict["user_email"] = user.email if user else "Unknown"
        # Check if current user has upvoted
        if current_user:
            feedback_dict["has_upvoted"] = crud.check_user_upvoted(db, feedback.id, current_user.id)
        else:
            feedback_dict["has_upvoted"] = False
        result.append(feedback_dict)

    return result


@app.get("/feedback/my", response_model=List[schemas.FeedbackResponse])
def read_my_feedback(
    current_user: models.User = Depends(auth.get_current_active_user),
    skip: int = 0,
    limit: int = None,
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of feedback entries created by the current user with validated pagination.

    Args:
        current_user: Current authenticated user
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return (max: {MAX_PAGE_SIZE})
        db: Database session dependency

    Returns:
        List of feedback entries created by the current user
        
    Raises:
        HTTPException: If pagination parameters are invalid
    """
    # Validate skip parameter
    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skip parameter must be non-negative"
        )
    
    # Set default limit if not provided
    if limit is None:
        limit = settings.DEFAULT_PAGE_SIZE
    
    # Validate limit parameter
    if limit < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be at least 1"
        )
    
    if limit > settings.MAX_PAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Limit cannot exceed {settings.MAX_PAGE_SIZE}"
        )
    
    feedback_list = crud.get_user_feedback(
        db, user_id=current_user.id, skip=skip, limit=limit
    )

    result = []
    for feedback in feedback_list:
        feedback_dict = feedback.__dict__.copy()
        feedback_dict["user_email"] = current_user.email
        feedback_dict["has_upvoted"] = crud.check_user_upvoted(db, feedback.id, current_user.id)
        result.append(feedback_dict)

    return result


@app.get("/feedback/{feedback_id}", response_model=schemas.FeedbackResponse)
def read_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_optional)
):
    """
    Retrieve a specific feedback entry by ID.

    Args:
        feedback_id: ID of the feedback to retrieve
        db: Database session dependency
        current_user: Optional current authenticated user

    Returns:
        Feedback entry details

    Raises:
        HTTPException: If feedback with given ID is not found
    """
    db_feedback = crud.get_feedback(db, feedback_id=feedback_id)
    if db_feedback is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback with ID {feedback_id} not found",
        )

    user = crud.get_user(db, db_feedback.user_id)
    feedback_dict = db_feedback.__dict__.copy()
    feedback_dict["user_email"] = user.email if user else "Unknown"
    # Check if current user has upvoted
    if current_user:
        feedback_dict["has_upvoted"] = crud.check_user_upvoted(db, feedback_id, current_user.id)
    else:
        feedback_dict["has_upvoted"] = False

    return feedback_dict


@app.post("/feedback/{feedback_id}/upvote", response_model=schemas.UpvoteResponse)
@limiter.limit(rate_limit_write())
def upvote_feedback(
    request: Request,
    feedback_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Toggle upvote for a feedback entry with rate limiting (20/min).
    If user hasn't upvoted, adds an upvote. If user has upvoted, removes the upvote.

    Args:
        feedback_id: ID of the feedback to upvote
        current_user: Current authenticated user
        db: Database session dependency

    Returns:
        Updated feedback entry with new upvote count and upvote status

    Raises:
        HTTPException: If feedback with given ID is not found
    """
    db_feedback, has_upvoted, message = crud.toggle_upvote_feedback(
        db, feedback_id=feedback_id, user_id=current_user.id
    )
    if db_feedback is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback with ID {feedback_id} not found",
        )
    return {
        "id": db_feedback.id,
        "upvotes": db_feedback.upvotes,
        "has_upvoted": has_upvoted,
        "message": message
    }


@app.put("/feedback/{feedback_id}", response_model=schemas.FeedbackResponse)
def update_feedback(
    feedback_id: int,
    feedback: schemas.FeedbackUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update an existing feedback entry (only by the original author).

    Args:
        feedback_id: ID of the feedback to update
        feedback: Updated feedback data
        current_user: Current authenticated user
        db: Database session dependency

    Returns:
        Updated feedback entry details

    Raises:
        HTTPException: If feedback with given ID is not found or user is not authorized
    """
    db_feedback = crud.update_feedback(
        db, feedback_id=feedback_id, feedback=feedback, user_id=current_user.id
    )
    if db_feedback is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback with ID {feedback_id} not found or you are not authorized to update it",
        )

    # Add user email and upvote status to response
    feedback_dict = db_feedback.__dict__.copy()
    feedback_dict["user_email"] = current_user.email
    feedback_dict["has_upvoted"] = crud.check_user_upvoted(db, feedback_id, current_user.id)

    return feedback_dict


@app.delete("/feedback/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback(
    feedback_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Delete a feedback entry (only by the original author).

    Args:
        feedback_id: ID of the feedback to delete
        current_user: Current authenticated user
        db: Database session dependency

    Raises:
        HTTPException: If feedback with given ID is not found or user is not authorized
    """
    success = crud.delete_feedback(db, feedback_id=feedback_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback with ID {feedback_id} not found or you are not authorized to delete it",
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
