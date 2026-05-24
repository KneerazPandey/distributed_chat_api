from django.conf import settings

User = settings.AUTH_USER_MODEL

class UserSelector:
    @staticmethod
    def is_email_exist(email: str) -> bool:
        return User.objects.filter(email=email).exists()
    
    def get_by_email(email: str) -> User | None:
        return User.objects.filter(email=email).first()
    