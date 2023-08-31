from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine

from src.book_keeper.authors.models import Author


async def test_list(app: AsyncClient) -> None:
    response = await app.get("/authors")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == []


async def test_create(app: AsyncClient, engine: AsyncEngine) -> None:
    response = await app.post(
        "/authors",
        json={"first_name": "str", "last_name": "str", "birth_date": "1990-10-10"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data == {
        "birth_date": "1990-10-10",
        "first_name": "str",
        "id": 1,
        "last_name": "str",
    }


async def test_get(app: AsyncClient, engine: AsyncEngine, author: Author) -> None:
    response = await app.get(f"/authors/{author.id}")
    assert response.status_code == 200, response.text
    assert response.json() == {
        "birth_date": "2000-10-10",
        "first_name": "Name",
        "id": 1,
        "last_name": "LastName",
    }


async def test_update(app: AsyncClient, author: Author) -> None:
    response = await app.patch(f"/authors/{author.id}", json={"first_name": "Name2"})
    assert response.status_code == 200, response.text
    assert response.json() == {
        "birth_date": "2000-10-10",
        "first_name": "Name2",
        "id": 1,
        "last_name": "LastName",
    }


async def test_delete(app: AsyncClient, author: Author) -> None:
    response = await app.delete(f"/authors/{author.id}")
    assert response.status_code == 204, response.text

    response = await app.get(f"/authors/{author.id}")
    assert response.status_code == 404, response.text
