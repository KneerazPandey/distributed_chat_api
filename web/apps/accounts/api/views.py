from rest_framework.request import Request
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import GenericAPIView

from apps.accounts.api.serializers import (
    UserRegistrationSerializer, VerifyRegistrationOTPSerializer, UserLoginSerializer,
    LoginResponseSerializer, ChangePasswordSerializer, UserSerializer, 
    ForgotPasswordSerializer, VerifyForgetPasswordOTPSerializer, 
    ResetPasswordSerializer, GoogleAuthSerializer
)
from apps.accounts.authentication import PasswordResetJWTAuthentication
from apps.accounts.services import AuthService, GoogleAuthService
from core.responses import ApiResponse



class UserRegistrationAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def post(self, request: Request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        _, otp = AuthService.register(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )

        return ApiResponse.success(
            message="Otp has been sent to your email address.",
            data={
                "email": serializer.validated_data['email'],
                "otp": otp
            },
            status_code=status.HTTP_201_CREATED
        )
        


class VerifyRegistrationOTPAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyRegistrationOTPSerializer

    def post(self, request: Request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        _ = AuthService.verify_registration_otp(
            email=serializer.validated_data['email'],
            otp=serializer.validated_data['otp']
        )

        return ApiResponse.success(
            message="Email verified successfully.",
            data={
                "email": serializer.validated_data['email'],
            },
            status_code=status.HTTP_200_OK
        )
    


class UserLoginAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request: Request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        login_result = AuthService.login(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )

        login_response_serializer = LoginResponseSerializer(login_result)

        return ApiResponse.success(
            message="Login Successfull.",
            data=login_response_serializer.data,
            status_code=status.HTTP_200_OK
        )


class ChangePasswordAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request: Request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = AuthService.change_password(
            user=request.user,
            old_password=serializer.validated_data['old_password'],
            new_password=serializer.validated_data['new_password']
        )

        
        return ApiResponse.success(
            message="Password changed successfully",
            data=UserSerializer(user).data,
            status_code=status.HTTP_200_OK
        )



class ForgetPasswordAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ForgotPasswordSerializer

    def post(self, request: Request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp = AuthService.forget_password(
            email=serializer.validated_data['email']
        )

        return ApiResponse.success(
            message="Otp has been sent to your email address.",
            data={
                "email": serializer.validated_data['email'],
                "otp": otp
            },
            status_code=status.HTTP_201_CREATED
        )
    

class VerifyForgetPasswordOTPAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyForgetPasswordOTPSerializer

    def post(self, request: Request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        password_reset_token = AuthService.verify_forget_password_otp(
            email=serializer.validated_data['email'],
            otp=serializer.validated_data['otp']
        )

        return ApiResponse.success(
            message="Otp verified successfully.",
            data={
                "email": serializer.validated_data['email'],
                'password_reset_token': password_reset_token,
            },
            status_code=status.HTTP_200_OK
        )
    


class ResetPasswordAPIView(GenericAPIView):
    authentication_classes = [PasswordResetJWTAuthentication]
    serializer_class = ResetPasswordSerializer

    def post(self, request: Request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = request.auth

        _ = AuthService.reset_password(
            token=token,
            password=serializer.validated_data['new_password']
        )
        
        return ApiResponse.success(
            message="Password Reset Successfully. Please login with new credentials.",
            data=None,
            status_code=status.HTTP_200_OK
        )



class GoogleAuthAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = GoogleAuthSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["id_token"]
        google_data = GoogleAuthService.verify_google_token(token)

        if not google_data:
            return ApiResponse.error(
                message="Invalid Google Token",
                errors={},
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        try:
            login_result = GoogleAuthService.login_or_register(google_data)
            return ApiResponse.success(
                message="Successfully authenticated with google",
                data=LoginResponseSerializer(login_result).data,
                status_code=status.HTTP_200_OK
            )

        except ValueError as e:
            return ApiResponse.error(
                message=str(e),
                errors={},
                status_code=status.HTTP_400_BAD_REQUEST
            )