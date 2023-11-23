from datetime import date
from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine


class Entry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    day: date = Field(index=True, nullable=False)
    hours: float = Field(nullable=False)
    project: str = Field(index=True, nullable=False)
    task: Optional[str] = Field()
    client_id: int = Field(default=None, foreign_key="client.id", nullable=False)


class Client(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False, unique=True)
    rate: float = Field(nullable=False)
    currency: str = Field(nullable=False)


if __name__ == '__main__':
    engine = create_engine("sqlite:///logs.db", echo=True)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        client = Client(name="test", rate=100, currency="EUR")
        session.add(client)
        session.commit()
        entry = Entry(day=date.today(), hours=8, project="test", client_id=client.id)
        session.add(entry)
        session.commit()
        print(entry)
        print(client)
