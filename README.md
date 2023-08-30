### Сервис BookKeeper

#### Описание
Для работы с БД был использован инструмент [SQLModel](https://sqlmodel.tiangolo.com), 
который представляет связку ORM и Pydantic моделей.

Для первоначальной инициализации БД необходимо запустить команду 
`poetry run init_db`, или `docker-compose exec app poetry run init_db` если запускается из _docker-compose_.
Эта команда создаст необходимые таблицы.

Стандарная документация API при запуске через _docker-compose_ будет доступна по адресу http://127.0.0.1:8004/docs#