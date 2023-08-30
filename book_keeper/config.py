from pathlib import Path

from dynaconf import Dynaconf

root_path = Path(__file__).parent.parent

settings = Dynaconf(
    environments=True,
    env="testing",
    envvar_prefix="BOOK_KEEPER",
    settings_files=[root_path / "settings.toml", root_path / "environment.toml"],
    merge_enabled=True,
)
