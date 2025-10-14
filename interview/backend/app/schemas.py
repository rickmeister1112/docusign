from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional


# Authentication schemas
class UserBase(BaseModel):
    """
    Base Pydantic schema for user data validation.
    Contains the common fields shared between create and response operations.
    """

    email: EmailStr = Field(..., description="User's email address")


class UserCreate(UserBase):
    """
    Pydantic schema for creating new user accounts.
    Includes password for account creation.
    """

    password: str = Field(
        ..., min_length=8, description="User's password (minimum 8 characters)"
    )


class UserResponse(UserBase):
    """
    Pydantic schema for user response data.
    Includes all fields from UserBase plus database-generated fields.
    """

    id: int = Field(..., description="Unique identifier for the user")
    is_active: bool = Field(..., description="Whether the user account is active")
    created_at: datetime = Field(
        ..., description="Timestamp when user account was created"
    )
    updated_at: Optional[datetime] = Field(
        None, description="Timestamp when user account was last updated"
    )

    class Config:
        """
        Pydantic configuration for the schema.
        Enables ORM mode for automatic conversion from SQLAlchemy models.
        """

        from_attributes = True


class UserLogin(BaseModel):
    """
    Pydantic schema for user login requests.
    """

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class Token(BaseModel):
    """
    Pydantic schema for JWT token responses.
    """

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    """
    Pydantic schema for JWT token data.
    """

    email: Optional[str] = None


# Feedback schemas
class FeedbackBase(BaseModel):
    """
    Base Pydantic schema for feedback data validation.
    Contains the common fields shared between create and update operations.
    """

    text: str = Field(
        ..., min_length=1, max_length=1000, description="Feedback text content"
    )


class FeedbackCreate(FeedbackBase):
    """
    Pydantic schema for creating new feedback entries.
    Inherits from FeedbackBase and adds any creation-specific validation.
    """

    pass


class FeedbackUpdate(BaseModel):
    """
    Pydantic schema for updating existing feedback entries.
    All fields are optional to allow partial updates.
    """

    text: Optional[str] = Field(
        None, min_length=1, max_length=1000, description="Updated feedback text content"
    )


class FeedbackResponse(FeedbackBase):
    """
    Pydantic schema for feedback response data.
    Includes all fields from FeedbackBase plus database-generated fields and user information.
    """

    id: int = Field(..., description="Unique identifier for the feedback entry")
    upvotes: int = Field(..., description="Number of upvotes for this feedback")
    user_id: int = Field(..., description="ID of the user who created this feedback")
    user_email: str = Field(
        ..., description="Email of the user who created this feedback"
    )
    has_upvoted: bool = Field(
        default=False, description="Whether the current user has upvoted this feedback"
    )
    created_at: datetime = Field(..., description="Timestamp when feedback was created")
    updated_at: Optional[datetime] = Field(
        None, description="Timestamp when feedback was last updated"
    )

    class Config:
        """
        Pydantic configuration for the schema.
        Enables ORM mode for automatic conversion from SQLAlchemy models.
        """

        from_attributes = True


class UpvoteRequest(BaseModel):
    """
    Pydantic schema for upvote requests.
    """

    pass


class UpvoteResponse(BaseModel):
    """
    Pydantic schema for upvote response data.
    """

    id: int = Field(..., description="Unique identifier for the feedback entry")
    upvotes: int = Field(..., description="Updated number of upvotes for this feedback")
    has_upvoted: bool = Field(..., description="Whether the user has upvoted (true) or removed upvote (false)")
    message: str = Field(..., description="Action message (upvoted or removed upvote)")

    class Config:
        """
        Pydantic configuration for the schema.
        Enables ORM mode for automatic conversion from SQLAlchemy models.
        """

        from_attributes = True
