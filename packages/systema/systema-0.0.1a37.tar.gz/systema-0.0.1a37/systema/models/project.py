from __future__ import annotations

from datetime import datetime

from sqlmodel import Field

from systema.base import BaseModel, IdMixin
from systema.models.mode import Mode


class SubProjectMixin(BaseModel):
    id: str = Field(..., foreign_key="project.id", primary_key=True)


class ProjectBase(BaseModel):
    name: str
    mode: Mode | None = Field(None)


class Project(ProjectBase, IdMixin, table=True):
    created_at: datetime = Field(default_factory=datetime.now, index=True)


class ProjectCreate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: str
    created_at: datetime


class ProjectUpdate(BaseModel):
    name: str | None = None
    mode: Mode | None = None
