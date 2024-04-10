from __future__ import annotations

from sqlmodel import Field

from systema.base import BaseModel, CreatedAtMixin, UpdatedAtMixin
from systema.models.task import (
    SubTaskMixin,
    TaskCreate,
    TaskRead,
    TaskUpdate,
)


class CardBase(BaseModel):
    order: int = Field(0, ge=0)
    bin_id: str | None = Field(None, foreign_key="bin.id", nullable=True)


class CardCreate(TaskCreate):
    bin_id: str | None = None


class CardRead(
    TaskRead,
    CardBase,
    CreatedAtMixin,
    UpdatedAtMixin,
):
    pass


class CardUpdate(CardBase, TaskUpdate):
    pass


class Card(
    SubTaskMixin,
    CardBase,
    CreatedAtMixin,
    UpdatedAtMixin,
    table=True,
):
    pass
