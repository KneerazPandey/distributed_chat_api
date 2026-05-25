from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class PasswordResetJWTAuthentication(JWTAuthentication):

    def get_validated_token(self, raw_token):

        token = super().get_validated_token(raw_token)

        if token.get("token_type") != "password_reset":
            raise InvalidToken("Invalid password reset token")

        return token