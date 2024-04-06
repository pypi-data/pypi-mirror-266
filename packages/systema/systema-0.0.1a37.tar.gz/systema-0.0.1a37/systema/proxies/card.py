from typing import Any, Literal

from sqlmodel import Session, col, select

from systema.models.bin import Bin
from systema.models.card import Card, CardRead
from systema.models.project import Project
from systema.models.task import Task
from systema.proxies.task import SubTaskProxy


class CardProxy(SubTaskProxy[CardRead]):
    def __init__(self, board_id: str):
        self.board_id = board_id
        self.project_id = board_id

    @property
    def base_url(self) -> str:
        return super().base_url + f"projects/{self.board_id}/cards/"

    @property
    def model(self):
        return Card

    @property
    def model_read(self):
        return CardRead

    def _reorder(
        self,
        session: Session,
        project_id: str,
        bin_id: str | None,
        order: int,
        exclude: str,
        shift: bool = True,
    ):
        statement = (
            select(Card)
            .join(Task)
            .where(
                Task.id == Card.id,
                Task.project_id == project_id,
                Card.bin_id == bin_id,
                Card.order >= order,
                Card.id != exclude,
            )
            .order_by(col(Card.order).asc())
        )
        cards = session.exec(statement).all()
        for i, item in enumerate(cards):
            item.order = order + i
            if shift:
                item.order += 1
            session.add(item)
        session.commit()

    def _move_x(
        self,
        session: Session,
        card: Any,
        project: Project,
        direction: Literal["left"] | Literal["right"],
    ):
        if not isinstance(card, Card):
            raise ValueError
        current_bin = session.exec(select(Bin).where(Bin.id == card.bin_id)).first()

        if direction == "left":
            target_order = (current_bin.order - 1) if current_bin else 0
        elif direction == "right":
            target_order = (current_bin.order + 1) if current_bin else 0
        else:
            raise ValueError

        if target_order == -1:
            card.bin_id = None
            card.order = 0
            return

        target_bin = session.exec(
            select(Bin).where(
                Bin.board_id == project.id,
                Bin.order == target_order,
            )
        ).first()

        if target_bin is None:
            return

        card.bin_id = target_bin.id
        card.order = 0

        self._reorder(
            session,
            project.id,
            card.bin_id,
            card.order,
            exclude=card.id,
            shift=True,
        )

    def move(self, id: str, direction: Literal["up", "down", "left", "right"]):
        if self.is_set_as_server():
            with Session(self.engine) as session:
                project = self.get_project(session)
                card, task = self.get_task(session, project, id)

                original_card = card.model_copy()

                if direction == "up":
                    card.order = max(0, card.order - 1)
                elif direction == "down":
                    statement = (
                        select(Card)
                        .join(Task)
                        .where(
                            Card.bin_id == card.bin_id,
                            Card.id == Task.id,
                            Task.project_id == project.id,
                        )
                        .order_by(col(Card.order).desc())
                    )
                    max_card = session.exec(statement).first()
                    max_order = max_card.order if max_card else 0

                    if card.order >= max_order:
                        return CardRead.from_task(card, task)

                    card.order += 1
                elif direction in ("left", "right"):
                    self._move_x(session, card, project, direction)
                else:
                    raise ValueError()

                session.add(card)
                session.commit()
                session.refresh(card)

                self._reorder(
                    session,
                    project.id,
                    original_card.bin_id,
                    original_card.order,
                    exclude=card.id,
                    shift=False,
                )
                self._reorder(
                    session,
                    project.id,
                    card.bin_id,
                    card.order,
                    exclude=card.id,
                    shift=True,
                )

                session.add_all((card, task))
                session.commit()
                session.refresh(card)
                session.refresh(task)
                return CardRead.from_task(card, task)

        response = self.client.post(f"{self.base_url}{id}/move/{direction}")
        response.raise_for_status()
        return CardRead(**response.json())
