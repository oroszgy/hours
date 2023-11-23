from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel


class Entry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    day: date = Field(index=True)
    hours: float = Field()
    project: str = Field(index=True)
    task: Optional[str] = Field()
