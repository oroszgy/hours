# Work

A minimalistic work time logger for the command line.

## Usage

First add a client:
```bash
hours clients add -c BigCorporate --rate 100 --currency €
hours clients list
```
Then log your work for today:
```bash
hours log -c BigCorporate -h 8.0 -p "ML pipeline" -t "fixing bugs"
```

Get a report for the current month:
```bash
hours report 
```

Create a timesheet to Excel file:
```bash
hours export
```

For more information, see the help:
```bash
hours --help
                                                                                                                                                                                                                                            
 Usage: hours [OPTIONS] COMMAND [ARGS]...                                                                                                                                                                                                   
                                                                                                                                                                                                                                            
 A minimalistic work time logger for the command line.                                                                                                                                                                                  
                                                                                                                                                                                                                                            
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion        [bash|zsh|fish|powershell|pwsh]  Install completion for the specified shell. [default: None]                                                                                                                 │
│ --show-completion           [bash|zsh|fish|powershell|pwsh]  Show completion for the specified shell, to copy it or customize the installation. [default: None]                                                                          │
│ --help                                                       Show this message and exit.                                                                                                                                                 │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ clients                              Manage clients                                                                                                                                                                                      │
│ export                               Create an XLS report of the work log entries                                                                                                                                                        │
│ log                                  Log worked hours.                                                                                                                                                                                   │
│ remove                               Remove a work log entries                                                                                                                                                                           │
│ report                               List work log entries                                                                                                                                                                               │
│ update                               Log worked hours.                                                                                                                                                                                   │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

# Roadmap

- [ ] Error handling, copy
- [ ] CI/CD: GitHub Actions
- [ ] Documentation: mkdocs

