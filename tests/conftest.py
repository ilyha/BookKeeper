import random
from collections.abc import AsyncGenerator
from datetime import date
from unittest.mock import patch

import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine, text
from sqlmodel.ext.asyncio.session import AsyncSession

import src.book_keeper.db
from src.book_keeper import app as main_app
from src.book_keeper.authors.models import Author
from src.book_keeper.books.models import Book
from src.book_keeper.config import settings


@pytest.fixture
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    db_name = f"test_{random.getrandbits(32)}"
    async with src.book_keeper.db.engine.connect() as conn:
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        await conn.execute(text(f"CREATE DATABASE {db_name}"))

    base_url, _ = settings.db.url.rsplit("/", 1)
    engine = AsyncEngine(create_engine(f"{base_url}/{db_name}", echo=settings.debug))
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine
    await engine.dispose()
    async with src.book_keeper.db.engine.connect() as conn:
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        await conn.execute(text(f"DROP DATABASE {db_name}"))


@pytest.fixture
async def session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
async def app(engine: AsyncEngine) -> AsyncGenerator[AsyncClient, None]:
    async with LifespanManager(main_app):
        with patch("src.book_keeper.db.engine", engine):
            async with AsyncClient(app=main_app, base_url="http://test") as client:
                yield client


@pytest.fixture
async def author(session: AsyncSession) -> Author:
    db_author = Author(
        first_name="Name",
        last_name="LastName",
        birth_date=date(2000, 10, 10),
    )
    session.add(db_author)
    await session.commit()
    await session.refresh(db_author)
    return db_author


@pytest.fixture
async def book(session: AsyncSession, author: Author) -> Book:
    db_book = Book(
        name="Book",
        description="description",
        publishing_date=date(2020, 10, 10),
        author_id=author.id,
    )
    session.add(db_book)
    await session.commit()
    await session.refresh(db_book)
    return db_book
