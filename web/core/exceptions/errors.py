from .base import ApplicationError
from rest_framework import status


class EmailAlreadyExistsError(ApplicationError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "User with this email already exists"
    default_code = "email_already_exists"


class InvalidOtpError(ApplicationError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid OTP"
    default_code = "invalid_otp"


class CacheError(ApplicationError):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Unable to retrive cache data"
    default_code = "cache_not_found"


class RegistrationOtpCacheExpiredOrInvalidError(ApplicationError):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Registration Otp Invalid or expired."
    default_code = "invalid_or_expired_cache"


class OtpAttemptExceedError(ApplicationError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = "All 3 attempt failed. Please enter details again to get new otp."
    default_code = "too_many_requests"
