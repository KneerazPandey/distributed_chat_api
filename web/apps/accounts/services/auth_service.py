from typing import Union
from django.core.cache import cache
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed

from apps.accounts.selectors import UserSelector
from apps.accounts.api.dtos import LoginResult
from apps.accounts.events import UserRegisteredEvent, ForgetPasswordEvent
from apps.accounts.models import User
from core.utils.random_generator import RandomGenerator
from core.tokens import PasswordResetToken
from core.events import EventDispatcher
from core.exceptions import (
    EmailAlreadyExistsError, OtpAttemptExceedError,
    InvalidOtpError, InvalidPasswordError, InvalidEmailError
)


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
            raise InvalidOtpError()
        
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
    
    @staticmethod
    def change_password(user: User, old_password: str, new_password) -> User:
        if not user.check_password(old_password):
            raise InvalidPasswordError()
        
        # Django password validation
        validate_password(new_password, user)

        user.set_password(new_password)
        user.save()

        return user
    
    @staticmethod
    def forget_password(email: str) -> str:
        email = email.strip().lower()
        if not UserSelector.is_email_exist(email=email):
            raise InvalidEmailError()
        
        cache_key = f'auth:forget_password:{email}'
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

        event = ForgetPasswordEvent(email=email, otp=otp)
        EventDispatcher.dispatch(event)

        return otp
    

    @staticmethod
    def verify_forget_password_otp(email: str, otp: str) -> str:
        email = email.lower().strip()
        cache_key = f'auth:forget_password:{email}'
        data = cache.get(cache_key)

        if not data:
            raise InvalidOtpError()
        
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

        token = PasswordResetToken.for_user(user)
        token["purpose"] = "password_reset"

        cache.delete(cache_key)

        return str(token)
    

    @staticmethod
    def reset_password(token: any, password: str) -> User:
        if not token:
            raise AuthenticationFailed("Missing token")
        
        if token.get("token_type") != "password_reset":
            raise AuthenticationFailed("Invalid token type")
        
        user_id = token.get("user_id")
        user = UserSelector.get_by_id(user_id)

        if not user:
            raise AuthenticationFailed("User not found")
        
        user.set_password(password)
        user.save()

        return user 
