import asyncio

from fastapi import FastAPI

from src.book_keeper.authors.routes import authors_router
from src.book_keeper.books.routes import books_router
from src.book_keeper.db import create_db_and_tables

app = FastAPI(openapi_url="/openapi.json")


def init() -> None:
    asyncio.run(create_db_and_tables())


app.include_router(authors_router)
app.include_router(books_router)
