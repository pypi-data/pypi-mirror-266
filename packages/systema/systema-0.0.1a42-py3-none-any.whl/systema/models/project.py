from __future__ import annotations

from sqlmodel import Field

from systema.base import BaseModel, CreatedAtMixin, IdMixin, UpdatedAtMixin
from systema.models.mode import Mode


class SubProjectMixin(BaseModel):
    id: str = Field(..., foreign_key="project.id", primary_key=True)


class ProjectBase(BaseModel):
    name: str
    mode: Mode | None = None


class Project(
    ProjectBase,
    IdMixin,
    CreatedAtMixin,
    UpdatedAtMixin,
    table=True,
):
    pass


class ProjectCreate(ProjectBase):
    pass


class ProjectRead(
    ProjectBase,
    CreatedAtMixin,
    UpdatedAtMixin,
):
    id: str


class ProjectUpdate(BaseModel):
    name: str | None = None
    mode: Mode | None = None
