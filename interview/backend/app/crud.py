from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from . import models, schemas
from .auth import get_password_hash


# User management functions
def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """
    Create a new user account in the database.

    Args:
        db: Database session
        user: User data to create

    Returns:
        Created user model instance
    """
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """
    Retrieve a specific user by ID.

    Args:
        db: Database session
        user_id: ID of the user to retrieve

    Returns:
        User model instance or None if not found
    """
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """
    Retrieve a specific user by email address.

    Args:
        db: Database session
        email: Email address of the user to retrieve

    Returns:
        User model instance or None if not found
    """
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """
    Retrieve a list of users with pagination.

    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return

    Returns:
        List of user model instances
    """
    return db.query(models.User).offset(skip).limit(limit).all()


# Feedback management functions
def create_feedback(
    db: Session, feedback: schemas.FeedbackCreate, user_id: int
) -> models.Feedback:
    """
    Create a new feedback entry in the database.

    Args:
        db: Database session
        feedback: Feedback data to create
        user_id: ID of the user creating the feedback

    Returns:
        Created feedback model instance
    """
    db_feedback = models.Feedback(text=feedback.text, user_id=user_id)
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


def get_feedback(db: Session, feedback_id: int) -> Optional[models.Feedback]:
    """
    Retrieve a specific feedback entry by ID.

    Args:
        db: Database session
        feedback_id: ID of the feedback to retrieve

    Returns:
        Feedback model instance or None if not found
    """
    return db.query(models.Feedback).filter(models.Feedback.id == feedback_id).first()


def get_feedback_list(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.Feedback]:
    """
    Retrieve a list of feedback entries with pagination.
    Ordered by upvotes (descending) then by creation date (newest first).

    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return

    Returns:
        List of feedback model instances
    """
    return (
        db.query(models.Feedback)
        .order_by(desc(models.Feedback.upvotes), desc(models.Feedback.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_user_feedback(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[models.Feedback]:
    """
    Retrieve a list of feedback entries for a specific user.

    Args:
        db: Database session
        user_id: ID of the user whose feedback to retrieve
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return

    Returns:
        List of feedback model instances for the user
    """
    return (
        db.query(models.Feedback)
        .filter(models.Feedback.user_id == user_id)
        .order_by(desc(models.Feedback.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def check_user_upvoted(db: Session, feedback_id: int, user_id: int) -> bool:
    """
    Check if a user has already upvoted a feedback entry.

    Args:
        db: Database session
        feedback_id: ID of the feedback
        user_id: ID of the user

    Returns:
        True if user has upvoted, False otherwise
    """
    upvote = db.query(models.Upvote).filter(
        models.Upvote.feedback_id == feedback_id,
        models.Upvote.user_id == user_id
    ).first()
    return upvote is not None


def toggle_upvote_feedback(db: Session, feedback_id: int, user_id: int) -> tuple[Optional[models.Feedback], bool, str]:
    """
    Toggle upvote for a feedback entry (add if not exists, remove if exists).

    Args:
        db: Database session
        feedback_id: ID of the feedback to upvote
        user_id: ID of the user upvoting

    Returns:
        Tuple of (feedback model instance or None if not found, upvoted status, message)
    """
    db_feedback = get_feedback(db, feedback_id)
    if db_feedback is None:
        return None, False, "Feedback not found"

    # Check if user has already upvoted
    existing_upvote = db.query(models.Upvote).filter(
        models.Upvote.feedback_id == feedback_id,
        models.Upvote.user_id == user_id
    ).first()

    if existing_upvote:
        # Remove upvote
        db.delete(existing_upvote)
        db_feedback.upvotes -= 1
        db.commit()
        db.refresh(db_feedback)
        return db_feedback, False, "Upvote removed"
    else:
        # Add upvote
        new_upvote = models.Upvote(user_id=user_id, feedback_id=feedback_id)
        db.add(new_upvote)
        db_feedback.upvotes += 1
        db.commit()
        db.refresh(db_feedback)
        return db_feedback, True, "Upvoted successfully"


def upvote_feedback(db: Session, feedback_id: int) -> Optional[models.Feedback]:
    """
    Increment the upvote count for a feedback entry.
    DEPRECATED: Use toggle_upvote_feedback instead for authenticated upvotes.

    Args:
        db: Database session
        feedback_id: ID of the feedback to upvote

    Returns:
        Updated feedback model instance or None if not found
    """
    db_feedback = get_feedback(db, feedback_id)
    if db_feedback is None:
        return None

    db_feedback.upvotes += 1
    db.commit()
    db.refresh(db_feedback)

    return get_feedback(db, feedback_id)


def update_feedback(
    db: Session, feedback_id: int, feedback: schemas.FeedbackUpdate, user_id: int
) -> Optional[models.Feedback]:
    """
    Update an existing feedback entry (only by the original author).

    Args:
        db: Database session
        feedback_id: ID of the feedback to update
        feedback: Updated feedback data
        user_id: ID of the user attempting to update

    Returns:
        Updated feedback model instance or None if not found or unauthorized
    """
    db_feedback = get_feedback(db, feedback_id)
    if db_feedback is None:
        return None

    # Check if user is the author of the feedback
    if db_feedback.user_id != user_id:
        return None

    # Update only provided fields
    update_data = feedback.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_feedback, field, value)

    db.commit()
    db.refresh(db_feedback)
    return db_feedback


def delete_feedback(db: Session, feedback_id: int, user_id: int) -> bool:
    """
    Delete a feedback entry from the database (only by the original author).

    Args:
        db: Database session
        feedback_id: ID of the feedback to delete
        user_id: ID of the user attempting to delete

    Returns:
        True if feedback was deleted, False if not found or unauthorized
    """
    db_feedback = get_feedback(db, feedback_id)
    if db_feedback is None:
        return False

    # Check if user is the author of the feedback
    if db_feedback.user_id != user_id:
        return False

    db.delete(db_feedback)
    db.commit()
    return True
