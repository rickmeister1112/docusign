from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uvicorn
import time

from . import crud, models, schemas, auth
from .database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Feedback CRUD API with Authentication",
    description="A CRUD API for managing feedback submissions with user authentication and upvote functionality",
    version="1.0.0",
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


# Authentication endpoints
@app.post(
    "/auth/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Args:
        user: User registration data
        db: Database session dependency

    Returns:
        Created user account details

    Raises:
        HTTPException: If email already exists
    """
    # Check if user already exists
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    return crud.create_user(db=db, user=user)


@app.post("/auth/login", response_model=schemas.Token)
def login_user(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user and return JWT token.

    Args:
        user_credentials: User login credentials
        db: Database session dependency

    Returns:
        JWT access token

    Raises:
        HTTPException: If credentials are invalid
    """
    user = auth.authenticate_user(
        db, email=user_credentials.email, password=user_credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

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
def create_feedback(
    feedback: schemas.FeedbackCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new feedback entry (requires authentication).

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
def read_feedback_list(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_optional)
):
    """
    Retrieve a list of feedback entries with pagination.
    Ordered by upvotes (descending) then by creation date (newest first).

    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        db: Database session dependency
        current_user: Optional current authenticated user

    Returns:
        List of feedback entries ordered by upvotes and creation date
    """
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
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of feedback entries created by the current user.

    Args:
        current_user: Current authenticated user
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        db: Database session dependency

    Returns:
        List of feedback entries created by the current user
    """
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
def upvote_feedback(
    feedback_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Toggle upvote for a feedback entry (requires authentication).
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
