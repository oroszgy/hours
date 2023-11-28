# Quickstart

First, let's add a client and set the hourly rate:

```bash
$ hours clients add -c BigCorporate --rate 100 --currency €
$ hours clients list
```

Then, log your work for today:

```bash
hours log -c BigCorporate -h 8.0 -p "ML pipeline" -t "fixing bugs"
```

Having some data in the database, you can get a report for the current month:

```bash
hours report 
```

Later on, you can prepare a timesheet and export it to an Excel file:

```bash
hours export
```
