from datetime import date
from typing import List

import pytest

from hours.controller import Controller
from hours.model import Entry


@pytest.fixture()
def controller() -> Controller:
    return Controller(None)


def test_if_log_hours_stored_data(controller: Controller):
    controller.log_hours("project", "task1", date.fromisoformat("2021-01-01"), 8.0)
    controller.log_hours("project", "task2", date.fromisoformat("2021-01-02"), 8.0)
    controller.log_hours("project2", "task3", date.fromisoformat("2021-01-03"), 8.0)

    entries: List[Entry] = list(controller.get_entries())

    assert len(entries) == 3


def test_if_remove_entries_deletes_multiple_data(controller: Controller):
    controller.log_hours("project", "task1", date.fromisoformat("2021-01-01"), 8.0)
    controller.log_hours("project", "task2", date.fromisoformat("2021-01-02"), 8.0)
    controller.log_hours("project2", "task3", date.fromisoformat("2021-01-03"), 8.0)

    controller.remove_entries([1, 2])

    entries = controller.get_entries()
    assert len(entries) == 1
    assert entries[0].id == 3


def test_if_remove_entries_deletes_data(controller: Controller):
    controller.log_hours("project", "task1", date.fromisoformat("2021-01-01"), 8.0)
    controller.log_hours("project", "task2", date.fromisoformat("2021-01-02"), 8.0)
    controller.log_hours("project2", "task3", date.fromisoformat("2021-01-03"), 8.0)

    controller.remove_entries([1])

    entries = controller.get_entries()
    assert len(entries) == 2


def test_if_get_entries_returns_ordered_data(controller: Controller):
    controller.log_hours("project", "task1", date.fromisoformat("2021-01-01"), 8.0)
    controller.log_hours("project2", "task3", date.fromisoformat("2021-01-03"), 8.0)
    controller.log_hours("project", "task2", date.fromisoformat("2021-01-02"), 8.0)

    entries: List[Entry] = list(controller.get_entries())

    assert len(entries) == 3
    dates = [entry.day for entry in entries]
    assert dates == sorted(dates)
