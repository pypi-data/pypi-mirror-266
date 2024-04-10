from systema.base import CreatedAtMixin, UpdatedAtMixin
from systema.models.project import SubProjectMixin


class Calendar(
    SubProjectMixin,
    CreatedAtMixin,
    UpdatedAtMixin,
    table=True,
):
    pass
