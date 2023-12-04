from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional, Sequence

from sqlmodel import Session, SQLModel, create_engine, select

from hours.model import Client, Entry
from hours.views import ConsoleDisplay, FileDisplay


class EntryController:
    def __init__(self, db_path: Optional[Path], debug=False):
        self._db_path: Optional[Path] = db_path
        self._engine = create_engine(
            f"sqlite:///{self._db_path.resolve() if self._db_path else ':memory:'}",
            echo=debug,
        )
        self._create_model_if_not_exists()

        self._console_display = ConsoleDisplay()
        self._file_display = FileDisplay()

    def _create_model_if_not_exists(self):
        if self._db_path is not None and self._db_path.exists():
            return

        SQLModel.metadata.create_all(self._engine)

    def get_entries(
        self,
        client_name: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> Sequence[Entry]:
        with Session(self._engine) as session:
            statement = select(Entry)
            if from_date is not None:
                # Workaround for SqlModel bug: it generates a wrong SQL query
                from_date = from_date - timedelta(microseconds=1)
                statement = statement.where(Entry.day >= from_date)
            if to_date is not None:
                statement = statement.where(Entry.day < to_date)
            if client_name is not None:
                client: Client = self.get_client_by_name(client_name)
                statement = statement.where(Entry.client_id == client.id)

            statement = statement.order_by(Entry.day).order_by(Entry.id)

            results = session.exec(statement)
            return results.all()

    def add_entry(self, client: str, project: str, task: Optional[str], day: date, hours: float) -> Entry:
        client = self.get_client_by_name(client)
        return self._add_entry(client, project, task, day, hours)

    def _add_entry(self, client: Client, project: str, task: Optional[str], day: date, hours: float) -> Entry:
        with Session(self._engine) as session:
            entry = Entry(day=day, hours=hours, project=project, task=task, client=client)
            session.add(entry)

            session.commit()

            return entry

    def add_client(self, name: str, rate: float, currency: str) -> Client:
        with Session(self._engine) as session:
            client = Client(name=name, rate=rate, currency=currency)
            session.add(client)

            session.commit()

            return client

    def get_client_by_name(self, client: str):
        with Session(self._engine) as session:
            statement = select(Client).where(Client.name == client)
            results = session.exec(statement)
            return results.one()

    def get_clients(self) -> Sequence[Client]:
        with Session(self._engine) as session:
            statement = select(Client)
            results = session.exec(statement)
            return results.all()

    def remove_client(self, name: str) -> None:
        with Session(self._engine) as session:
            # noinspection PyUnresolvedReferences
            statement = select(Client).where(Client.name == name)
            results = session.exec(statement)
            client = results.one()
            session.delete(client)

            session.commit()

    def update_client(self, name: str, rate: Optional[float], currency: Optional[str]) -> Client:
        with Session(self._engine) as session:
            client = self.get_client_by_name(name)
            if rate:
                client.rate = rate
            if currency:
                client.currency = currency

            session.commit()

            return client

    def duplicate_last_entry(
        self,
        client_override: Optional[str] = None,
        project_override: Optional[str] = None,
        task_override: Optional[str] = None,
        day_override: Optional[date] = None,
        hours_override: Optional[float] = None,
    ) -> Entry:
        entries = self.get_entries()
        last_entry: Entry = entries[-1]

        if client_override is not None:
            client = self.get_client_by_name(client_override)
        else:
            client = last_entry.client
        project_override = project_override or last_entry.project
        task_override = task_override or last_entry.task
        day_override = day_override or last_entry.day
        hours = hours_override or last_entry.hours

        return self._add_entry(client, project_override, task_override, day_override, hours)

    def display_entries(self, client: Optional[str], from_date: date, to_date: date, show_all: bool):
        entries: List[Entry] = list(
            self.get_entries(
                client,
                from_date if not show_all else None,
                to_date if not show_all else None,
            )
        )

        self._console_display.show_entries(entries)

    def export_entries(
        self,
        client: str,
        from_date: date,
        to_date: date,
        out_path: Path,
    ):
        year_w_month_name = from_date.strftime("%Y %B")
        out_path = out_path or Path(f"{client} - {year_w_month_name}.xlsx")
        result: List[Entry] = list(self.get_entries(client, from_date, to_date))

        self._console_display.show_entries(result)
        self._file_display.save_to_excel(result, out_path, year_w_month_name)

    def remove_entries(self, ids: List[int]):
        with Session(self._engine) as session:
            # noinspection PyUnresolvedReferences
            statement = select(Entry).filter(Entry.id.in_(ids))
            results = session.exec(statement)
            entries = results.all()
            for e in entries:
                session.delete(e)

            session.commit()

    def update_entry(
        self,
        entry_id: int,
        project: Optional[str] = None,
        task: Optional[str] = None,
        day: Optional[date] = None,
        hours: Optional[float] = None,
    ):
        with Session(self._engine) as session:
            statement = select(Entry).where(Entry.id == entry_id)
            results = session.exec(statement)
            entry: Entry = results.one()
            if project:
                entry.project = project
            if task:
                entry.task = task
            if day:
                entry.day = day
            if hours:
                entry.hours = hours

            session.commit()

    def display_clients(self):
        clients: List[Client] = list(self.get_clients())
        self._console_display.show_clients(clients)
