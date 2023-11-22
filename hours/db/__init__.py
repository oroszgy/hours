import datetime
import sqlite3
from importlib.resources import files
from pathlib import Path
from typing import List


class Database:
    def __init__(self, db_path: Path):
        self._db_path = db_path

    def __enter__(self):
        if not self._db_path.exists():
            self._create_schema()
            self._add_indices()

        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()

    def _create_schema(self):
        conn = sqlite3.connect(self._db_path, check_same_thread=False)
        create_stmts: str = (files("hours.db") / "build_schema.sql").read_text()
        conn.executescript(create_stmts)
        conn.commit()
        conn.close()

    def _add_indices(self):
        create_stmts: str = (files("hours.db") / "create_indices.sql").read_text()
        self._conn.executescript(create_stmts)
        self._conn.commit()

    def log_hours(self, project: str, task: str, description: str | None, day: datetime.date, hours: float) -> None:
        cursor = self._conn.cursor()
        cursor.execute(
            "INSERT INTO entry (id, day, hours, project, task, description) VALUES(?, ?, ?, ?, ?, ?)",
            [
                None,
                day,
                hours,
                project,
                task,
                description
            ]
        )
        self._conn.commit()

    def remove_hours(self, ids: List[int]) -> None:
        cursor = self._conn.cursor()
        cursor.executemany(
            "DELETE FROM entry WHERE id = ?",
            [
                (id,) for id in ids
            ]
        )
        self._conn.commit()

    def get_hours(self, from_date: datetime.datetime | None = None, to_date: datetime.datetime | None = None) -> list[
        tuple]:
        from_date = from_date or 0
        to_date = to_date or datetime.datetime.now()
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT * FROM entry WHERE day >= ? AND day < ? ORDER BY id ASC",
            [
                from_date, to_date
            ]
        )
        return cursor.fetchall()
