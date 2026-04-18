"""
Password security service for validation and management.

Implements password strength requirements and security checks.
"""

import re
from typing import Tuple


class PasswordSecurityService:
    """Service for password validation and security."""

    # Common weak passwords to block
    WEAK_PASSWORDS = {
        "password", "123456", "12345678", "qwerty", "abc123",
        "monkey", "1234567", "letmein", "trustno1", "dragon",
        "baseball", "111111", "iloveyou", "master", "sunshine",
        "ashley", "bailey", "passw0rd", "shadow", "123123"
    }

    MIN_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True

    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        Validate password strength.

        Requirements:
        - Minimum 8 characters
        - At least 1 uppercase letter
        - At least 1 lowercase letter
        - At least 1 digit
        - At least 1 special character (!@#$%^&*)
        - Not in common weak password list

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"

        # Check length
        if len(password) < PasswordSecurityService.MIN_LENGTH:
            return False, f"Password must be at least {PasswordSecurityService.MIN_LENGTH} characters long"

        # Check for uppercase
        if PasswordSecurityService.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"

        # Check for lowercase
        if PasswordSecurityService.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"

        # Check for digit
        if PasswordSecurityService.REQUIRE_DIGIT and not re.search(r'\d', password):
            return False, "Password must contain at least one digit"

        # Check for special character
        if PasswordSecurityService.REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*()_+=\-\[\]{};:\'",.<>?/\\|`~]', password):
            return False, "Password must contain at least one special character (!@#$%^&*)"

        # Check against common weak passwords
        if password.lower() in PasswordSecurityService.WEAK_PASSWORDS:
            return False, "This password is too common. Please choose a stronger password"

        return True, ""

    @staticmethod
    def get_password_strength_score(password: str) -> int:
        """
        Calculate password strength score (0-100).

        Args:
            password: Password to analyze

        Returns:
            Strength score from 0 to 100
        """
        score = 0

        # Length: 20 points for 8+ chars, +2 for each additional char (max 40)
        length_score = min(40, 20 + (max(0, len(password) - 8) * 2))
        score += length_score

        # Variety: 15 points for each type
        if re.search(r'[a-z]', password):
            score += 15
        if re.search(r'[A-Z]', password):
            score += 15
        if re.search(r'\d', password):
            score += 15
        if re.search(r'[!@#$%^&*()_+=\-\[\]{};:\'",.<>?/\\|`~]', password):
            score += 15

        return min(100, score)

    @staticmethod
    def get_password_strength_label(score: int) -> str:
        """
        Get human-readable password strength label.

        Args:
            score: Strength score (0-100)

        Returns:
            Strength label (Weak, Fair, Good, Strong, Very Strong)
        """
        if score < 30:
            return "Weak"
        elif score < 50:
            return "Fair"
        elif score < 70:
            return "Good"
        elif score < 85:
            return "Strong"
        else:
            return "Very Strong"

    @staticmethod
    def passwords_match(password1: str, password2: str) -> bool:
        """
        Check if two passwords match.

        Args:
            password1: First password
            password2: Second password

        Returns:
            True if passwords match
        """
        return password1 == password2
