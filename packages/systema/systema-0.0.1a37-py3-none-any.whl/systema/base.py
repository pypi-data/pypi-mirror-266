from __future__ import annotations

from typing import ClassVar

from nanoid import generate
from nanoid.resources import size
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


class IdMixin(_SQLModel):
    id: str = Field(
        default_factory=generate,
        primary_key=True,
        index=True,
        nullable=False,
        min_length=size,
        max_length=size,
    )
