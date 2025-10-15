"""
Input validation utilities for enhanced security.
"""
import re
from typing import Tuple
from .config import settings


class PasswordValidator:
    """
    Validates password strength based on configured policy.
    Prevents weak passwords that are easy to crack.
    """
    
    # Common weak passwords to reject
    WEAK_PASSWORDS = {
        "password", "12345678", "password123", "qwerty123", "abc123456",
        "letmein123", "welcome123", "admin123", "user12345", "test12345",
        "password1", "123456789", "qwertyuiop", "123123123", "aaaaaaaa",
        "11111111", "00000000", "iloveyou", "sunshine", "princess"
    }
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        Validate password against security policy.
        
        Args:
            password: The password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
            - (True, "") if valid
            - (False, "error message") if invalid
        """
        # Check minimum length
        if len(password) < settings.MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {settings.MIN_PASSWORD_LENGTH} characters long"
        
        # Check for uppercase letter if required
        if settings.REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"
        
        # Check for lowercase letter if required
        if settings.REQUIRE_LOWERCASE and not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"
        
        # Check for digit if required
        if settings.REQUIRE_DIGIT and not re.search(r"\d", password):
            return False, "Password must contain at least one digit"
        
        # Check for special character if required
        if settings.REQUIRE_SPECIAL and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Password must contain at least one special character (!@#$%^&*...)"
        
        # Check against common weak passwords (case-insensitive)
        if password.lower() in PasswordValidator.WEAK_PASSWORDS:
            return False, "This password is too common. Please choose a more unique password"
        
        return True, ""
    
    @staticmethod
    def get_password_requirements() -> dict:
        """
        Get current password requirements for client-side display.
        
        Returns:
            Dictionary of password requirements
        """
        return {
            "min_length": settings.MIN_PASSWORD_LENGTH,
            "require_uppercase": settings.REQUIRE_UPPERCASE,
            "require_lowercase": settings.REQUIRE_LOWERCASE,
            "require_digit": settings.REQUIRE_DIGIT,
            "require_special": settings.REQUIRE_SPECIAL,
        }


class EmailValidator:
    """
    Validates email addresses with custom rules.
    """
    
    # Common disposable email domains to block
    DISPOSABLE_DOMAINS = {
        "tempmail.com", "throwaway.email", "guerrillamail.com",
        "10minutemail.com", "mailinator.com", "trash-mail.com"
    }
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Validate email address format and domain.
        
        Args:
            email: The email to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email or "@" not in email:
            return False, "Invalid email address"
        
        # Basic regex validation
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, email):
            return False, "Invalid email format"
        
        # Check for disposable email domains (optional - can be disabled)
        domain = email.split("@")[1].lower()
        if domain in EmailValidator.DISPOSABLE_DOMAINS:
            return False, "Disposable email addresses are not allowed"
        
        return True, ""

