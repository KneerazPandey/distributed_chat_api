from typing import Union
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.selectors import UserSelector
from apps.accounts.api.dtos import LoginResult
from apps.accounts.events import UserRegisteredEvent
from core.utils.random_generator import RandomGenerator
from core.events import EventDispatcher
from core.exceptions import (
    EmailAlreadyExistsError, RegistrationOtpCacheExpiredOrInvalidError, OtpAttemptExceedError,
    InvalidOtpError
)


User = settings.AUTH_USER_MODEL


class AuthService:
    @staticmethod
    def register(email: str, password: str, **kwargs) -> Union[User, str]:
        email = email.strip().lower()
        if UserSelector.is_email_exist(email=email):
            raise EmailAlreadyExistsError()
        
        cache_key = f'auth:register:{email}'
        otp = RandomGenerator.generate_otp()
        data = {
            'email': email,
            'otp': otp,
        }
        cache.set(
            cache_key,
            data,
            timeout=300
        )

        user = User.objects.create_user(
            email=email,
            password=password,
            **kwargs,
        )

        event = UserRegisteredEvent(
            email=email,
            otp=otp,
        )
        EventDispatcher.dispatch(event)

        return user, otp
    

    @staticmethod
    def verify_registration_otp(email: str, otp: str) -> User:
        email = email.lower().strip()
        cache_key = f'auth:register:{email}'
        data = cache.get(cache_key)

        if not data:
            raise RegistrationOtpCacheExpiredOrInvalidError()
        
        attempts = data.get('attempts', 0)
        if attempts > 3:
            cache.delete(cache_key)
            raise OtpAttemptExceedError()

        if data["otp"] != otp:
            data["attempts"] = data.get("attempts", 1) + 1
            cache.set(cache_key, data, timeout=300)
            raise InvalidOtpError()
        

        user = UserSelector.get_by_email(email=email)
        user.update(is_active=True)

        cache.delete(cache_key)

        return user 
    
    @staticmethod
    def login(email: str, password: str) -> LoginResult:
        email = email.strip().lower()
        user = authenticate(email=email, password=password)

        if not user:
            raise ValueError("Invalid credentials")

        refresh = RefreshToken.for_user(user)

        return LoginResult(
            user=user,
            access=str(refresh.access_token),
            refresh=str(refresh)
        )