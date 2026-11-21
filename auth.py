"""
User Authentication, Security & Session Management module for Smart Citizen Governance Portal.
Provides bcrypt password hashing, input validation, registration, login,
password reset with OTP verification, and profile management.
"""

import os
import re
import bcrypt
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
import database
import otp


# ==========================================
# Password Hashing & Security
# ==========================================

def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt with a securely generated salt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Securely verifies a plaintext password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


# ==========================================
# Input Validation Helpers
# ==========================================

def validate_email(email: str) -> bool:
    """Validates email format using regex."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """Validates password complexity requirements."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain an uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain a lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain a digit."
    return True, ""


# ==========================================
# Registration & User Management
# ==========================================

def register_user(
    full_name: str,
    mobile: str,
    email: str,
    state: str,
    district: str,
    password: str,
    confirm_password: str,
    otp_code: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Registers a new citizen account.
    If SMS verification is configured, validates that OTP was verified.
    """
    # 1. Clean Inputs
    name_clean = full_name.strip()
    mobile_clean = re.sub(r"[^\d]", "", mobile.strip())
    email_clean = email.strip().lower()
    state_clean = state.strip()
    district_clean = district.strip()

    # 2. Validation Checks
    if not name_clean:
        return False, "Please enter your full name."
    if not otp.validate_mobile_format(mobile_clean):
        return False, "Please enter a valid 10-digit Indian mobile number."
    if not validate_email(email_clean):
        return False, "Please enter a valid email address."
    if not state_clean or state_clean == "Select State":
        return False, "Please select your state."
    if not district_clean or district_clean == "Select District":
        return False, "Please select your district."
    if password != confirm_password:
        return False, "Passwords do not match."

    valid_pw, pw_msg = validate_password_strength(password)
    if not valid_pw:
        return False, pw_msg

    # 3. Check for existing mobile or email
    existing_user = database.execute_query(
        "SELECT id, mobile, email FROM users WHERE mobile = ? OR email = ?",
        (mobile_clean, email_clean)
    )
    if existing_user:
        if existing_user[0]["mobile"] == mobile_clean:
            return False, "An account with this mobile number already exists. Please log in."
        else:
            return False, "An account with this email address already exists. Please log in."

    # 4. OTP Verification Handling
    is_verified = 0
    if otp.is_sms_configured():
        if not otp_code:
            return False, "Please enter the OTP verification code sent to your mobile."
        verified, v_msg = otp.verify_otp(mobile_clean, otp_code, purpose="signup")
        if not verified:
            return False, v_msg
        is_verified = 1
    else:
        # Fail closed by default. Only local development may explicitly opt out.
        allow_unverified = os.getenv("ALLOW_UNVERIFIED_SIGNUP", "false").strip().lower() in {"1", "true", "yes"}
        if not allow_unverified:
            return False, "Registration requires SMS verification. Configure the SMS provider or explicitly enable ALLOW_UNVERIFIED_SIGNUP for local development only."
        is_verified = 0

    # 5. Secure Hash and Insert
    pw_hash = hash_password(password)
    try:
        user_id = database.execute_insert(
            """
            INSERT INTO users (full_name, mobile, email, state, district, password_hash, is_mobile_verified, is_admin)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (name_clean, mobile_clean, email_clean, state_clean, district_clean, pw_hash, is_verified)
        )
        return True, "Account registered successfully! You can now log in."
    except Exception as e:
        return False, f"Registration failed due to a database error: {str(e)}"


def authenticate_user(identifier: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Authenticates a citizen using either Mobile Number or Email + Password.
    Returns (success, message, user_dict_without_password_hash).
    """
    ident_clean = identifier.strip()
    if not ident_clean or not password:
        return False, "Please enter your mobile/email and password.", None

    clean_mobile = re.sub(r"[^\d]", "", ident_clean)
    email_clean = ident_clean.lower()

    # Query by mobile or email
    users = database.execute_query(
        "SELECT * FROM users WHERE mobile = ? OR email = ?",
        (clean_mobile, email_clean)
    )

    if not users:
        return False, "Invalid mobile/email or password.", None

    user = users[0]
    if not verify_password(password, user["password_hash"]):
        return False, "Invalid mobile/email or password.", None

    # Sanitize user dict (remove password_hash)
    user_dict = {
        "id": user["id"],
        "full_name": user["full_name"],
        "mobile": user["mobile"],
        "email": user["email"],
        "state": user["state"],
        "district": user["district"],
        "is_mobile_verified": bool(user["is_mobile_verified"]),
        "is_admin": bool(user["is_admin"]),
        "created_at": user["created_at"]
    }

    return True, "Login successful.", user_dict


# ==========================================
# Forgot Password & Password Reset
# ==========================================

def request_password_reset_otp(identifier: str) -> Tuple[bool, str]:
    """
    Sends a password reset OTP to the registered mobile.
    To avoid account enumeration, returns standard messaging.
    """
    ident_clean = identifier.strip()
    if not ident_clean:
        return False, "Please enter your registered mobile number or email."

    clean_mobile = re.sub(r"[^\d]", "", ident_clean)
    email_clean = ident_clean.lower()

    users = database.execute_query(
        "SELECT mobile FROM users WHERE mobile = ? OR email = ?",
        (clean_mobile, email_clean)
    )

    if not users:
        # Standard message to avoid account enumeration
        return False, "If the account exists, an OTP will be dispatched. Please check your SMS provider configuration."

    target_mobile = users[0]["mobile"]
    return otp.send_otp(target_mobile, purpose="forgot_password")


def complete_password_reset(
    identifier: str,
    otp_code: str,
    new_password: str,
    confirm_password: str
) -> Tuple[bool, str]:
    """
    Verifies OTP and resets the user's password securely.
    """
    ident_clean = identifier.strip()
    clean_mobile = re.sub(r"[^\d]", "", ident_clean)
    email_clean = ident_clean.lower()

    if not ident_clean:
        return False, "Please enter your registered mobile number or email."

    if new_password != confirm_password:
        return False, "New passwords do not match."

    valid_pw, pw_msg = validate_password_strength(new_password)
    if not valid_pw:
        return False, pw_msg

    users = database.execute_query(
        "SELECT id, mobile FROM users WHERE mobile = ? OR email = ?",
        (clean_mobile, email_clean)
    )

    if not users:
        return False, "Unable to find an account associated with this information."

    user = users[0]
    target_mobile = user["mobile"]

    if otp.is_sms_configured():
        verified, v_msg = otp.verify_otp(target_mobile, otp_code, purpose="forgot_password")
        if not verified:
            return False, v_msg
    else:
        return False, "SMS verification is not configured. Add the SMS provider credentials to enable real OTP."

    new_hash = hash_password(new_password)
    database.execute_update(
        "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (new_hash, user["id"])
    )

    return True, "Password has been reset successfully. You can now log in with your new password."


# ==========================================
# Profile Management
# ==========================================

def update_user_profile(
    user_id: int,
    full_name: str,
    email: str,
    state: str,
    district: str
) -> Tuple[bool, str]:
    """
    Updates safe profile fields for a citizen.
    Does NOT allow modifying mobile number directly without re-verification.
    """
    name_clean = full_name.strip()
    email_clean = email.strip().lower()
    state_clean = state.strip()
    district_clean = district.strip()

    if not name_clean:
        return False, "Full name cannot be empty."
    if not validate_email(email_clean):
        return False, "Please enter a valid email address."

    # Check if email is taken by another user
    existing = database.execute_query(
        "SELECT id FROM users WHERE email = ? AND id != ?",
        (email_clean, user_id)
    )
    if existing:
        return False, "This email is already in use by another account."

    database.execute_update(
        """
        UPDATE users
        SET full_name = ?, email = ?, state = ?, district = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (name_clean, email_clean, state_clean, district_clean, user_id)
    )

    return True, "Profile updated successfully."

