from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum

from sqlmodel import Field

from systema.base import (
    BaseModel,
    CreatedAtMixin,
    UpdatedAtMixin,
)
from systema.models.task import (
    SubTaskMixin,
    TaskCreate,
    TaskRead,
    TaskUpdate,
)


class TimeUnit(str, Enum):
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"


def next_full_hour():
    dt = datetime.now() + timedelta(hours=1)
    return dt.replace(minute=0, second=0, microsecond=0)


class EventBase(BaseModel):
    reference_timestamp: datetime | None = Field(default=None, nullable=True)
    duration: int = Field(default=30)
    duration_unit: TimeUnit = Field(default=TimeUnit.MINUTES)
    all_day: bool = Field(default=False)


class EventCreate(TaskCreate, EventBase):
    pass


class EventRead(
    TaskRead,
    EventBase,
    CreatedAtMixin,
    UpdatedAtMixin,
):
    pass


class EventUpdate(TaskUpdate):
    reference_timestamp: datetime | None = None
    duration: int | None = None
    duration_unit: TimeUnit | None = None
    all_day: bool | None = None


class Event(
    SubTaskMixin,
    EventBase,
    CreatedAtMixin,
    UpdatedAtMixin,
    table=True,
):
    pass
