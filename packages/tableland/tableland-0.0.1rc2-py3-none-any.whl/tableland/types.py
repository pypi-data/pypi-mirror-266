import ast
from re import search
from typing import Literal, Optional, TypedDict

from web3.exceptions import ContractLogicError

# Supported Tableland chain names
ChainName = Literal[
    "mainnet",
    "homestead",
    "optimism",
    "arbitrum",
    "arbitrum_nova",
    "matic",
    "filecoin",
    "sepolia",
    "optimism_sepolia",
    "arbitrum_sepolia",
    "maticmum",
    "filecoin_calibration",
    "local_tableland",
    "localhost",
]


# Tableland config values across different chains
class ChainInfo(TypedDict):
    # mainnets
    mainnet: str | int
    homestead: str | int
    optimism: str | int
    arbitrum: str | int
    arbitrum_nova: str | int
    matic: str | int
    filecoin: str | int
    # testnets
    sepolia: str | int
    optimism_sepolia: str | int
    arbitrum_sepolia: str | int
    maticmum: str | int
    filecoin_calibration: str | int
    # local
    local_tableland: str | int
    localhost: str | int


# Create table event data
class CreateTableEvent(TypedDict):
    owner: str
    table_id: int
    table_name: Optional[str]
    statement: str
    event: str
    transaction_hash: str
    block_number: int
    error: Optional[str]


# Mutate table event data
class MutateTableEvent(TypedDict):
    caller: str
    is_owner: bool
    table_id: int
    table_name: Optional[str]
    statement: str
    policy: str
    event: str
    transaction_hash: str
    block_number: int
    error: Optional[str]


# Table data from validator endpoint
class TableMetadataResponse(TypedDict):
    name: str
    external_url: str
    animation_url: str
    image: str
    attributes: list
    schema: dict


class ReceiptResponse(TypedDict):
    table_id: Optional[str]
    table_ids: Optional[list[str]]
    transaction_hash: str
    block_number: int
    chain_id: int
    error: Optional[str]


class ServerError(Exception):
    pass


class PollingTimeoutError(Exception):
    pass


class NetworkError(Exception):
    def __init__(self, message="", response=None):
        self.message = f"Network error: {message}"
        self.response = response
        if response is not None:
            try:
                json_body = response.json()
                api_error_message = json_body.get("message", "")
                if api_error_message:
                    self.message += f": {api_error_message}"
            except ValueError:
                pass
        super().__init__(self.message)


class RegistryError(Exception):
    def __init__(self, original_exception: ContractLogicError):
        self.original_exception = original_exception
        self.message = "Registry error: "
        error_message = str(original_exception)

        try:
            eval_message = ast.literal_eval(error_message)
            if (
                isinstance(eval_message, tuple)
                and len(eval_message) > 1
                and "message" in eval_message[1]
            ):
                msg_match = search(r"Error: (.+)", eval_message[1]["message"])
                if msg_match:
                    msg = msg_match.group(1)
            else:
                msg = error_message
        except (ValueError, SyntaxError):
            msg = error_message

        self.message += msg
        super().__init__(self.message)
