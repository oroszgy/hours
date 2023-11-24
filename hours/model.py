from datetime import date
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Entry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    day: date = Field(index=True, nullable=False)
    hours: float = Field(nullable=False)
    project: str = Field(index=True, nullable=False)
    task: Optional[str] = Field()
    client_id: int = Field(default=None, foreign_key="client.id", nullable=False)
    client: "Client" = Relationship(back_populates="entries", sa_relationship_kwargs={"lazy": "joined"})


class Client(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False, unique=True)
    rate: float = Field(nullable=False)
    currency: str = Field(nullable=False)
    entries: List[Entry] = Relationship(back_populates="client")
