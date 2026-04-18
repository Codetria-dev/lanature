"""
Two-Factor Authentication (2FA) service.

Implements TOTP (Time-based One-Time Password) for user authentication.
Uses pyotp for TOTP generation and validation.
Supports QR codes and backup codes for account recovery.
"""

import pyotp
import qrcode
import secrets
import string
from typing import List, Tuple
from io import BytesIO
import base64


class TwoFactorService:
    """Service for managing 2FA operations."""

    @staticmethod
    def generate_totp_secret(name: str, issuer: str = "LaNature") -> str:
        """
        Generate a new TOTP secret key.

        Args:
            name: User identifier (usually email)
            issuer: Service name for authenticator app

        Returns:
            Base32-encoded TOTP secret
        """
        secret = pyotp.random_base32()
        return secret

    @staticmethod
    def generate_qr_code(secret: str, name: str, issuer: str = "LaNature") -> str:
        """
        Generate QR code for TOTP setup.

        Args:
            secret: TOTP secret key
            name: User identifier (email)
            issuer: Service name

        Returns:
            Base64-encoded PNG image of QR code
        """
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(name=name, issuer_name=issuer)

        # Generate QR code image
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)
        img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode()

        return f"data:image/png;base64,{img_base64}"

    @staticmethod
    def generate_backup_codes(count: int = 10, length: int = 8) -> List[str]:
        """
        Generate backup codes for account recovery.

        Args:
            count: Number of codes to generate
            length: Length of each code

        Returns:
            List of backup codes (uppercase alphanumeric)
        """
        alphabet = string.ascii_uppercase + string.digits
        codes = []

        for _ in range(count):
            code = "".join(secrets.choice(alphabet) for _ in range(length))
            codes.append(code)

        return codes

    @staticmethod
    def verify_totp(secret: str, code: str, window: int = 1) -> bool:
        """
        Verify a TOTP code.

        Args:
            secret: User's TOTP secret
            code: 6-digit code to verify
            window: Time window for verification (tolerance in steps)

        Returns:
            True if code is valid, False otherwise
        """
        totp = pyotp.TOTP(secret)
        # Allow for small time drift (±window steps)
        return totp.verify(code, valid_window=window)

    @staticmethod
    def verify_backup_code(code: str, stored_codes: List[str]) -> Tuple[bool, List[str]]:
        """
        Verify and consume a backup code.

        Args:
            code: Backup code to verify
            stored_codes: List of remaining backup codes

        Returns:
            Tuple of (is_valid, updated_codes_list)
            If valid, code is removed from list
        """
        code_upper = code.upper().strip()

        if code_upper in stored_codes:
            # Remove the used code
            updated_codes = [c for c in stored_codes if c != code_upper]
            return True, updated_codes

        return False, stored_codes

    @staticmethod
    def get_totp_uri(secret: str, email: str, issuer: str = "LaNature") -> str:
        """
        Get TOTP URI for provisioning.

        Useful for displaying the manual entry key if QR scan fails.

        Args:
            secret: TOTP secret
            email: User email
            issuer: Service name

        Returns:
            TOTP provisioning URI
        """
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=email, issuer_name=issuer)
