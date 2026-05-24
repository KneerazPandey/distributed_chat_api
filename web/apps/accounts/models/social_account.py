import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


User = settings.AUTH_USER_MODEL



class SocialAccount(models.Model):
    """
    The plug-and-play provider matrix. This table allows to add Google, 
    Facebook, Apple, or passkeys later without modifying the User model.
    """
    class ProviderTypes(models.TextChoices):
        GOOGLE = "google", "Google"
        FACEBOOK = "facebook", "Facebook"
        APPLE = "apple", "Apple"
        LOCAL = "local", "Password"  # For tracking standard logins

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="social_accounts")
    
    # E.g., "google", "facebook"
    provider = models.CharField(max_length=50, choices=ProviderTypes.choices)
    
    # The unique ID returned by Google/Facebook OAuth (e.g., 'sub' or 'id')
    provider_user_id = models.CharField(max_length=255, db_index=True)
    
    # Stores raw payload metadata securely from the provider for audit trails
    extra_data = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # A user cannot link the exact same Google account twice
        unique_together = ("provider", "provider_user_id")
        indexes = [
            models.Index(fields=["provider", "provider_user_id"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.provider}"

