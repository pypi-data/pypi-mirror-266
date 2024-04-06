from sqlmodel import Session, select

from systema.models.mode import Mode
from systema.models.project import (
    Project,
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
)
from systema.proxies.base import Proxy


class ProjectProxy(Proxy[ProjectRead]):
    @property
    def base_url(self) -> str:
        return super().base_url + "projects/"

    def get(self, id: str):
        if self.is_set_as_server():
            with Session(self.engine) as session:
                return ProjectRead.model_validate(session.get(Project, id))
        response = self.client.get(f"{self.base_url}{id}/")
        response.raise_for_status()
        return ProjectRead(**response.json())

    def all(self):
        if self.is_set_as_server():
            with Session(self.engine) as session:
                statement = select(Project)
                return (
                    ProjectRead.model_validate(row)
                    for row in session.exec(statement).all()
                )
        response = self.client.get(self.base_url)
        response.raise_for_status()
        return (ProjectRead(**p) for p in response.json())

    def create(self, data: ProjectCreate):
        if self.is_set_as_server():
            from systema.models.board import Board
            from systema.models.checklist import Checklist

            project = Project.model_validate(data)
            with Session(self.engine) as session:
                session.add(project)
                session.commit()
                session.refresh(project)

                list_ = Checklist(id=project.id)
                board = Board(id=project.id)

                session.add_all((list_, board))
                session.commit()

                session.refresh(board)
                board.create_default_bins(session)

                session.refresh(project)
                return ProjectRead.model_validate(project)
        response = self.client.post(self.base_url, json=data.model_dump(mode="json"))
        response.raise_for_status()
        return ProjectRead(**response.json())

    def update(self, id: str, data: ProjectUpdate):
        if self.is_set_as_server():
            with Session(self.engine) as session:
                if db_project := session.get(Project, id):
                    db_project.sqlmodel_update(data.model_dump(exclude_unset=True))
                    session.add(db_project)
                    session.commit()

                    session.refresh(db_project)
                    return ProjectRead.model_validate(db_project)

                raise Project.NotFound()
        response = self.client.patch(
            f"{self.base_url}{id}/",
            json=data.model_dump(mode="json", exclude_none=True),
        )
        response.raise_for_status()
        return ProjectRead(**response.json())

    def delete(self, id: str):
        if self.is_set_as_server():
            from systema.models.board import Board
            from systema.models.checklist import Checklist

            with Session(self.engine) as session:
                if project := session.get(Project, id):
                    session.delete(project)
                    if list_ := session.get(Checklist, id):
                        session.delete(list_)
                    if board := session.get(Board, id):
                        session.delete(board)
                    session.commit()
                    return

                raise Project.NotFound()
        response = self.client.delete(f"{self.base_url}{id}/")
        response.raise_for_status()

    def save_mode(self, id: str, mode: Mode):
        return self.update(id, ProjectUpdate(mode=mode))
