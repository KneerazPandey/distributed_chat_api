from dataclasses import dataclass

from core.events import BaseEvent


@dataclass(frozen=True, kw_only=True)
class ForgetPasswordEvent(BaseEvent):

    email: str
    otp: str

    event_name: str = "accounts.forget.password.event"