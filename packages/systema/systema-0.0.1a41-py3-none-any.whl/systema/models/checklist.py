from systema.base import CreatedAtMixin, UpdatedAtMixin
from systema.models.project import SubProjectMixin


class Checklist(
    SubProjectMixin,
    CreatedAtMixin,
    UpdatedAtMixin,
    table=True,
):
    pass
