from typing import Optional
from dataclasses import dataclass

from core.events import BaseEvent


@dataclass(frozen=True, kw_only=True)
class UserRegisteredEvent(BaseEvent):

    username: Optional[str]
    email: str
    otp: str

    event_name: str = "accounts.user.registered.event"