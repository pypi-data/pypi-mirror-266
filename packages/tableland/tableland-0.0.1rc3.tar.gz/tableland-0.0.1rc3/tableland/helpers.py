from json import loads
from pathlib import Path
from typing import cast

from sqlglot import exp, parse_one

from .types import ChainInfo, ChainName, CreateTableEvent, MutateTableEvent

chain_mapping = ChainInfo(
    mainnet=1,
    homestead=1,
    optimism=10,
    arbitrum=42161,
    arbitrum_nova=42170,
    matic=137,
    filecoin=314,
    sepolia=11155111,
    optimism_sepolia=11155420,
    arbitrum_sepolia=421614,
    maticmum=80001,
    filecoin_calibration=314159,
    local_tableland=31337,
    localhost=31337,
)

homestead_addr = "0x012969f7e3439a9B04025b5a049EB9BAD82A8C12"
proxies = ChainInfo(
    # mainnets
    mainnet=homestead_addr,
    homestead=homestead_addr,
    optimism="0xfad44BF5B843dE943a09D4f3E84949A11d3aa3e6",
    arbitrum="0x9aBd75E8640871A5a20d3B4eE6330a04c962aFfd",
    arbitrum_nova="0x1A22854c5b1642760a827f20137a67930AE108d2",
    matic="0x5c4e6A9e5C1e1BF445A062006faF19EA6c49aFeA",
    filecoin="0x59EF8Bf2d6c102B4c42AEf9189e1a9F0ABfD652d",
    # testnets
    sepolia="0xc50C62498448ACc8dBdE43DA77f8D5D2E2c7597D",
    optimism_sepolia="0x68A2f4423ad3bf5139Db563CF3bC80aA09ed7079",
    arbitrum_sepolia="0x223A74B8323914afDC3ff1e5005564dC17231d6e",
    maticmum="0x4b48841d4b32C4650E4ABc117A03FE8B51f38F68",
    filecoin_calibration="0x030BCf3D50cad04c2e57391B12740982A9308621",
    # local
    local_tableland="0xe7f1725e7734ce288f8367e1bb143e90bb3f0512",
    localhost="",
)

mainnet_uri = "https://tableland.network/api/v1/"
testnet_uri = "https://testnets.tableland.network/api/v1/"
local_tableland_uri = "http://localhost:8080/api/v1/"
base_uris = ChainInfo(
    # mainnets
    mainnet=mainnet_uri,
    homestead=mainnet_uri,
    optimism=mainnet_uri,
    arbitrum=mainnet_uri,
    arbitrum_nova=mainnet_uri,
    matic=mainnet_uri,
    filecoin=mainnet_uri,
    # testnets
    sepolia=testnet_uri,
    optimism_sepolia=testnet_uri,
    arbitrum_sepolia=testnet_uri,
    maticmum=testnet_uri,
    filecoin_calibration=testnet_uri,
    # local
    local_tableland=local_tableland_uri,
    localhost=local_tableland_uri,
)

validator_polling_timeouts = ChainInfo(
    # mainnets
    mainnet=40_000,
    homestead=40_000,
    optimism=10_000,
    arbitrum=10_000,
    arbitrum_nova=10_000,
    matic=15_000,
    filecoin=210_000,
    # testnets
    sepolia=40_000,
    optimism_sepolia=10_000,
    arbitrum_sepolia=10_000,
    maticmum=15_000,
    filecoin_calibration=210_000,
    # local
    local_tableland=5_000,
    localhost=5_000,
)


def chain_id_to_name(chain_id) -> ChainName:
    """Get the chain name from a chain ID."""
    for name, id in chain_mapping.items():
        if id == chain_id:
            return cast(ChainName, name)
    raise ValueError(f"chain ID not found: {chain_id}")


def get_registry_address(chain_id) -> str:
    """Get the registry address for a given chain ID."""
    chain_name = chain_id_to_name(chain_id)
    return str(proxies[chain_name])


def get_validator_base_uri(chain_id) -> str:
    """Get the base URI for a given chain ID."""
    chain_name = chain_id_to_name(chain_id)
    return str(base_uris[chain_name])


def get_validator_polling_config(chain_id) -> dict[str, int]:
    """Get the polling configuration for a given chain ID."""
    chain_name = chain_id_to_name(chain_id)
    timeout = int(validator_polling_timeouts[chain_name])
    # Adjust for longer polling intervals on Filecoin
    interval = 5000 if "filecoin" in chain_name else 1500
    return {"timeout": timeout, "interval": interval}


def read_file_to_json(path: Path) -> dict:
    """Read a file and parse it as JSON."""
    with open(path, "r") as f:
        data = loads(f.read())
    return data


def get_table_parts_from_name(table_name: str) -> dict[str, int | str]:
    """Extract the table ID from a table name."""
    parts = table_name.rsplit("_", 2)
    if len(parts) < 3:
        raise ValueError(f"invalid table name format: {table_name}")

    table_prefix, chain_id, table_id = parts[0], parts[1], parts[2]
    try:
        chain_id_casted = int(chain_id)
        table_id_casted = int(table_id)
    except ValueError:
        raise ValueError("chain ID and Table ID must be integers")

    return {
        "prefix": table_prefix,
        "chain_id": chain_id_casted,
        "table_id": table_id_casted,
    }


def get_table_names_from_statement(statement: str) -> list[str]:
    """Get the names of tables from a SQL statement."""
    names = []
    for table in parse_one(statement).find_all(exp.Table):
        names.append(table.name)
    return names


def prepare_create_statement(statement: str, chain_id: int) -> str:
    """Format the table name in a CREATE TABLE statement by adding the chain ID."""
    ast = parse_one(statement)

    def transformer(node, chain_id: int):
        if isinstance(node, exp.Table):
            original_name = node.args["this"]
            new_name = f"{original_name}_{str(chain_id)}"
            return parse_one(new_name)
        return node

    modified_statement = ast.transform(transformer, chain_id).sql()
    return modified_statement


def parse_create_table_event(data: dict) -> CreateTableEvent:
    """Parse the event log from a `create`'s CreateTable event."""
    owner = data["args"]["owner"]
    table_id = data["args"]["tableId"]
    statement = data["args"]["statement"]
    event = data["event"]
    transaction_hash = data["transactionHash"].hex()
    block_number = data["blockNumber"]

    return CreateTableEvent(
        owner=owner,
        table_id=table_id,
        table_name=None,  # Update this dynamically
        statement=statement,
        event=event,
        transaction_hash=transaction_hash,
        block_number=block_number,
        error=None,
    )


def parse_mutate_event(data: dict) -> MutateTableEvent:
    """Parse the event log from a `mutate`'s RunSQL event."""
    caller = data["args"]["caller"]
    is_owner = data["args"]["isOwner"]
    table_id = data["args"]["tableId"]
    statement = data["args"]["statement"]
    policy = data["args"]["policy"]
    event = data["event"]
    transaction_hash = data["transactionHash"].hex()
    block_number = data["blockNumber"]

    return MutateTableEvent(
        caller=caller,
        is_owner=is_owner,
        table_id=table_id,
        table_name=None,  # Update this dynamically
        statement=statement,
        policy=policy,
        event=event,
        transaction_hash=transaction_hash,
        block_number=block_number,
        error=None,
    )
