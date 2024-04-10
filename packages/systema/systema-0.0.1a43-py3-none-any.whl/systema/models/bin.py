from sqlmodel import Field

from systema.base import BaseModel, CreatedAtMixin, IdMixin, UpdatedAtMixin


class BinBase(BaseModel):
    name: str
    order: int = Field(0, ge=0)


class BinCreate(BinBase):
    pass


class BinUpdate(BaseModel):
    name: str | None = None
    order: int | None = None


class Bin(
    BinBase,
    IdMixin,
    CreatedAtMixin,
    UpdatedAtMixin,
    table=True,
):
    board_id: str = Field(..., foreign_key="board.id")


class BinRead(
    BinBase,
    CreatedAtMixin,
    UpdatedAtMixin,
):
    id: str
    board_id: str

    @classmethod
    def from_bin(cls, bin: Bin):
        return BinRead.model_validate(bin)
