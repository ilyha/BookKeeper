from datetime import date

from sqlmodel import Field, SQLModel


class AuthorBase(SQLModel):
    first_name: str
    last_name: str
    birth_date: date | None = None


class Author(AuthorBase, table=True):
    id: int | None = Field(default=None, nullable=False, primary_key=True)


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(SQLModel):
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None
