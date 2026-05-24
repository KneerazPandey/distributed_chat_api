from dataclasses import dataclass
from apps.accounts.models import User


@dataclass
class LoginResult:
    user: User
    access: str
    refresh: str