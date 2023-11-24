from datetime import date
from typing import List

import pytest

from hours.controller import EntryController
from hours.model import Entry


@pytest.fixture()
def controller() -> EntryController:
    return EntryController(None)


def test_if_add_client_stores_data(controller: EntryController):
    controller.add_client("client", 100, "EUR")

    clients = controller.get_clients()
    assert len(clients) == 1
    assert clients[0].name == "client"
    assert clients[0].rate == 100
    assert clients[0].currency == "EUR"


def test_if_remove_client_deletes_data(controller: EntryController):
    controller.add_client("client", 100, "EUR")
    controller.remove_client("client")

    clients = controller.get_clients()
    assert len(clients) == 0


def test_if_log_hours_stored_data(controller: EntryController):
    client = controller.add_client("client", 100, "EUR")
    controller._add_entry(client, "project", "task1", date.fromisoformat("2021-01-01"), 8.0)
    controller._add_entry(client, "project", "task2", date.fromisoformat("2021-01-02"), 8.0)
    controller._add_entry(client, "project2", "task3", date.fromisoformat("2021-01-03"), 8.0)

    entries: List[Entry] = list(controller.get_entries())

    assert len(entries) == 3


def test_if_remove_entries_deletes_multiple_data(controller: EntryController):
    client = controller.add_client("client", 100, "EUR")
    controller._add_entry(client, "project", "task1", date.fromisoformat("2021-01-01"), 8.0)
    controller._add_entry(client, "project", "task2", date.fromisoformat("2021-01-02"), 8.0)
    controller._add_entry(client, "project2", "task3", date.fromisoformat("2021-01-03"), 8.0)

    controller.remove_entries([1, 2])

    entries = controller.get_entries()
    assert len(entries) == 1
    assert entries[0].id == 3


def test_if_remove_entries_deletes_data(controller: EntryController):
    client = controller.add_client("client", 100, "EUR")
    controller._add_entry(client, "project", "task1", date.fromisoformat("2021-01-01"), 8.0)
    controller._add_entry(client, "project", "task2", date.fromisoformat("2021-01-02"), 8.0)
    controller._add_entry(client, "project2", "task3", date.fromisoformat("2021-01-03"), 8.0)

    controller.remove_entries([1])

    entries = controller.get_entries()
    assert len(entries) == 2


def test_if_get_entries_returns_ordered_data(controller: EntryController):
    client = controller.add_client("client", 100, "EUR")
    controller._add_entry(client, "project", "task1", date.fromisoformat("2021-01-01"), 8.0)
    controller._add_entry(client, "project2", "task3", date.fromisoformat("2021-01-03"), 8.0)
    controller._add_entry(client, "project", "task2", date.fromisoformat("2021-01-02"), 8.0)

    entries: List[Entry] = list(controller.get_entries())

    assert len(entries) == 3
    dates = [entry.day for entry in entries]
    assert dates == sorted(dates)


def test_if_update_entries_modifies_data(controller: EntryController):
    client = controller.add_client("client", 100, "EUR")
    controller._add_entry(client, "project", "task1", date.fromisoformat("2021-01-01"), 8.0)
    controller._add_entry(client, "project2", "task3", date.fromisoformat("2021-01-03"), 8.0)
    controller._add_entry(client, "project", "task2", date.fromisoformat("2021-01-02"), 8.0)

    controller.update_entry(1, task="modified_task")

    entries: List[Entry] = list(controller.get_entries())

    assert len(entries) == 3
    assert entries[0].project == "project"
    assert entries[0].task == "modified_task"
    assert entries[0].day == date.fromisoformat("2021-01-01")
    assert entries[0].hours == 8.0


def test_if_can_duplicate_entry(controller: EntryController):
    client = controller.add_client("client", 100, "EUR")
    controller._add_entry(client, "project", "task1", date.fromisoformat("2021-01-01"), 8.0)

    controller.duplicate_last_entry()

    entries = list(controller.get_entries())
    first_entry = entries[0]
    last_entry = entries[-1]
    assert len(entries) == 2

    assert last_entry.client.name == first_entry.client.name
    assert last_entry.project == first_entry.project
    assert last_entry.task == first_entry.task
    assert last_entry.day == first_entry.day
    assert last_entry.hours == first_entry.hours


def test_if_can_duplicate_entry_with_override(controller: EntryController):
    client = controller.add_client("client", 100, "EUR")
    controller._add_entry(client, "project", "task1", date.fromisoformat("2021-01-01"), 8.0)

    controller.duplicate_last_entry(task_override="task2")

    entries = list(controller.get_entries())
    first_entry = entries[0]
    last_entry = entries[-1]
    assert len(entries) == 2

    assert last_entry.client.name == first_entry.client.name
    assert last_entry.project == first_entry.project
    assert last_entry.task == "task2"
    assert last_entry.day == first_entry.day
    assert last_entry.hours == first_entry.hours
