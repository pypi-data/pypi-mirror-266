from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, ClassVar

import sqlalchemy as sa
from nanoid import generate
from nanoid.resources import size
from pydantic import AfterValidator
from sqlmodel import Field
from sqlmodel import SQLModel as _SQLModel


class BaseModel(_SQLModel):
    __plural__: ClassVar[str | None] = None
    """Custom plural"""

    class NotFound(Exception):
        """When query returns no result"""

    @classmethod
    def get_singular_name(cls):
        return cls.__name__

    @classmethod
    def get_plural_name(cls):
        if plural := cls.__plural__:
            return plural
        return cls.get_singular_name() + "s"


def convert_to_local_timezone(dt: datetime):
    dt = (
        dt.replace(tzinfo=timezone.utc)  # to timezone-aware
        .astimezone()  # convert to local timezone
        .replace(tzinfo=None)  # to timezone-naive
    )

    return dt


LocalDatetime = Annotated[datetime, AfterValidator(convert_to_local_timezone)]


class IdMixin(_SQLModel):
    id: str = Field(
        default_factory=generate,
        primary_key=True,
        index=True,
        nullable=False,
        min_length=size,
        max_length=size,
    )


class CreatedAtMixin(_SQLModel):
    created_at: LocalDatetime | None = Field(
        default=None,
        sa_type=sa.DateTime(),
        sa_column_kwargs={"server_default": sa.func.now()},
        nullable=False,
    )


class UpdatedAtMixin(_SQLModel):
    updated_at: LocalDatetime | None = Field(
        default=None,
        sa_type=sa.DateTime(),
        sa_column_kwargs={"server_default": sa.func.now(), "onupdate": sa.func.now()},
    )


# TODO: implement soft delete
class DeletedAtMixin(_SQLModel):
    deleted_at: datetime | None = Field(default=None)
