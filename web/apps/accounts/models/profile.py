import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


User = settings.AUTH_USER_MODEL


def user_avatar_path(instance, filename):
    # Dynamic file path generation: media/avatars/user_<uuid>/filename
    return f"avatars/user_{instance.user.id}/{filename}"

class Profile(models.Model):
    """
    The user's public face. Keeps heavy media assets and customizable metadata
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    username = models.CharField(max_length=150, unique=True, db_index=True)
    display_name = models.CharField(max_length=150, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    avatar = models.ImageField(upload_to=user_avatar_path, blank=True, null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=["username"]),
        ]

    def __str__(self):
        return self.username