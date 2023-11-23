from datetime import datetime
from pathlib import Path
from typing import Annotated, List

import typer
import xlsxwriter
from rich.console import Console
from rich.table import Table
from typer import Typer

from hours.config import DEFAULT_CONFIG
from hours.controller import EntryController
from hours.date_utils import first_day_of_month, first_day_of_prev_month, tomorrow
from hours.model import Entry

app = Typer(name="hours", help="A minimalistic hours logger for the command line.", no_args_is_help=True)


def make_controller():
    return EntryController(DEFAULT_CONFIG.db_path)


def show_table(results: List[Entry]):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Day")
    table.add_column("Hours", justify="right")
    table.add_column("Project")
    table.add_column("Task")
    table.add_column("Description")
    for entry in results:
        table.add_row(entry.day.isoformat(), str(entry.hours), entry.project, entry.task)
    console = Console()
    console.print(table)


@app.command(no_args_is_help=True, help="Log worked hours.")
def log(
    project: Annotated[str, typer.Option("-p", "--project", help="Project name")] = None,
    task: Annotated[str, typer.Option("-t", "--task", help="Task name")] = None,
    date: Annotated[
        datetime, typer.Option("-d", "--date", help="Day (ISO format)", formats=["%Y-%m-%d"])
    ] = datetime.now()
    .date()
    .isoformat(),
    hours: Annotated[float, typer.Option("-h", "--hours", help="Task name")] = 8.0,
    copy: Annotated[
        bool,
        typer.Option(
            "-c", "--copy", help="Copy last entry for today, and overwrite values if specified", flag_value=True
        ),
    ] = False,
):
    controller = make_controller()

    if copy:
        entries = controller.get_entries()
        last_entry = entries[-1]
        project = project or last_entry.project
        task = task or last_entry.task
        hours = hours or last_entry.task

    controller.log_hours(project, task, date, hours)


@app.command(help="List work log entries", name="list")
def list_(
    from_date: Annotated[
        datetime,
        typer.Option(
            "-f", "--from", help="From day (ISO format), default: first day of the month", formats=["%Y-%m-%d"]
        ),
    ] = first_day_of_month().isoformat(),
    to_date: Annotated[
        datetime, typer.Option("-u", "--until", help="To day (ISO format), default: tomorrow", formats=["%Y-%m-%d"])
    ] = tomorrow().isoformat(),
    show_all: Annotated[bool, typer.Option("-a", "--all", help="Show all entries")] = False,
):
    controller = make_controller()
    result: list[Entry] = list(
        controller.get_entries(from_date if not show_all else None, to_date if not show_all else None)
    )
    show_table(result)


@app.command(help="Create an XLS report of the work log entries", no_args_is_help=True)
def export(
    hourly_rate: Annotated[float, typer.Option("-r", "--rate", help="Hourly rate")],
    out_path: Annotated[
        Path,
        typer.Option(
            "-o", "--out", help="Output path, the default name is the year and the " "month of the given interval"
        ),
    ] = None,
    from_date: Annotated[
        datetime, typer.Option("-s", "--since", help="Since day (ISO format)", formats=["%Y-%m-%d"])
    ] = first_day_of_prev_month().isoformat(),
    to_date: Annotated[
        datetime, typer.Option("-u", "--until", help="Until day (ISO format)", formats=["%Y-%m-%d"])
    ] = first_day_of_month().isoformat(),
):
    year_w_mont_name = from_date.strftime("%Y %B")
    out_path = Path(year_w_mont_name + ".xlsx")
    controller = make_controller()
    result: list[Entry] = list(controller.get_entries(from_date, to_date))
    show_table(result)
    with xlsxwriter.Workbook(out_path) as workbook:
        worksheet = workbook.add_worksheet(year_w_mont_name)
        bold = workbook.add_format({"bold": True})
        wrapped = workbook.add_format()
        wrapped.set_text_wrap()
        euro_format = workbook.add_format({'num_format': '€#,##0.00'})
        bold_euro_format = workbook.add_format({'num_format': '€#,##0.00', "bold": True})
        hours_format = workbook.add_format({'num_format': '0.00'})
        bold_hours_format = workbook.add_format({'num_format': '0.00', "bold": True})

        worksheet.write(0, 0, "Date", bold)
        worksheet.set_column(0, 0, 12)
        worksheet.write(0, 1, "Project", bold)
        worksheet.set_column(1, 1, 20)
        worksheet.write(0, 2, "Task", bold)
        worksheet.set_column(2, 2, 20)
        worksheet.write(0, 3, "Duration", bold)
        worksheet.set_column(3, 3, 20)
        worksheet.write(0, 4, "Amount", bold)
        worksheet.set_column(4, 4, 15)

        # worksheet.autofit()

        total_hours: float = 0.0
        total_amount: float = 0.0
        for i, entry in enumerate(result):
            worksheet.write(i + 1, 0, entry.day.isoformat())
            worksheet.write(i + 1, 1, entry.project)
            worksheet.write(i + 1, 2, entry.task)
            worksheet.write(i + 1, 3, entry.hours, hours_format)
            total_hours += entry.hours
            worksheet.write(i + 1, 4, entry.hours * hourly_rate, euro_format)
            total_amount += entry.hours * hourly_rate

        worksheet.write(i + 3, 3, "Total", bold)
        worksheet.write_formula(i + 3, 3, f"=SUM(D2:D{i + 2})", bold_hours_format, total_hours)
        worksheet.write_formula(i + 3, 4, f"=SUM(E2:E{i + 2})", bold_euro_format, total_amount)


@app.command(help="Remove a work log entries", no_args_is_help=True)
def remove(ids: List[int] = typer.Argument(help="Entry ids to remove")):
    controller = make_controller()
    controller.remove_entries(ids)


if __name__ == '__main__':
    app()
