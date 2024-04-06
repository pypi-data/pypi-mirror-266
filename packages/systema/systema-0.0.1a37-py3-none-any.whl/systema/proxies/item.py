from typing import Literal

from sqlmodel import Session, col, select

from systema.models.item import (
    Item,
    ItemRead,
)
from systema.models.project import Project
from systema.models.task import Status, Task
from systema.proxies.task import SubTaskProxy


class ItemProxy(SubTaskProxy[ItemRead]):
    def __init__(self, project_id: str):
        self.project_id = project_id

    @property
    def base_url(self) -> str:
        return super().base_url + f"projects/{self.project_id}/items/"

    @property
    def model(self):
        return Item

    @property
    def model_read(self):
        return ItemRead

    def move(self, id: str, up_or_down: Literal["up", "down"]):
        if self.is_set_as_server():
            with Session(self.engine) as session:
                project = self.get_project(session)
                item, task = self.get_task(session, project, id)

                original_order = item.order

                if up_or_down == "up":
                    item.order = max(0, item.order - 1)
                elif up_or_down == "down":
                    statement = select(Item).order_by(col(Item.order).desc())
                    max_item = session.exec(statement).first()
                    max_order = max_item.order if max_item else 0
                    if item.order >= max_order:
                        return ItemRead.from_task(item, task)

                    item.order += 1
                else:
                    raise ValueError()

                session.add(item)
                session.commit()
                session.refresh(item)

                self._reorder(
                    session,
                    project.id,
                    original_order,
                    exclude=item.id,
                    shift=False,
                )
                self._reorder(
                    session,
                    project.id,
                    item.order,
                    exclude=item.id,
                    shift=True,
                )

                session.add(item)
                session.commit()
                session.refresh(item)
                session.refresh(task)
                return ItemRead.from_task(item, task)

        response = self.client.post(f"{self.base_url}{id}/{up_or_down}")
        response.raise_for_status()
        return ItemRead(**response.json())

    def toggle(self, id: str):
        if self.is_set_as_server():
            with Session(self.engine) as session:
                project = self.get_project(session)
                item, task = self.get_task(session, project, id)

                if task.status == Status.DONE:
                    task.status = Status.NOT_STARTED
                    original_order = 0
                else:
                    task.status = Status.DONE
                    original_order = item.order
                    item.order = 0

                session.add_all((task, item))
                session.commit()

                session.refresh(item)
                session.refresh(task)

                self._reorder(
                    session, project.id, original_order, item.id, original_order == 0
                )

                session.refresh(item)
                session.refresh(task)

                return ItemRead.from_task(item, task)
        response = self.client.post(f"{self.base_url}{id}/toggle")
        response.raise_for_status()
        return ItemRead(**response.json())

    def _reorder(
        self,
        session: Session,
        project_id: str,
        order: int,
        exclude: str,
        shift: bool = True,
    ):
        statement = (
            select(Item)
            .join(Task)
            .where(
                Task.id == Item.id,
                Task.project_id == project_id,
                Item.order >= order,
                Task.status != Status.DONE,
                Item.id != exclude,
            )
            .order_by(col(Item.order).asc())
        )
        items = session.exec(statement).all()
        for i, item in enumerate(items):
            item.order = order + i
            if shift:
                item.order += 1
            session.add(item)
        session.commit()

    def post_update(
        self,
        session: Session,
        project: Project,
        original_obj: Item,
        current_obj: Item,
    ):
        original_order = original_obj.order

        if original_order != current_obj.order:
            self._reorder(
                session,
                project.id,
                original_order,
                exclude=current_obj.id,
                shift=False,
            )
            self._reorder(
                session,
                project.id,
                current_obj.order,
                exclude=current_obj.id,
                shift=True,
            )
        session.refresh(current_obj)
        return current_obj

    def pre_delete(
        self,
        session: Session,
        project: Project,
        original_obj: Item,
    ):
        self._reorder(
            session, project.id, original_obj.order, original_obj.id, shift=False
        )
        return True
