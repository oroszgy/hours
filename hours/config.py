from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    db_path: Path


DEFAULT_CONFIG = Config(Path("logs.db"))
