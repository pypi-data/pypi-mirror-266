from systema.models.event import Event, EventRead
from systema.proxies.task import SubTaskProxy


class EventProxy(SubTaskProxy[EventRead]):
    @property
    def base_url(self) -> str:
        return super().base_url + f"projects/{self.project_id}/events/"

    @property
    def model(self):
        return Event

    @property
    def model_read(self):
        return EventRead
