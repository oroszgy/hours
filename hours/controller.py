from datetime import date
from pathlib import Path
from typing import List, Optional, Sequence

from sqlmodel import Session, SQLModel, create_engine, select

from hours.model import Client, Entry
from hours.views import ConsoleDisplay, FileDisplay


class EntryController:
    def __init__(self, db_path: Optional[Path], debug=False):
        self._db_path: Path | None = db_path
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

    def _get_entries(
        self,
        client_name: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> Sequence[Entry]:
        client: Client = self.get_client_by_name(client_name)
        with Session(self._engine) as session:
            statement = select(Entry)
            if from_date is not None:
                statement = statement.where(Entry.day >= from_date)
            if to_date is not None:
                statement = statement.where(Entry.day < to_date)
            if client_name is not None:
                statement = statement.where(Entry.client_id == client.id)

            statement = statement.order_by(Entry.day).order_by(Entry.id)

            results = session.exec(statement)
            return results.all()

    def _add_entry(self, client: str, project: str, task: str | None, day: date, hours: float):
        with Session(self._engine) as session:
            stmt = select(Client).filter(Client.name == client)
            results = session.exec(stmt)
            client: Client = results.one()
            entry = Entry(day=day, hours=hours, project=project, task=task, client_id=client.id)
            session.add(entry)

            session.commit()

    def add_client(self, name: str, rate: float, currency: str):
        with Session(self._engine) as session:
            client = Client(name=name, rate=rate, currency=currency)
            session.add(client)

            session.commit()

    def get_client_by_id(self, id: str):
        with Session(self._engine) as session:
            statement = select(Client).filter(Client.id == id)
            results = session.exec(statement)
            return results.one()

    def get_client_by_name(self, client: str):
        with Session(self._engine) as session:
            statement = select(Client).filter(Client.name == client)
            results = session.exec(statement)
            return results.one()

    def get_clients(self) -> Sequence[Client]:
        with Session(self._engine) as session:
            statement = select(Client)
            results = session.exec(statement)
            return results.all()

    def remove_client(self, name: str):
        with Session(self._engine) as session:
            # noinspection PyUnresolvedReferences
            statement = select(Client).filter(Client.name == name)
            results = session.exec(statement)
            client = results.one()
            session.delete(client)

            session.commit()

    def update_client(self, name: str | None, rate: float | None, currenct: str | None):
        with Session(self._engine) as session:
            statement = select(Client).filter(Client.name == name)
            results = session.exec(statement)
            client: Client = results.one()
            if rate:
                client.rate = rate
            if currenct:
                client.currency = currenct

            session.commit()

    def add_entry(
        self,
        client: str | None,
        project: str | None,
        task: str | None,
        day: date | None,
        hours: float | None,
        copy: bool = False,
    ):
        if copy:
            entries = self._get_entries()
            last_entry = entries[-1]
            project = project or last_entry.project
            task = task or last_entry.task
            hours = hours or last_entry.task
            client = client or self.get_client_by_id(last_entry.client_id).name

        self._add_entry(client, project, task, day, hours)

    def display_entries(self, client: str | None, from_date: date, to_date: date, show_all: bool):
        entries: list[Entry] = list(
            self._get_entries(
                client,
                from_date if not show_all else None,
                to_date if not show_all else None,
            )
        )
        clients = []
        for entry in entries:
            client = self.get_client_by_id(entry.client_id)
            clients.append(client)

        self._console_display.show_entries(entries, clients)

    def export_entries(
        self,
        client: str,
        from_date: date,
        to_date: date,
        hourly_rate: float,
        out_path: Path,
    ):
        year_w_month_name = from_date.strftime("%Y %B")
        out_path = out_path or Path(f"{client} - {year_w_month_name}.xlsx")
        result: list[Entry] = list(self._get_entries(from_date, to_date, client))
        client: Client = self.get_client(client)
        self._console_display.show_entries(result)
        self._file_display.save_to_excel(result, client.rate, client.currency, out_path, year_w_month_name)

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
        project: str | None = None,
        task: str | None = None,
        day: date | None = None,
        hours: float | None = None,
    ):
        with Session(self._engine) as session:
            statement = select(Entry).filter(Entry.id == entry_id)
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
        clients: list[Client] = list(self.get_clients())
        self._console_display.show_clients(clients)
