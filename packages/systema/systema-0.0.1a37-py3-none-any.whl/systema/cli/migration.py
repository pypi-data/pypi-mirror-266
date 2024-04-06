from sqlmodel import Session, create_engine, select

from systema.management import Settings
from systema.models.board import Board
from systema.models.card import Card
from systema.models.checklist import Checklist
from systema.models.item import Item
from systema.models.project import Project, SubProjectMixin
from systema.models.task import SubTaskMixin, Task

CoreModels = Project | Task
SubModels = SubProjectMixin | SubTaskMixin

SUBMODELS: dict[type[CoreModels], tuple[type[SubModels], ...]] = {
    Project: (
        Checklist,
        Board,
    ),
    Task: (Item, Card),
}


def create_submodels():
    engine = create_engine(Settings().db_address)
    with Session(engine) as session:
        for core_model, submodels in SUBMODELS.items():
            print(f"Iterating through {core_model.__name__}")
            for core_instance in session.exec(select(core_model)).all():
                for submodel in submodels:
                    if not session.get(submodel, core_instance.id):
                        print(
                            f"Instance of {submodel.__name__} not found for id={core_instance.id}"
                        )
                        session.add(submodel(id=core_instance.id))
                        session.commit()
