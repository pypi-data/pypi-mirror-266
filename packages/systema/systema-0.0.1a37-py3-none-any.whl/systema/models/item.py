from __future__ import annotations

from sqlmodel import Field, Session

from systema.base import BaseModel
from systema.models.task import (
    SubTaskMixin,
    Task,
    TaskCreate,
    TaskRead,
    TaskUpdate,
)


class ItemBase(BaseModel):
    order: int = Field(0, ge=0)


class ItemCreate(TaskCreate):
    pass


class ItemRead(TaskRead, ItemBase):
    pass


class ItemUpdate(ItemBase, TaskUpdate):
    pass


class Item(SubTaskMixin, ItemBase, table=True):
    @classmethod
    def _create(cls, session: Session, task: Task):
        session.refresh(task)
        item = Item.model_validate(task)
        session.add(item)
        session.commit()
        session.refresh(item)

        cls._reorder(session, task.project_id, item.order, exclude=item.id, shift=True)

        session.refresh(item)
        return item
