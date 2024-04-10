from sqlmodel import Field

from systema.base import BaseModel, CreatedAtMixin, UpdatedAtMixin


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserBase(BaseModel):
    username: str = Field(..., primary_key=True)
    active: bool = True
    superuser: bool = False


class User(
    UserBase,
    CreatedAtMixin,
    UpdatedAtMixin,
    table=True,
):
    hashed_password: str
