# tableland.py

[![License: MIT AND Apache-2.0](https://img.shields.io/badge/License-MIT%20AND%20Apache--2.0-blue.svg)](./LICENSE)
[![standard-readme compliant](https://img.shields.io/badge/standard--readme-OK-green.svg)](https://github.com/RichardLitt/standard-readme)
[![PyPI version](https://badge.fury.io/py/tableland.svg)](https://badge.fury.io/py/tableland)

> A minimal Tableland Python SDK for creating, writing, and reading onchain tables

## Background

This package is a simple Python SDK for the [Tableland](https://tableland.xyz) network. It's built around the [web3.py](https://web3py.readthedocs.io/en/stable/) library for onchain interactions and lets developers create, read, and write data to Tableland tables.

## Install

You can install with `pip`:

```sh
pip install tableland
```

With `pipx`:

```sh
pipx install tableland
```

Or with `poetry`:

```sh
poetry add tableland
```

## Usage

Start by importing the `Database` class and creating a new instance with an RPC provider for your desired chain and private key. You can then create a new table, write data to the table, and read data from the table.

```python
from tableland import Database

private_key = "59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"  # Replace with your private key
db = Database(
    private_key=private_key,
    provider_uri="http://localhost:8545",  # Replace with your chain RPC provider URL
)

# Create a new table
statement = "create table my_table (id int, val text)"
create_event = db.create(statement)
table_name = create_event["table_name"]
table_id = create_event["table_id"]

# Check if there are any errors
if create_event["error"] is not None:
    print(f"Error: {create_event['error']}")

# Insert a row into the table
statement = f"insert into {table_name} (id, val) values (1, 'hello')"
write_event = db.write(statement)

# Check if there are any errors
if write_event["error"] is not None:
    print(f"Error: {write_event['error']}")

# Query the table
statement = f"select * from {table_name}"
data = db.read(statement)
print(data)
# [{'id': 1, 'val': 'hello'}]
```

The `Database` class also has a few other methods, including getting the transaction receipt for create or write events, getting the table's owner, signer's address, or various table information:

```python
# Alternatively, manually get validator transaction receipt vs. checking `write_event["error"]` value
statement = f"insert into {table_name} (id, val) values (1, 'hello', 'an erroneous value')"
write_event = db.write(statement)
tx_hash = write_event["transaction_hash"]
receipt = db.get_receipt(tx_hash)
if receipt["error"] is not None:
    print(f"Error: {write_event['error']}")

# Get the chain ID
chain_id = db.get_chain_id()
# 31337

# Get table info
owner = db.get_owner(table_id)
print(owner)
# 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266

# Get table info
schema = db.get_table_info(table_id)["schema"]["columns"]
print(schema)
# [{"name": "id", "type": "int"}, {"name": "val", "type": "text}]

# Get the signer address
address = db.get_signer_address()
print(address)
# 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
```

There are also a few helper functions, including getting table information, Tableland registry contract addresses, or validator URL information:

```python
from tableland import get_registry_address, get_table_parts_from_name, get_validator_base_uri

# Get Tableland registry contract address
registry_address = get_registry_address(chain_id)
print(registry_address)
# 0xe7f1725e7734ce288f8367e1bb143e90bb3f0512

# Get the table prefix, chain ID, and table ID from a table name
parts = get_table_parts_from_name(table_name)
print(parts)
# {"prefix": "my_table", "chain_id": 31337, "table_id": 2}

# Get validator base URI for a given chain
chain_id = 31337  # Replace with your chain ID
base_uri = get_validator_base_uri(chain_id)
print(base_uri)
# http://localhost:8080/api/v1/

# Get the validator's poling settings
config = get_validator_polling_config(31337)
print(config)
# {"timeout": 5000, "interval": 1_500}
```

## Development

This project uses [poetry](https://python-poetry.org/docs/#installation) for dependency management. Make sure [pipx](https://pipx.pypa.io/stable/installation/) is installed (e.g., `brew install pipx` on Mac) and then install poetry with `pipx install poetry`.

Once that's set up, you can install the project dependencies and run various tasks via [`poe`](https://poethepoet.natn.io/poetry_plugin.html) or `poetry run`. You can view all of the available tasks by running `poetry run poe --help` or reviewing the `[tool.poe.tasks]` of the `pyproject.toml` file.

```sh
# Install dependencies
poetry install

# Setup pre-commit and pre-push hooks
poetry poe pre-commit

# Run linters
poetry poe lint

# Run tests
poetry poe test
poetry poe coverage
# Or
poetry run pytest

# Build the package
poetry build
```

> Note: if you're using a Mac M1/M2 and the default poetry settings, you _might_ run into issues with respect to the Python virtual environment's cache directory defined in the global poetry configuration. Check the path by running `poetry config --list` and looking at the `cache-dir` value. If that's the case, running `poetry config cache-dir "$HOME/.local/share/virtualenvs"` should fix it (i.e., the previous value is `$HOME/Library/Caches/pypoetry`). Alternatively, setting the `virtualenvs.in-project` config to `true` will use a local `.venv` instead.

## Contributing

PRs accepted.

This package was created with Cookiecutter and the [sourcery.ai](https://github.com/sourcery-ai/python-best-practices-cookiecutter) project template. Small note: If editing the README, please conform to the
[standard-readme](https://github.com/RichardLitt/standard-readme) specification.

## License

MIT AND Apache-2.0, © 2021-2024 Tableland Network Contributors
