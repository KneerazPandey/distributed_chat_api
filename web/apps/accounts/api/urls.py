from django.urls import path
from apps.accounts.api.views import (
    UserRegistrationAPIView, VerifyRegistrationOTPAPIView, UserLoginAPIView,
    ChangePasswordAPIView, ForgetPasswordAPIView, VerifyForgetPasswordOTPAPIView,
    ResetPasswordAPIView
)



urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='register'),

    path('login/', UserLoginAPIView.as_view(), name='login'),

    path('verify-register-otp/', VerifyRegistrationOTPAPIView.as_view(), name='verify_register_otp'),

    path('change-password/', ChangePasswordAPIView.as_view(), name='change_password'),

    path('forget-password/', ForgetPasswordAPIView.as_view(), name='forget_password'),

    path('verify-forget-password-otp/', VerifyForgetPasswordOTPAPIView.as_view(), name='verify_forget_password_otp'),

    path('reset-password/', ResetPasswordAPIView.as_view(), name='reset_password'),
]