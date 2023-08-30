from datetime import date

from sqlmodel import Field, SQLModel

from src.book_keeper.authors.models import Author


class BookBase(SQLModel):
    name: str
    description: str | None = None
    publishing_date: date
    author_id: int | None = Field(default=None, foreign_key="author.id")


class Book(BookBase, table=True):
    id: int | None = Field(default=None, nullable=False, primary_key=True)


class BookCreate(BookBase):
    pass


class BookUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    publishing_date: date | None = None
    author_id: int | None = None


class BookReadWithAuthor(BookBase):
    author: Author
