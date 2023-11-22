from datetime import datetime
from pathlib import Path
from typing import Annotated, Tuple, List

import typer
import xlsxwriter
from rich.console import Console
from rich.table import Table
from typer import Typer

from date_utils import first_day_of_month, first_day_of_prev_month, tomorrow
from hours.db import Database

app = Typer(
    name="hours",
    help="A minimalistic hours logger for the command line.",
    no_args_is_help=True
)


def show_table(result: List[Tuple[int, str, float, str, str, str]]):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", justify="right")
    table.add_column("Day")
    table.add_column("Hours", justify="right")
    table.add_column("Project")
    table.add_column("Task")
    table.add_column("Description")
    for row in result:
        table.add_row(
            str(row[0]),
            row[1].split(" ")[0],
            str(row[2]),
            row[3],
            row[4],
            row[5]
        )
    console = Console()
    console.print(table)


@app.command(no_args_is_help=True, help="Log worked hours.")
def log(
        project: Annotated[
            str, typer.Option("-p", "--project",
                              help="Project name, the default is to grab the last one logged.")] = None,
        task: Annotated[str, typer.Option("-t", "--task",
                                          help="Task name, the default is to grab the last one logged.")] = None,
        description: Annotated[str, typer.Option("-s", "--description",
                                                 help="Task description")] = "",
        date: Annotated[datetime, typer.Option(
            "-d", "--date",
            help="Day (ISO format)",
            formats=["%Y-%m-%d"])] = datetime.now().date().isoformat(),
        hours: Annotated[float, typer.Option
            ("-h", "--hours",
             help="Task name")] = 8.0,
        copy: Annotated[bool, typer.Option(
            "-c", "--copy",
            help="Copy last entry for today, and overwrite values if specified",
            flag_value=True)] = False

):
    with Database(Path("logs.db")) as db:
        _, _, hours_, project_, task_, description_ = db.get_hours()[-1]
        project = project or project_
        task = task or task_
        if copy:
            description = description or description_
            hours = hours or hours_

        db.log_hours(project, task, description, date, hours)

        db.get_hours()


@app.command(help="List work log entries")
def list(
        from_date: Annotated[
            datetime, typer.Option("-f", "--from",
                                   help="From day (ISO format), default: first day of the month",
                                   formats=["%Y-%m-%d"])] = first_day_of_month().isoformat(),
        to_date: Annotated[datetime, typer.Option("-u", "--until",
                                                  help="To day (ISO format), default: tomorrow",
                                                  formats=["%Y-%m-%d"])] = tomorrow().isoformat(),
        show_all: Annotated[bool, typer.Option("-a", "--all", help="Show all entries")] = False
):
    with Database(Path("logs.db")) as db:
        result: list[tuple[int, str, float, str, str, str]] = db.get_hours(
            from_date if not show_all else None,
            to_date if not show_all else None
        )
        show_table(result)


@app.command(help="Create an XLS report of the work log entries", no_args_is_help=True)
def export(
        hourly_rate: Annotated[float, typer.Option("-r", "--rate", help="Hourly rate")],
        out_path: Annotated[Path, typer.Option("-o", "--out",
                                               help="Output path, the default name is the year and the "
                                                    "month of the given interval")] = None,
        from_date: Annotated[datetime, typer.Option("-s", "--since",
                                                    help="Since day (ISO format)",
                                                    formats=["%Y-%m-%d"])] = \
                first_day_of_prev_month().isoformat(),
        to_date: Annotated[datetime, typer.Option("-u", "--until",
                                                  help="Until day (ISO format)",
                                                  formats=["%Y-%m-%d"])] = first_day_of_month().isoformat(),

):
    year_w_mont_name = from_date.strftime("%Y %B")
    out_path = Path(year_w_mont_name + ".xlsx")
    with Database(Path("logs.db")) as db:
        result: list[tuple[int, str, float, str, str, str]] = db.get_hours(from_date, to_date)
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
            worksheet.write(0, 3, "Description", bold)
            worksheet.set_column(3, 3, 20)
            worksheet.write(0, 4, "Duration", bold)
            worksheet.write(0, 5, "Amount", bold)
            worksheet.set_column(5, 5, 15)

            # worksheet.autofit()

            total_hours: float = 0.0
            total_amount: float = 0.0
            for i, (_, date, hours, project, task, description) in enumerate(result):
                worksheet.write(i + 1, 0, date.split()[0])
                worksheet.write(i + 1, 1, project)
                worksheet.write(i + 1, 2, task)
                worksheet.write(i + 1, 3, description, wrapped)
                worksheet.write(i + 1, 4, hours, hours_format)
                total_hours += hours
                worksheet.write(i + 1, 5, hours * hourly_rate, euro_format)
                total_amount += hours * hourly_rate

            worksheet.write(i + 3, 3, "Total", bold)
            worksheet.write_formula(i + 3, 4, f"=SUM(E2:E{i + 2})", bold_hours_format, total_hours)
            worksheet.write_formula(i + 3, 5, f"=SUM(F2:F{i + 2})", bold_euro_format, total_amount)


@app.command(help="Remove a work log entries", no_args_is_help=True)
def remove(ids: List[int] = typer.Argument(help="Entry ids to remove")):
    with Database(Path("logs.db")) as db:
        db.remove_hours(ids)


if __name__ == '__main__':
    app()
