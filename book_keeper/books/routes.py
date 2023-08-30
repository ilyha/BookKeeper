from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from book_keeper.authors.models import Author
from book_keeper.books.models import Book, BookCreate, BookReadWithAuthor, BookUpdate
from book_keeper.db import get_session

books_router = APIRouter(prefix="/books", tags=["Books"])


@books_router.post("", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(
    *, session: Annotated[AsyncSession, Depends(get_session)], book: BookCreate
) -> Book:
    db_author = await session.get(Author, book.author_id)
    if not db_author:
        raise HTTPException(status_code=422, detail="Author not found")
    db_book = Book.from_orm(book)
    session.add(db_book)
    await session.commit()
    await session.refresh(db_book)
    return db_book


@books_router.get("", response_model=list[BookReadWithAuthor])
async def read_books(
    *,
    session: Annotated[AsyncSession, Depends(get_session)],
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    author_ids: Annotated[list[int] | None, Query()] = None,
) -> list[BookReadWithAuthor]:
    if author_ids:
        statement = (
            select(Book, Author)
            .where(Book.author_id.in_(author_ids))  # type: ignore[union-attr]
            .join(Author, isouter=True)
        )
    else:
        statement = select(Book, Author).join(Author, isouter=True)

    result = await session.execute(statement.offset(offset).limit(limit))
    return [
        BookReadWithAuthor(**book.dict(), author=author)
        for book, author in result.all()
    ]


@books_router.get("/{book_id}", response_model=Book)
async def read_book(
    *, session: Annotated[AsyncSession, Depends(get_session)], book_id: int
) -> Book:
    db_book = await session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@books_router.patch("/{book_id}", response_model=BookReadWithAuthor)
async def update_book(
    *,
    session: Annotated[AsyncSession, Depends(get_session)],
    book_id: int,
    book: BookUpdate,
) -> Book:
    db_book = await session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book.author_id:
        db_author = await session.get(Author, book.author_id)
        if not db_author:
            raise HTTPException(status_code=422, detail="Author not found")

    book_data = book.dict(exclude_unset=True)
    for key, value in book_data.items():
        setattr(db_book, key, value)
    session.add(db_book)
    await session.commit()
    await session.refresh(db_book)
    return db_book


@books_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    *, session: Annotated[AsyncSession, Depends(get_session)], book_id: int
) -> None:
    db_book = await session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    await session.delete(db_book)
    await session.commit()
