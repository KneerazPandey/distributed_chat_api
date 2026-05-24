import uuid
from dataclasses import dataclass, field
from datetime import datetime, UTC


@dataclass(frozen=True, kw_only=True)
class BaseEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    event_name: str = "base.event"