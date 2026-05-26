from google.auth.transport import requests
from google.oauth2 import id_token
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import SocialAccount, User
from apps.accounts.selectors import SocialAccountSelector, UserSelector
from apps.accounts.api.dtos import LoginResult


class GoogleAuthService:

    @staticmethod
    def verify_google_token(token: str):
        try:
            data = id_token.verify_oauth2_token(
                id_token=token,
                requests=requests.Request(),
                audience=settings.GOOGLE_CLIENT_ID
            )
            return data 
        except Exception as e:
            print(f"GOOGLE VERIFICATION ERROR: {e}") 
            return None
        
    
    @staticmethod
    def login_or_register(data) -> LoginResult:
        email = data.get("email")
        google_id = data.get("sub")  # unique google user id

        if not email:
            raise ValueError("Google account has no email")
        if not google_id:
            raise ValueError('No any credentials details obtained from google.')

        email = email.lower().strip()

        # 1. Check if social account exists
        social = SocialAccountSelector.get_provider(
            provider_id=google_id,
            provider_name="google"
        )

        if social:
            user = social.user

        else:
            # 2. Check if user exists with same email
            user = UserSelector.get_by_email(email=email)

            if not user:
                user = User.objects.create(
                    email=email,
                    is_active=True
                )

            # 3. Link social account
            SocialAccount.objects.create(
                user=user,
                provider="google",
                provider_user_id=google_id,
                extra_data=data
            )

        # 4. Generate JWT
        refresh = RefreshToken.for_user(user)

        login_result = LoginResult(
            user=user,
            access=str(refresh.access_token),
            refresh=str(refresh)
        )

        return login_result