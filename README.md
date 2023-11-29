# ⏳ Hours

[![Build](https://github.com/oroszgy/hours/actions/workflows/build.yml/badge.svg)](https://github.com/oroszgy/hours/actions/workflows/build.yml)

A minimalistic work time logger for the command line.

## Usage

Install the package:

```bash
pip install hours
```

Let's add a client first and set the hourly rate:

```bash
hours clients add -n BigCorporate --rate 100 --currency €
hours clients list
```

Then log your work for today:

```bash
hours log -c BigCorporate -h 8.0 -p "ML pipeline" -t "fixing bugs"
```

Get a report for the current month (or any other period):

```bash
hours report 
```

Create a timesheet to Excel file:

```bash
hours export
```

For more information, see the [documentation](https://oroszgy.github.io/hours).

