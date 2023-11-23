from datetime import date
from pathlib import Path
from typing import List, Optional, Sequence

from sqlmodel import Session, SQLModel, create_engine, select

from hours.model import Entry


class Controller:
    def __init__(self, db_path: Optional[Path]):
        self._db_path: Path | None = db_path
        self._engine = create_engine(f"sqlite://{self._db_path.resolve() if self._db_path else ''}", echo=True)
        self._create_model_if_not_exists()

    def _create_model_if_not_exists(self):
        if self._db_path is not None and self._db_path.exists():
            return

        SQLModel.metadata.create_all(self._engine)

    def get_entries(self, from_date: date | None = None, to_date: date | None = None) -> Sequence[Entry]:
        with Session(self._engine) as session:
            statement = select(Entry)
            if from_date is not None:
                statement = statement.where(Entry.day >= from_date)
            if to_date is not None:
                statement = statement.where(Entry.day < to_date)

            statement = statement.order_by(Entry.day).order_by(Entry.id)

            results = session.exec(statement)
            return results.all()

    def log_hours(self, project: str, task: str | None, day: date, hours: float):
        with Session(self._engine) as session:
            entry = Entry(day=day, hours=hours, project=project, task=task)
            session.add(entry)

            session.commit()

    def remove_entries(self, ids: List[int]):
        with Session(self._engine) as session:
            # noinspection PyUnresolvedReferences
            statement = select(Entry).filter(Entry.id.in_(ids))
            results = session.exec(statement)
            entries = results.all()
            for e in entries:
                session.delete(e)

            session.commit()
