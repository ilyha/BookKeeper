import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine

from src.book_keeper.authors.models import Author
from src.book_keeper.books.models import Book


async def test_list_empty(app: AsyncClient) -> None:
    response = await app.get("/books")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == []


async def test_list(app: AsyncClient, book: Book) -> None:
    response = await app.get("/books")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == [
        {
            "author": {
                "birth_date": "2000-10-10",
                "first_name": "Name",
                "id": 1,
                "last_name": "LastName",
            },
            "author_id": 1,
            "description": "description",
            "name": "Book",
            "publishing_date": "2020-10-10",
        }
    ]


@pytest.mark.parametrize(("author_id", "results_count"), [(1, 1), (2, 0)])
async def test_list_by_author(
    app: AsyncClient, book: Book, author_id: int, results_count: int
) -> None:
    response = await app.get("/books", params={"author_ids": [author_id]})
    assert response.status_code == 200, response.text
    assert len(response.json()) == results_count


async def test_create(app: AsyncClient, engine: AsyncEngine, author: Author) -> None:
    response = await app.post(
        "/books",
        json={
            "name": "Name",
            "description": "description",
            "publishing_date": "1990-10-10",
            "author_id": author.id,
        },
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data == {
        "author_id": 1,
        "description": "description",
        "id": 1,
        "name": "Name",
        "publishing_date": "1990-10-10",
    }


async def test_get(app: AsyncClient, engine: AsyncEngine, book: Author) -> None:
    response = await app.get(f"/books/{book.id}")
    assert response.status_code == 200, response.text
    assert response.json() == {
        "author_id": 1,
        "description": "description",
        "id": 1,
        "name": "Book",
        "publishing_date": "2020-10-10",
    }


async def test_update(app: AsyncClient, book: Author) -> None:
    response = await app.patch(
        f"/books/{book.id}", json={"description": "New description"}
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        "author_id": 1,
        "description": "New description",
        "id": 1,
        "name": "Book",
        "publishing_date": "2020-10-10",
    }


async def test_delete(app: AsyncClient, book: Author) -> None:
    response = await app.delete(f"/books/{book.id}")
    assert response.status_code == 204, response.text

    response = await app.get(f"/books/{book.id}")
    assert response.status_code == 404, response.text
