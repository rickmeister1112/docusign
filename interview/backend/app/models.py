from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    """
    SQLAlchemy model for user accounts.
    Represents a user with email, hashed password, and account metadata.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(
        String, unique=True, index=True, nullable=False, comment="User's email address"
    )
    hashed_password = Column(
        String, nullable=False, comment="Hashed password for authentication"
    )
    is_active = Column(
        Boolean, default=True, comment="Whether the user account is active"
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Timestamp when user account was created",
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        comment="Timestamp when user account was last updated",
    )

    # Relationship to feedback entries
    feedbacks = relationship("Feedback", back_populates="user")
    # Relationship to upvotes
    upvotes = relationship("Upvote", back_populates="user")


class Feedback(Base):
    """
    SQLAlchemy model for feedback entries.
    Represents a feedback submission with text content, metadata, upvote count, and user association.
    """

    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False, comment="The feedback text content")
    upvotes = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of upvotes for this feedback",
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        comment="ID of the user who created this feedback",
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Timestamp when feedback was created",
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        comment="Timestamp when feedback was last updated",
    )

    # Relationship to user
    user = relationship("User", back_populates="feedbacks")
    # Relationship to upvotes
    upvote_records = relationship("Upvote", back_populates="feedback", cascade="all, delete-orphan")


class Upvote(Base):
    """
    SQLAlchemy model for tracking upvotes.
    Represents a user's upvote on a feedback entry (one user can only upvote once per feedback).
    """

    __tablename__ = "upvotes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        comment="ID of the user who upvoted",
    )
    feedback_id = Column(
        Integer,
        ForeignKey("feedback.id"),
        nullable=False,
        comment="ID of the feedback that was upvoted",
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Timestamp when upvote was created",
    )

    # Ensure a user can only upvote a feedback once
    __table_args__ = (
        UniqueConstraint('user_id', 'feedback_id', name='unique_user_feedback_upvote'),
    )

    # Relationships
    user = relationship("User", back_populates="upvotes")
    feedback = relationship("Feedback", back_populates="upvote_records")
