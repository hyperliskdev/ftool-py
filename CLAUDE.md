# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ftool-py is a Python CLI tool for interacting with CrowdStrike Falcon APIs using the falconpy library. It provides commands for managing and querying Falcon hosts/devices. This is a Python rewrite of a Rust tool (ftool-rs) that previously used rusty_falcon.

## Setup and Installation

The tool requires CrowdStrike API credentials stored in a `.env` file in the project root:
- Copy `.env.example` to `.env`
- Add `FALCON_CLIENT_ID` and `FALCON_CLIENT_SECRET` values
- The tool must be run from the same directory as the `.env` file

Install globally in editable mode:
```bash
pipx install -e . --force
```

After installation, the `ftool` command is available globally.

## Architecture

### Command Registration Pattern
New commands follow a registration pattern in `ftoolpy/commands/`:

1. Each command is a separate Python module in `ftoolpy/commands/`
2. Commands implement two functions:
   - `register_subcommand(subparsers)` - registers the argparse subcommand
   - A handler function (set via `parser.set_defaults(func=handler)`)
3. Commands are registered in `ftoolpy/cli.py` by importing and calling `register_subcommand()`

### Authentication
All Falcon API calls use the centralized `get_client()` function from `ftoolpy/auth.py`:
- Loads credentials from `.env` file
- Returns an initialized `APIHarnessV2` instance from falconpy
- Raises exceptions if `.env` is missing or credentials are not found

### Falcon API Patterns
The codebase uses the `falcon.command()` method to call Falcon APIs:

```python
falcon = get_client()
response = falcon.command("QueryDevicesByFilter", filter=f"hostname:'{hostname}'", limit=5000)
```

Common API calls:
- `QueryDevicesByFilter` - search for devices by hostname, returns device IDs
- `PostDeviceDetailsV2` - get detailed device information (last_seen, first_seen, etc.)
- `QueryHiddenDevices` - query hidden/decommissioned devices
- `UpdateDeviceTags` - add/remove tags from devices (requires `FalconGroupingTags/` prefix)

Response structure:
- `response["status_code"]` - HTTP status code
- `response["body"]["resources"]` - array of results (device IDs or device objects)

## Existing Commands

### alive-hosts
Checks online/offline status of hosts from an input file.

```bash
ftool alive-hosts -i hostnames.txt -o results.csv
ftool alive-hosts -i hostnames.txt --dead  # Show only offline hosts
```

Implementation notes:
- Takes hostnames (one per line) as input
- Queries devices using `QueryDevicesByFilter` with hostname filter
- Retrieves device details with `PostDeviceDetailsV2`
- The `--dead` flag shows hostnames that were not found in Falcon (offline/removed)
- Output format: `hostname,device_id,last_seen,first_seen`

### tag-hosts
Adds or removes tags from hosts.

```bash
ftool tag-hosts -i hostnames.txt -t "Critical" -a add
ftool tag-hosts -i hostnames.txt -t "Critical" -a remove
```

Implementation notes:
- Tags must be prefixed with `FalconGroupingTags/` (automatically added if missing)
- Processes one hostname at a time (no batching)
- Success indicated by HTTP 202 response from `UpdateDeviceTags`

## Adding New Commands

1. Create a new file in `ftoolpy/commands/your_command.py`
2. Implement `register_subcommand(subparsers)` to define arguments
3. Implement the handler function
4. Import and register in `ftoolpy/cli.py`

Example skeleton:
```python
from ftoolpy.auth import get_client

def register_subcommand(subparsers):
    parser = subparsers.add_parser("my-command", help="Description")
    parser.add_argument("-i", "--input", required=True, help="Input file")
    parser.set_defaults(func=my_handler)

def my_handler(args):
    falcon = get_client()
    # Implementation here
```
