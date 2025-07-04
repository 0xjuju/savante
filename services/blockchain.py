import asyncio
from concurrent.futures import ThreadPoolExecutor
import requests
from typing import List, Optional, Dict, Any, Callable, TypeVar

from app.core.config import get_settings
from web3 import Web3
from web3.types import BlockData, TxData, TxReceipt


settings = get_settings()
T = TypeVar("T")


class BlockchainParser:
    def __init__(self, chain: str, max_workers: int = 25):
        self.chain = chain.lower()
        self.rpc_url = self._get_rpc_url()
        self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))

        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def _get_rpc_url(self) -> str:
        ALCHEMY_MAP = {
            "ethereum": "eth",
            "base": "base",
            "arbitrum": "arb",
        }
        if self.chain not in ALCHEMY_MAP:
            raise ValueError(f"Unsupported chain: {self.chain}")

        return f"https://{ALCHEMY_MAP[self.chain]}-mainnet.g.alchemy.com/v2/{settings.alchemy_api_key}"

    async def _run_io(self, func: Callable[[], T]) -> T:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, func)

    async def get_block(self, block_number: int, full_tx: bool = True) -> BlockData:
        return await self._run_io(lambda: self.web3.eth.get_block(block_number, full_transactions=full_tx))

    async def get_transaction(self, tx_hash: str) -> TxData:
        return await self._run_io(lambda: self.web3.eth.get_transaction(tx_hash))

    async def get_transaction_receipt(self, tx_hash: str) -> TxReceipt:
        return await self._run_io(lambda: self.web3.eth.get_transaction_receipt(tx_hash))

    def is_dex_trade(self, tx_receipt: TxReceipt) -> bool:
        dex_addresses = {
            "uniswap_v2": "0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f",
            "sushiswap": "0xc0aee478e3658e2610c5f7a4a2e1777ce9e4f2ac",
        }
        return any(log['address'].lower() in dex_addresses.values() for log in tx_receipt['logs'])

    async def get_recent_blocks(
        self, count: int = 5, start_block: Optional[int] = None
    ) -> List[BlockData]:
        latest = start_block or self.web3.eth.block_number
        tasks = [
            self.get_block(latest - i)
            for i in range(count)
        ]
        return await asyncio.gather(*tasks)

    async def detect_sandwich_bot(self, block: BlockData) -> List[Dict[str, Any]]:
        print(f"Analyzing sandwich activity in block {block['number']}")
        return []

    async def detect_frontrun_bot(self, block: BlockData) -> List[Dict[str, Any]]:
        print(f"Analyzing frontrunning in block {block['number']}")
        return []

    async def detect_arbitrage_bot(self, block: BlockData) -> List[Dict[str, Any]]:
        print(f"Analyzing arbitrage in block {block['number']}")
        return []

    async def trace_transaction(self, tx_hash: str) -> Dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "alchemy_traceTransaction",
            "params": [tx_hash],
        }
        return await self._run_io(lambda: requests.post(self.rpc_url, json=payload, headers=headers).json())
