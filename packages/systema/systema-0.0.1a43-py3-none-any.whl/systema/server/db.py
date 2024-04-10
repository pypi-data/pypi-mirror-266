from sqlmodel import SQLModel, create_engine

from systema.management import Settings
from systema.models import get_all_db_models


def create_db_and_tables():
    get_all_db_models()

    engine = create_engine(Settings().db_address)
    SQLModel.metadata.create_all(engine)


def show_tables():
    print(SQLModel.metadata.tables)
