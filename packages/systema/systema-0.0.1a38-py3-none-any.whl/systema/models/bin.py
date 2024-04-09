from datetime import datetime

from sqlmodel import Field

from systema.base import BaseModel, IdMixin


class BinBase(BaseModel):
    name: str
    order: int = Field(0, ge=0)


class BinCreate(BinBase):
    pass


class BinUpdate(BaseModel):
    name: str | None = None
    order: int | None = None


class Bin(BinBase, IdMixin, table=True):
    board_id: str = Field(..., foreign_key="board.id")
    created_at: datetime = Field(default_factory=datetime.now, index=True)


class BinRead(BinBase):
    id: str
    board_id: str
    created_at: datetime

    @classmethod
    def from_bin(cls, bin: Bin):
        return BinRead.model_validate(bin)
