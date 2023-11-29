from datetime import datetime
from pathlib import Path
from typing import Annotated, List

import typer
from typer import Typer

from hours.config import APP_DIR, DEFAULT_CONFIG
from hours.controller import EntryController
from hours.date_utils import first_day_of_month, first_day_of_prev_month, tomorrow

app = Typer(
    name="hours",
    help="A minimalistic work time logger for the command line.",
    no_args_is_help=True,
)

if not APP_DIR.exists():
    APP_DIR.mkdir(parents=True, exist_ok=True)

controller = EntryController(DEFAULT_CONFIG.db_path)


@app.command(no_args_is_help=True, help="Log worked hours.")
def log(
    client: Annotated[str, typer.Option("-c", "--client", help="Client name")] = None,
    project: Annotated[str, typer.Option("-p", "--project", help="Project name")] = None,
    task: Annotated[str, typer.Option("-t", "--task", help="Task name")] = None,
    date: Annotated[
        datetime,
        typer.Option("-d", "--date", help="Day (ISO format)", formats=["%Y-%m-%d"]),
    ] = datetime.now()
    .date()
    .isoformat(),
    hours: Annotated[float, typer.Option("-h", "--hours", help="Task name")] = 8.0,
    duplicate: Annotated[
        bool,
        typer.Option(
            "-l",
            "--duplicate-last",
            help="Duplicate last entry for today, and overwrite values if specified",
            flag_value=True,
        ),
    ] = False,
):
    if duplicate:
        controller.duplicate_last_entry(client, project, task, date, hours)
    else:
        if client is None or project is None or task is None or hours is None:
            typer.echo("You need to specify all the arguments if you are not duplicating the last entry.")
            raise typer.Exit(1)
        else:
            controller.add_entry(client, project, task, date, hours)


@app.command(no_args_is_help=True, help="Log worked hours.")
def update(
    entry_id: Annotated[int, typer.Option("-i", "--id", help="Entry id")],
    project: Annotated[str, typer.Option("-p", "--project", help="Project name")] = None,
    task: Annotated[str, typer.Option("-t", "--task", help="Task name")] = None,
    date: Annotated[
        datetime,
        typer.Option("-d", "--date", help="Day (ISO format)", formats=["%Y-%m-%d"]),
    ] = None,
    hours: Annotated[float, typer.Option("-h", "--hours", help="Task name")] = None,
):
    if project is None and task is None and date is None and hours is None:
        typer.echo("You need to specify at least one argument to update.")
        raise typer.Exit(1)

    controller.update_entry(entry_id, project, task, date, hours)


@app.command(help="List work log entries")
def report(
    client: Annotated[str, typer.Option("-c", "--client", help="Client name")] = None,
    from_date: Annotated[
        datetime,
        typer.Option(
            "-f",
            "--from",
            help="From day (ISO format), default: first day of the month",
            formats=["%Y-%m-%d"],
        ),
    ] = first_day_of_month().isoformat(),
    to_date: Annotated[
        datetime,
        typer.Option(
            "-t",
            "--to",
            help="To day (ISO format), default: tomorrow",
            formats=["%Y-%m-%d"],
        ),
    ] = tomorrow().isoformat(),
    show_all: Annotated[bool, typer.Option("-a", "--all", help="Show all entries")] = False,
):
    controller.display_entries(client, from_date, to_date, show_all)


@app.command(help="Create an XLS report of the work log entries", no_args_is_help=True)
def export(
    client: Annotated[str, typer.Option("-c", "--client", help="Client name")],
    out_path: Annotated[
        Path,
        typer.Option(
            "-o",
            "--out",
            help="Output path, the default name is the year and the " "month of the given interval",
        ),
    ] = None,
    from_date: Annotated[
        datetime,
        typer.Option(
            "-f",
            "--from",
            help="From day (ISO format), default: first day of the previous month",
            formats=["%Y-%m-%d"],
        ),
    ] = first_day_of_prev_month().isoformat(),
    to_date: Annotated[
        datetime,
        typer.Option(
            "-t",
            "--to",
            help="To day (ISO format), default: first day of the actual month",
            formats=["%Y-%m-%d"],
        ),
    ] = first_day_of_month().isoformat(),
):
    controller.export_entries(client, from_date, to_date, out_path)


@app.command(help="Remove a work log entries", no_args_is_help=True)
def remove(ids: List[int] = typer.Argument(help="Entry ids to remove")):
    controller.remove_entries(ids)


clients_app = Typer(no_args_is_help=True, help="Manage clients")
app.add_typer(clients_app, name="clients")


@clients_app.command(help="Add a client", no_args_is_help=True, name="add")
def add_client(
    name: Annotated[str, typer.Option("-n", "--name", help="Client name")],
    rate: Annotated[float, typer.Option("-r", "--rate", help="Hourly rate")],
    currency: Annotated[str, typer.Option("-c", "--currency", help="Currency")],
):
    controller.add_client(name, rate, currency)


@clients_app.command(help="Update a client", no_args_is_help=True, name="update")
def update_client(
    name: Annotated[str, typer.Option("-n", "--name", help="Client name")],
    rate: Annotated[float, typer.Option("-r", "--rate", help="Hourly rate")] = None,
    currency: Annotated[str, typer.Option("-c", "--currency", help="Currency")] = None,
):
    if rate is None and currency is None:
        typer.echo("You need to specify at least one argument to update.")
        raise typer.Exit(1)
    controller.update_client(name, rate, currency)


@clients_app.command(help="Remove a client", no_args_is_help=True, name="remove")
def remove_client(
    name: Annotated[str, typer.Option("-n", "--name", help="Client name")],
):
    controller.remove_client(name)


@clients_app.command(help="List clients", name="list")
def list_clients():
    controller.display_clients()


if __name__ == "__main__":
    app()
