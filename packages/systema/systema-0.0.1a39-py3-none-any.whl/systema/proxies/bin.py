from typing import Literal

from sqlmodel import Session, col, select

from systema.models.bin import Bin, BinCreate, BinRead, BinUpdate
from systema.proxies.base import Proxy


class BinProxy(Proxy[BinRead]):
    def __init__(self, board_id: str):
        self.board_id = board_id

    @property
    def base_url(self) -> str:
        return super().base_url + f"projects/{self.board_id}/bins/"

    def _reorder(
        self,
        session: Session,
        board_id: str,
        order: int,
        exclude: str,
        shift: bool = True,
    ):
        statement = (
            select(Bin)
            .where(
                Bin.board_id == board_id,
                Bin.order >= order,
                Bin.id != exclude,
            )
            .order_by(col(Bin.order).asc())
        )
        bins = session.exec(statement).all()
        for i, bin in enumerate(bins):
            bin.order = order + i
            if shift:
                bin.order += 1
            session.add(bin)
        session.commit()

    def _get(self, session: Session, board_id: str, id: str):
        statement = select(Bin).where(Bin.id == id, Bin.board_id == board_id)
        if result := session.exec(statement).first():
            return result
        raise Bin.NotFound()

    def _get_board(self, session: Session, board_id: str):
        from systema.models.board import Board

        if board := session.get(Board, board_id):
            return board
        raise Board.NotFound

    def get(self, id: str):
        if self.is_set_as_server():
            with Session(self.engine) as session:
                return BinRead.from_bin(self._get(session, self.board_id, id))

        response = self.client.get(f"{self.base_url}{id}")
        response.raise_for_status()
        return BinRead(**response.json())

    def all(self):
        if self.is_set_as_server():
            with Session(self.engine) as session:
                board = self._get_board(session, self.board_id)
                statement = (
                    select(Bin)
                    .where(
                        Bin.board_id == board.id,
                    )
                    .order_by(
                        col(Bin.order).asc(),
                    )
                )
                return (BinRead.from_bin(row) for row in session.exec(statement).all())

        response = self.client.get(self.base_url)
        response.raise_for_status()
        return (BinRead(**p) for p in response.json())

    def create(self, data: BinCreate):
        if self.is_set_as_server():
            with Session(self.engine) as session:
                project = self._get_board(session, self.board_id)
                bin = Bin(name=data.name, board_id=project.id, order=data.order)
                session.add(bin)
                session.commit()
                session.refresh(bin)
                self._reorder(
                    session, bin.board_id, bin.order, exclude=bin.id, shift=True
                )
                session.refresh(bin)
                return BinRead.from_bin(bin)

        response = self.client.post(self.base_url, json=data.model_dump(mode="json"))
        response.raise_for_status()
        return BinRead(**response.json())

    def update(self, id: str, data: BinUpdate):
        if self.is_set_as_server():
            with Session(self.engine) as session:
                board = self._get_board(session, self.board_id)
                bin = self._get(session, self.board_id, id)

                original_order = bin.order

                bin.sqlmodel_update(data.model_dump(exclude_unset=True))

                session.add(bin)
                session.commit()

                session.refresh(bin)

                if original_order != bin.order:
                    self._reorder(
                        session,
                        board.id,
                        original_order,
                        exclude=bin.id,
                        shift=False,
                    )
                    self._reorder(
                        session,
                        board.id,
                        bin.order,
                        exclude=bin.id,
                        shift=True,
                    )

                session.refresh(bin)

                return BinRead.from_bin(bin)

        response = self.client.patch(
            f"{self.base_url}{id}/",
            json=data.model_dump(mode="json", exclude_none=True),
        )
        response.raise_for_status()
        return BinRead(**response.json())

    def delete(self, id: str):
        if self.is_set_as_server():
            with Session(self.engine) as session:
                board = self._get_board(session, self.board_id)
                bin = self._get(session, board.id, id)

                self._reorder(session, self.board_id, bin.order, bin.id, shift=False)

                session.delete(bin)

                session.commit()
        else:
            response = self.client.delete(f"{self.base_url}{id}/")
            response.raise_for_status()

    def move(self, id: str, direction: Literal["left", "right"]):
        if self.is_set_as_server():
            with Session(self.engine) as session:
                project = self._get_board(session, self.board_id)
                bin = self._get(session, self.board_id, id)

                original_order = bin.order

                if direction == "left":
                    bin.order = max(0, bin.order - 1)
                elif direction == "right":
                    statement = (
                        select(Bin)
                        .where(Bin.board_id == self.board_id)
                        .order_by(col(Bin.order).desc())
                    )
                    max_bin = session.exec(statement).first()
                    max_order = max_bin.order if max_bin else 0
                    if bin.order >= max_order:
                        return BinRead.from_bin(bin)

                    bin.order += 1
                else:
                    raise ValueError()

                session.add(bin)
                session.commit()
                session.refresh(bin)

                self._reorder(
                    session,
                    project.id,
                    original_order,
                    exclude=bin.id,
                    shift=False,
                )
                self._reorder(
                    session,
                    project.id,
                    bin.order,
                    exclude=bin.id,
                    shift=True,
                )

                session.add(bin)
                session.commit()
                session.refresh(bin)
                return BinRead.from_bin(bin)

        response = self.client.post(
            f"{self.base_url}{id}/move/{direction}",
        )
        response.raise_for_status()
        return BinRead(**response.json())
