"""
SMS OTP Provider & Verification Architecture for Smart Citizen Governance Portal.
Provides abstraction for external SMS verification gateways (Twilio Verify),
cooldown enforcement, expiration checks, attempt limits, and safe status reporting.
"""

import os
import re
from datetime import datetime, timedelta
from typing import Tuple, Optional
from abc import ABC, abstractmethod
import database

# External Provider Configuration from Environment Variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
TWILIO_VERIFY_SERVICE_SID = os.getenv("TWILIO_VERIFY_SERVICE_SID", "").strip()

# Security Parameters
OTP_EXPIRY_MINUTES = 10
RESEND_COOLDOWN_SECONDS = 60
MAX_ATTEMPTS = 3


class BaseSMSProvider(ABC):
    """Abstract base class for SMS OTP verification providers."""

    @abstractmethod
    def is_configured(self) -> bool:
        """Returns True if required provider API credentials are configured."""
        pass

    @abstractmethod
    def send_verification(self, mobile_number: str) -> Tuple[bool, str]:
        """Dispatches an OTP verification request to the real SMS carrier."""
        pass

    @abstractmethod
    def check_verification(self, mobile_number: str, code: str) -> Tuple[bool, str]:
        """Checks the entered OTP verification code against the provider."""
        pass


class TwilioVerifyProvider(BaseSMSProvider):
    """Official Twilio Verify API integration for production SMS OTP delivery."""

    def __init__(self, account_sid: str, auth_token: str, service_sid: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.service_sid = service_sid
        self._client = None

    def is_configured(self) -> bool:
        return bool(self.account_sid and self.auth_token and self.service_sid)

    def _get_client(self):
        if self._client is None and self.is_configured():
            try:
                from twilio.rest import Client
                self._client = Client(self.account_sid, self.auth_token)
            except Exception as e:
                self._client = None
        return self._client

    def send_verification(self, mobile_number: str) -> Tuple[bool, str]:
        if not self.is_configured():
            return False, "SMS verification is not configured. Add the SMS provider credentials to enable real OTP."

        client = self._get_client()
        if not client:
            return False, "Failed to initialize SMS gateway client."

        formatted_mobile = self._format_e164(mobile_number)
        try:
            verification = client.verify.v2.services(self.service_sid).verifications.create(
                to=formatted_mobile,
                channel="sms"
            )
            if verification.status in ["pending", "approved"]:
                return True, "Verification code sent successfully via SMS."
            return False, f"SMS Gateway status: {verification.status}"
        except Exception as e:
            return False, f"SMS Gateway error: {str(e)}"

    def check_verification(self, mobile_number: str, code: str) -> Tuple[bool, str]:
        if not self.is_configured():
            return False, "SMS verification is not configured. Add the SMS provider credentials to enable real OTP."

        client = self._get_client()
        if not client:
            return False, "Failed to initialize SMS gateway client."

        formatted_mobile = self._format_e164(mobile_number)
        try:
            check = client.verify.v2.services(self.service_sid).verification_checks.create(
                to=formatted_mobile,
                code=code.strip()
            )
            if check.status == "approved":
                return True, "Mobile number verified successfully."
            return False, "Invalid or expired verification code. Please check and try again."
        except Exception as e:
            return False, f"Verification check failed: {str(e)}"

    @staticmethod
    def _format_e164(mobile_number: str) -> str:
        """Formats 10-digit Indian phone numbers to E.164 (+91XXXXXXXXXX)."""
        clean = re.sub(r"[^\d+]", "", mobile_number)
        if clean.startswith("+"):
            return clean
        if len(clean) == 10:
            return f"+91{clean}"
        if clean.startswith("91") and len(clean) == 12:
            return f"+{clean}"
        return clean


# Global provider instance
_provider = TwilioVerifyProvider(
    account_sid=TWILIO_ACCOUNT_SID,
    auth_token=TWILIO_AUTH_TOKEN,
    service_sid=TWILIO_VERIFY_SERVICE_SID
)


def get_otp_provider() -> BaseSMSProvider:
    """Returns the configured SMS OTP provider."""
    return _provider


def is_sms_configured() -> bool:
    """Checks whether the SMS verification provider is configured with credentials."""
    return _provider.is_configured()


def validate_mobile_format(mobile: str) -> bool:
    """Validates if a mobile number is a standard 10-digit Indian mobile number."""
    clean = re.sub(r"[^\d]", "", mobile)
    return len(clean) == 10 and clean[0] in "56789"


def send_otp(mobile: str, purpose: str = "signup") -> Tuple[bool, str]:
    """
    Validates cooldown, checks provider configuration, and dispatches a real SMS OTP.
    Enforces security rate limits and cooldowns in database records.
    """
    if not validate_mobile_format(mobile):
        return False, "Please enter a valid 10-digit Indian mobile number."

    clean_mobile = re.sub(r"[^\d]", "", mobile)

    # Check cooldown and rate limits in SQLite
    records = database.execute_query(
        "SELECT * FROM otp_records WHERE mobile = ? AND purpose = ? ORDER BY id DESC LIMIT 1",
        (clean_mobile, purpose)
    )

    now = datetime.now()

    if records:
        last_record = records[0]
        resend_time = datetime.fromisoformat(last_record["resend_available_at"])
        if now < resend_time:
            remaining_seconds = int((resend_time - now).total_seconds())
            return False, f"Please wait {remaining_seconds} seconds before requesting a new OTP."

    if not is_sms_configured():
        return False, "SMS verification is not configured. Add the SMS provider credentials to enable real OTP."

    # Dispatch via Real SMS Provider
    success, msg = _provider.send_verification(clean_mobile)

    if success:
        # Record in database for cooldown & rate limiting
        expires_at = (now + timedelta(minutes=OTP_EXPIRY_MINUTES)).isoformat()
        resend_available_at = (now + timedelta(seconds=RESEND_COOLDOWN_SECONDS)).isoformat()

        database.execute_insert(
            """
            INSERT INTO otp_records (mobile, purpose, attempts, max_attempts, expires_at, resend_available_at, verified)
            VALUES (?, ?, 0, ?, ?, ?, 0)
            """,
            (clean_mobile, purpose, MAX_ATTEMPTS, expires_at, resend_available_at)
        )

    return success, msg


def verify_otp(mobile: str, code: str, purpose: str = "signup") -> Tuple[bool, str]:
    """
    Validates attempt limits, expiry, and verifies the OTP through the SMS provider.
    """
    if not code or not code.strip():
        return False, "Please enter the OTP verification code."

    clean_mobile = re.sub(r"[^\d]", "", mobile)
    clean_code = code.strip()

    if not is_sms_configured():
        return False, "SMS verification is not configured. Add the SMS provider credentials to enable real OTP."

    # Check attempt limit and expiry in database
    records = database.execute_query(
        "SELECT * FROM otp_records WHERE mobile = ? AND purpose = ? ORDER BY id DESC LIMIT 1",
        (clean_mobile, purpose)
    )

    if not records:
        return False, "No active OTP request found. Please request a new verification code."

    record = records[0]
    now = datetime.now()
    expires_at = datetime.fromisoformat(record["expires_at"])

    if now > expires_at:
        return False, "The OTP has expired. Please request a new verification code."

    if record["attempts"] >= record["max_attempts"]:
        return False, "Maximum verification attempts exceeded. Please request a new OTP."

    # Increment attempt count
    database.execute_update(
        "UPDATE otp_records SET attempts = attempts + 1 WHERE id = ?",
        (record["id"],)
    )

    # Verify with external provider
    success, msg = _provider.check_verification(clean_mobile, clean_code)

    if success:
        database.execute_update(
            "UPDATE otp_records SET verified = 1 WHERE id = ?",
            (record["id"],)
        )

    return success, msg

