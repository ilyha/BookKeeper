FROM python:3.11-slim

COPY poetry.lock /app/poetry.lock
COPY pyproject.toml /app/pyproject.toml
WORKDIR /app

RUN apt update && apt upgrade -y && \
    pip install -U pip && \
    pip install poetry && \
    poetry install --without dev && \
    poetry cache clear --all -n pypi && \
    apt autoremove -y &&  \
    apt clean -y && \
    find / -name "*.pyc" -or -name "*.whl" -delete

ADD . .

CMD ["poetry", "run", "uvicorn", "src.book_keeper:app", "--host", "0.0.0.0"]
