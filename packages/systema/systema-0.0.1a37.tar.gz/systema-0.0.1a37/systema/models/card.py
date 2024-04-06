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


class CardBase(BaseModel):
    order: int = Field(0, ge=0)
    bin_id: str | None = Field(None, foreign_key="bin.id", nullable=True)


class CardCreate(TaskCreate):
    pass


class CardRead(TaskRead, CardBase):
    pass


class CardUpdate(CardBase, TaskUpdate):
    pass


class Card(SubTaskMixin, CardBase, table=True):
    @classmethod
    def _create(cls, session: Session, task: Task):
        session.refresh(task)
        card = Card.model_validate(task)
        session.add(card)
        session.commit()
        session.refresh(card)

        cls._reorder(
            session,
            task.project_id,
            card.bin_id,
            card.order,
            exclude=card.id,
            shift=True,
        )

        session.refresh(card)
        return card
