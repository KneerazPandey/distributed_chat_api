from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class DistributedChatManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        PATHWAY 1: Standard Credentials Registration (Email + Password)
        Accounts start as INACTIVE until OTP verification.
        """
        if not email:
            raise ValueError(_("The Email field must be set"))
        
        email = self.normalize_email(email)
        existing_user = self.filter(email=email).first()
        
        if existing_user:
            if existing_user.is_active:
                raise ValidationError(_("An active account with this email already exists."))
            
            # Trapped User Edge Case: Update password if provided on retry
            if password:
                existing_user.set_password(password)
            
            for attr, value in extra_fields.items():
                setattr(existing_user, attr, value)
                
            existing_user.save(using=self._db)
            return existing_user, True  # (user, is_retry)
            
        # Brand New Local User
        extra_fields.setdefault("is_active", False)  # Must verify via OTP
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()  # Protects account from blank password bypasses
            
        user.save(using=self._db)
        return user, False # (user, is_retry)
    
    def create_superuser(self, email, password=None, **extra_fields):
        if not password:
            raise ValueError('Superuser must have password')
        
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise TypeError('Superuser must have is_staff=True')
        if extra_fields.get('is_active') is not True:
            raise TypeError('Superuser must have is_active=True')
        if extra_fields.get('is_superuser') is not True:
            raise TypeError('Superuser must have is_superuser=True')
        if extra_fields.get('is_verified') is not True:
            raise TypeError('Superuser must have is_verified=True')
        
        return self.create_user(email=email, password=password, **extra_fields)

    def create_social_user(self, email, provider, provider_user_id, extra_data=None, **extra_fields):
        """
        PATHWAY 2: Plug-and-Play Social Registration (OAuth)
        Accounts are TRUSTED and activated IMMEDIATELY because the provider verified the email.
        """
        if not email:
            raise ValueError(_("Social authentication requires an email address."))
            
        email = self.normalize_email(email)
        extra_data = extra_data or {}
        
        # 1. Fetch or provision the core User object
        user = self.filter(email=email).first()
        is_new_user = False
        
        if user:
            # If the user was previously trapped in an inactive OTP signup state,
            # completing a social login overrides it and activates them instantly!
            if not user.is_active:
                user.is_active = True
                user.save(using=self._db)
        else:
            # Brand new identity across the entire system
            user = self.model(email=email, is_active=True, **extra_fields)
            user.set_unusable_password()  # Safe: Can only log in via verified OAuth tokens
            user.save(using=self._db)
            is_new_user = True
            
        # 2. Prevent duplicate provider links, then attach the SocialAccount record
        social_account, created = user.social_accounts.get_or_create(
            provider=provider,
            provider_user_id=provider_user_id,
            defaults={"extra_data": extra_data}
        )
        
        return user, is_new_user