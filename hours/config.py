from dataclasses import dataclass
from pathlib import Path

import typer

APP_DIR: Path = Path(typer.get_app_dir("hours"))


@dataclass
class Config:
    db_path: Path = APP_DIR / "logs.db"


DEFAULT_CONFIG = Config()
