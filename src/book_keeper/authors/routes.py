from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from src.book_keeper.authors.models import Author, AuthorCreate, AuthorUpdate
from src.book_keeper.books.models import Book
from src.book_keeper.db import get_session

authors_router = APIRouter(prefix="/authors", tags=["Authors"])


@authors_router.post("", response_model=Author, status_code=status.HTTP_201_CREATED)
async def create_author(
    *, session: Annotated[AsyncSession, Depends(get_session)], author_in: AuthorCreate
) -> Author:
    db_author = Author(**author_in.dict())
    session.add(db_author)
    await session.commit()
    await session.refresh(db_author)
    return db_author


@authors_router.get("", response_model=list[Author])
async def read_authors(
    *,
    session: Annotated[AsyncSession, Depends(get_session)],
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
) -> list[Author]:
    result = await session.execute(select(Author).offset(offset).limit(limit))
    return result.scalars().all()


@authors_router.get("/{author_id}", response_model=Author)
async def get_author(
    *, session: Annotated[AsyncSession, Depends(get_session)], author_id: int
) -> Author:
    db_author = await session.get(Author, author_id)
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")
    return db_author


@authors_router.patch("/{author_id}", response_model=Author)
async def update_author(
    *,
    session: Annotated[AsyncSession, Depends(get_session)],
    author_id: int,
    author_in: AuthorUpdate,
) -> Author:
    db_author = await session.get(Author, author_id)
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")
    author_data = author_in.dict(exclude_unset=True)
    for key, value in author_data.items():
        setattr(db_author, key, value)
    session.add(db_author)
    await session.commit()
    await session.refresh(db_author)
    return db_author


@authors_router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(
    *, session: Annotated[AsyncSession, Depends(get_session)], author_id: int
) -> None:
    db_author = await session.get(Author, author_id)
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")

    db_book = (
        (await session.execute(select(Book).where(Book.author_id == author_id)))
        .scalars()
        .first()
    )
    if db_book:
        raise HTTPException(
            status_code=403, detail="Can't delete author with exists books"
        )
    await session.delete(db_author)
    await session.commit()
