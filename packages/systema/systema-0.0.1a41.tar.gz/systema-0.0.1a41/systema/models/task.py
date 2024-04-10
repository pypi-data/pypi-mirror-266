from __future__ import annotations

import enum
from typing import Any

from sqlmodel import Field

from systema.base import BaseModel, CreatedAtMixin, IdMixin, UpdatedAtMixin


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


class Task(
    TaskBase,
    IdMixin,
    CreatedAtMixin,
    UpdatedAtMixin,
    table=True,
):
    project_id: str = Field(..., foreign_key="project.id")


class TaskCreate(TaskBase):
    pass


class TaskRead(
    TaskBase,
    TaskReadMixin,
    CreatedAtMixin,
    UpdatedAtMixin,
):
    id: str
    status: Status

    def is_done(self):
        return self.status == Status.DONE


class TaskUpdate(BaseModel):
    name: str | None = None
    status: Status | None = None
