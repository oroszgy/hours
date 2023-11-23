from pathlib import Path
from typing import List

import xlsxwriter
from rich.console import Console
from rich.table import Table

from hours.model import Client, Entry


class ConsoleDisplay:
    def __init__(self):
        self._console = Console()

    def _create_table(
        self,
        headers: list[str],
        justify=None,
        bold: bool = False,
        color: str = "magenta",
    ) -> Table:
        table = Table(show_header=True, header_style=f"bold {color}" if bold else color)
        justify = justify or ["default"] * len(headers)
        for header, justify_column in zip(headers, justify):
            table.add_column(header, justify=justify_column)
        return table

    def show_entries(self, entries: List[Entry], clients: List[Client]) -> None:
        table = self._create_table(
            ["Id", "Client", "Day", "Project", "Task", "Hours", "Amount"],
            bold=True,
            justify=["right", "left", "left", "left", "left", "right", "right"],
        )

        total_hours: float = 0.0
        total_amount: float = 0.0
        for entry, client in zip(entries, clients):
            amount: float = client.rate * entry.hours
            table.add_row(
                str(entry.id),
                client.name,
                entry.day.isoformat(),
                entry.project,
                entry.task,
                str(entry.hours),
                f"{client.currency}{amount :.2f}",
            )
            total_hours += entry.hours
            total_amount += amount

        if len(set(client.currency for client in clients)) > 1:
            total_amount_str = "?"
        else:
            total_amount_str = f"{clients[0].currency}{total_amount :,.2f}"

        table.add_section()
        table.add_row("", "", "", "", "Total", str(total_hours), total_amount_str, style="bold green")

        self._console.print(table)

    def show_clients(self, clients: List[Client]) -> None:
        table = self._create_table(["Name", "Rate", "Currency"], bold=True, justify=["left", "right", "left"])
        for client in clients:
            table.add_row(client.name, f"{client.rate:,.2f}", client.currency)

        self._console.print(table)


class FileDisplay:
    def save_to_excel(
        self,
        entries: list[Entry],
        hourly_rate: float,
        currency: str,
        out_path: Path,
        sheet_name: str,
    ) -> None:
        with xlsxwriter.Workbook(out_path) as workbook:
            worksheet = workbook.add_worksheet(sheet_name)
            bold = workbook.add_format({"bold": True})
            wrapped = workbook.add_format()
            wrapped.set_text_wrap()
            euro_format = workbook.add_format({"num_format": f"{currency}#,##0.00"})
            bold_euro_format = workbook.add_format({"num_format": f"{currency}#,##0.00", "bold": True})
            hours_format = workbook.add_format({"num_format": "0.00"})
            bold_hours_format = workbook.add_format({"num_format": "0.00", "bold": True})

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
            for i, entry in enumerate(entries):
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
