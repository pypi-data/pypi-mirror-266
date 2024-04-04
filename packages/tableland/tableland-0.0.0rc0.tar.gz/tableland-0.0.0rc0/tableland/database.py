from pathlib import Path
from time import sleep, time

from eth_account import Account
from eth_utils import to_checksum_address
from requests import HTTPError, RequestException, get
from web3 import Web3
from web3._utils.events import EventLogErrorFlags
from web3.contract import Contract
from web3.exceptions import ContractLogicError
from web3.types import HexBytes, TxReceipt

from .helpers import (
    get_registry_address,
    get_table_names_from_statement,
    get_table_parts_from_name,
    get_validator_base_uri,
    get_validator_polling_config,
    parse_create_table_event,
    parse_mutate_event,
    prepare_create_statement,
    read_file_to_json,
)
from .types import (
    CreateTableEvent,
    MutateTableEvent,
    NetworkError,
    PollingTimeoutError,
    ReceiptResponse,
    RegistryError,
    ServerError,
    TableMetadataResponse,
)


class Database:

    registry: Contract
    signer: Account
    validator_uri: str
    w3: Web3

    def __init__(
        self,
        private_key: str,
        provider_uri: str,
    ):
        # Set up web3 instance and signer
        self.w3 = Web3(Web3.HTTPProvider(provider_uri))
        self.signer = Account.from_key(private_key)
        # Set up Tableland registry contract and validator base URI
        abi_file = Path(__file__).parent.parent / "abi.json"
        abi = read_file_to_json(abi_file)
        registry_addr = get_registry_address(self.w3.eth.chain_id)
        self.registry = self.w3.eth.contract(
            address=to_checksum_address(registry_addr), abi=abi
        )
        self.validator_uri = get_validator_base_uri(chain_id=self.get_chain_id())

    def get_signer_address(self):
        return self.signer.address

    def get_chain_id(self) -> int:
        return self.w3.eth.chain_id

    def wait_for_tx_receipt(self, tx_hash: HexBytes | HexBytes) -> TxReceipt:
        return self.w3.eth.wait_for_transaction_receipt(tx_hash)

    def parse_tx_receipt(self, tx_receipt: TxReceipt, event_type: str) -> dict:
        event = getattr(self.registry.events, event_type)()
        return event.process_receipt(tx_receipt, errors=EventLogErrorFlags.Discard)

    def create(self, statement: str, wait=True) -> CreateTableEvent:
        """Create a new table onchain."""
        try:
            chain_id = self.get_chain_id()
            stmt = prepare_create_statement(statement, chain_id)
            tx_hash = self.registry.functions.create(
                self.get_signer_address(), stmt
            ).transact()
            rec = self.wait_for_tx_receipt(tx_hash)
            log = self.parse_tx_receipt(rec, "CreateTable")
            data = parse_create_table_event(log[0])
            table_name = (
                get_table_names_from_statement(stmt)[0] + f"_{data['table_id']}"
            )
            data["table_name"] = table_name
            # Wait for validator to materialize SQL
            if wait:
                validator_rec = self.get_receipt(tx_hash)
                if validator_rec is not None and "error" in validator_rec:
                    data["error"] = validator_rec["error"]
            return data
        except ContractLogicError as e:
            raise RegistryError(e) from e
        except Exception as e:
            raise Exception(f"Unexpected error: {e}") from e

    def write(self, statement: str, wait=True) -> MutateTableEvent:
        """Execute a write query onchain."""
        try:
            table_name = get_table_names_from_statement(statement)[0]
            table_id = get_table_parts_from_name(table_name)["table_id"]
            sender = self.get_signer_address()
            tx_hash = self.registry.functions.mutate(
                sender, table_id, statement
            ).transact({"from": sender})
            rec = self.wait_for_tx_receipt(tx_hash)
            log = self.parse_tx_receipt(rec, "RunSQL")
            data = parse_mutate_event(log[0])
            data["table_name"] = table_name
            # Wait for validator to materialize SQL
            if wait:
                validator_rec = self.get_receipt(tx_hash)
                if validator_rec is not None and "error" in validator_rec:
                    data["error"] = validator_rec["error"]
            return data
        except ContractLogicError as e:
            raise RegistryError(e) from e
        except Exception as e:
            raise Exception(f"Unexpected error: {e}") from e

    def read(self, statement: str) -> dict:
        """Execute a read query against a validator."""
        try:
            url = f"{self.validator_uri}query"
            params = {"statement": statement}
            response = get(url, params=params)

            if response.status_code == 200:
                data = response.json()
            else:
                response.raise_for_status()
        except HTTPError as e:
            # Catch response from "no such table" error
            raise NetworkError("Network error", response=e.response) from e
        except RequestException as e:
            raise NetworkError(e) from e
        except Exception as e:
            raise Exception(f"Unexpected error: {e}") from e

        return data

    def get_owner(self, table_id: int) -> str | None:
        """Get the owner of a table by its ID."""
        try:
            data = self.registry.functions.ownerOf(table_id).call()
        except ContractLogicError as e:
            raise RegistryError(e) from e
        except Exception as e:
            raise Exception(f"Unexpected error: {e}") from e

        return data

    def get_receipt(self, tx_hash: str | HexBytes) -> ReceiptResponse:
        """Get create or mutation transaction receipt from a validator."""
        try:
            chain_id = self.get_chain_id()
            validator_info = get_validator_polling_config(chain_id)
            timeout, interval = (
                validator_info["timeout"],
                validator_info["interval"],
            )
            timeout_ms = timeout / 1000
            interval_ms = interval / 1000
            start_time = time()

            while True:
                chain_id = self.get_chain_id()
                if isinstance(tx_hash, HexBytes):
                    tx_hash_str = tx_hash.hex()
                else:
                    tx_hash_str = tx_hash
                url = f"{self.validator_uri}receipt/{chain_id}/{tx_hash_str}"
                response = get(url)
                if response.status_code == 200:
                    res = response.json()
                    data: ReceiptResponse = {
                        "table_id": res.get("table_id"),
                        "table_ids": res.get("table_ids"),
                        "transaction_hash": res["transaction_hash"],
                        "block_number": res["block_number"],
                        "chain_id": res["chain_id"],
                        "error": res.get("error"),
                    }
                    break
                elif response.status_code >= 500:
                    raise ServerError(f"Server error: {response.status_code}")
                elif time() - start_time > timeout_ms:
                    raise PollingTimeoutError("Validator polling timeout reached")
                else:
                    sleep(interval_ms)
        except RequestException as e:
            raise NetworkError(e) from e
        except Exception as e:
            raise Exception(f"Unexpected error: {e}") from e

        return data

    def get_table_info(self, table_id: int) -> TableMetadataResponse:
        """Get table metadata by its table ID."""
        try:
            chain_id = self.get_chain_id()
            url = f"{self.validator_uri}tables/{chain_id}/{table_id}"
            response = get(url)
            if response.status_code == 200:
                data = response.json()
            elif response.status_code >= 500:
                raise ServerError(f"Server error: {response.status_code}")
            else:
                response.raise_for_status()
        except RequestException as e:
            if "404 Client Error" in str(e):
                raise NetworkError("table not found") from e
            else:
                raise NetworkError(e) from e
        except Exception as e:
            raise Exception(f"Unexpected error: {e}") from e

        return data
