## Webex workspaces commands utilities 

## Usage:
```
Usage: python -m wbx_workspaces [OPTIONS] COMMAND [ARGS]...

Options:
  --version            Show the version and exit.
  -t, --token TEXT     Your access token. Read from AUTH_BEARER env variable
                       by default. You can find your personal token at
                       https://developer.webex.com/docs/getting-started.
  -d, --debug INTEGER  Debug level.
  --help               Show this message and exit.

Commands:
  locations   List locations IDs
  metrics     Gather yesterday's hourly peopleCount or timeUsed metric...
  workspaces  Get the list of workspaces in given location
```

# Examples:
```
ython -m wbx_workspaces workspaces -l Y2lzY29zcGFyazovL3VzL0xPQ0FUSU9OLzhkZDI0ZWRmLWFjOWQtNDcxYi05MTIxLTJmM2EzYjk0YzRlYQ

```

## Notes:
