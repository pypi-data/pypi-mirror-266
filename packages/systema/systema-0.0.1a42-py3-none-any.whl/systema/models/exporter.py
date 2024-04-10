from abc import ABC, abstractmethod
from pathlib import Path

from sqlmodel import Session, create_engine, select

from systema.management import Settings
from systema.models import get_all_db_models, get_model_by_name


class Exporter(ABC):
    def iter_instances(self):
        engine = create_engine(Settings().db_address)
        with Session(engine) as session:
            for model in get_all_db_models():
                for ins in session.exec(select(model)):
                    yield ins

    @property
    def file(self):
        file = Path(Settings().base_path / self.get_filename())
        file.touch(exist_ok=True)
        return file

    @abstractmethod
    def get_filename(self) -> str:
        pass

    @abstractmethod
    def dump(self):
        pass

    @abstractmethod
    def load(self):
        pass


class JSON(Exporter):
    def get_filename(self) -> str:
        return "data.json"

    def dump(self):
        import json

        data = [
            {"type": i.__class__.__name__, **i.model_dump(mode="json")}
            for i in self.iter_instances()
        ]

        with open(self.file, mode="w") as fp:
            json.dump(data, fp)

    def load(self):
        import json

        with open(self.file, mode="r") as fp:
            data: list[dict] = json.load(fp)

        engine = create_engine(Settings().db_address)
        with Session(engine) as session:
            for d in data:
                t = d.pop("type")
                model_type = get_model_by_name(t)
                inst = model_type.model_validate(d)
                session.add(inst)
            session.commit()
