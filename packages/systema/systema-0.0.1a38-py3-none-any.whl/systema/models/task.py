from __future__ import annotations

import enum
from datetime import datetime
from typing import Any

from sqlmodel import Field, Session

from systema.base import BaseModel, IdMixin


class SubTaskMixin(BaseModel):
    id: str = Field(..., foreign_key="task.id", primary_key=True)


class TaskReadMixin(BaseModel):
    @classmethod
    def from_task(cls, obj: Any, task: Task):
        return cls.model_validate(obj, update=task.model_dump())


class Status(enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskBase(BaseModel):
    name: str
    status: Status = Status.NOT_STARTED


class Task(TaskBase, IdMixin, table=True):
    created_at: datetime = Field(default_factory=datetime.now, index=True)
    project_id: str = Field(..., foreign_key="project.id")

    @classmethod
    def create_subclass_instances(cls, session: Session, task: Task):
        from systema.models.card import Card
        from systema.models.item import Item

        item = Item._create(session, task)
        card = Card._create(session, task)
        return (item, card)


class TaskCreate(TaskBase):
    pass


class TaskRead(TaskBase, TaskReadMixin):
    id: str
    created_at: datetime
    status: Status

    def is_done(self):
        return self.status == Status.DONE


class TaskUpdate(BaseModel):
    name: str | None = None
    status: Status | None = None
