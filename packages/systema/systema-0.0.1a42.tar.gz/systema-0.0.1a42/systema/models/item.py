from __future__ import annotations

from sqlmodel import Field

from systema.base import BaseModel, CreatedAtMixin, UpdatedAtMixin
from systema.models.task import (
    SubTaskMixin,
    TaskCreate,
    TaskRead,
    TaskUpdate,
)


class ItemBase(BaseModel):
    order: int = Field(0, ge=0)


class ItemCreate(TaskCreate):
    pass


class ItemRead(
    TaskRead,
    ItemBase,
    CreatedAtMixin,
    UpdatedAtMixin,
):
    pass


class ItemUpdate(ItemBase, TaskUpdate):
    pass


class Item(
    SubTaskMixin,
    ItemBase,
    CreatedAtMixin,
    UpdatedAtMixin,
    table=True,
):
    pass
