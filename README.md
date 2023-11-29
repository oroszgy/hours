<div align="center" markdown>

# ⏳ Hours

[![Build](https://github.com/oroszgy/hours/actions/workflows/build.yml/badge.svg)](https://github.com/oroszgy/hours/actions/workflows/build.yml)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/hours)
[![PyPI version](https://badge.fury.io/py/hours.svg)](https://pypi.org/project/hours/)
[![Downloads](https://static.pepy.tech/personalized-badge/hours?period=total&units=international_system&left_color=grey&right_color=green&left_text=Downloads)](https://pepy.tech/project/hours)

A minimalistic work time logger for the command line.
</div>

<hr/>

# Installation

```bash
pip install hours
```

## Usage

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

