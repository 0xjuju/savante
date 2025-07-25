import asyncio
from concurrent.futures import ThreadPoolExecutor
import httpx
import json

import redis
import requests
from typing import Optional, Any, Callable, TypeVar
import websockets

from app.core.config import get_settings
from app.schemas.blockchain import LogTx, MemTx, MinedTx
from pydantic import BaseModel
from app.utils.batch_utils import Batcher
from web3 import Web3
from web3.types import BlockData, LogReceipt, TxData, TxReceipt


settings = get_settings()
http_client = httpx.AsyncClient(timeout=10)
T = TypeVar("T")
TModel = TypeVar("TModel", bound=BaseModel)

SWAP_SIGNATURES = {
    # Uniswap V2 (factory 0x5C69…): two known signatures
    "0xd78ad95fa46c994b6551d0da85fc275fe613d9a74a2e37e3aed6e05d495e7c05",
    "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822",
    # Uniswap V3: old and new compiler layouts
    "0x414bf3899069d4b60af01391247d2d649f6cf533f4a8276e43d4b82030dced92",
    "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67",
}


class BlockchainParser:
    def __init__(self, chain: str, max_workers: int = 25):
        self.ALCHEMY_MAP = {
            "ethereum": "eth",
            "base": "base",
            "arbitrum": "arb",
        }

        self.chain = chain.lower()
        self.rpc_url = self._get_rpc_url()
        self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))

        self.WSS = f"wss://{self.ALCHEMY_MAP[self.chain]}-mainnet.g.alchemy.com/v2/{settings.alchemy_api_key}"

        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def _get_rpc_url(self) -> str:

        if self.chain not in self.ALCHEMY_MAP:
            raise ValueError(f"Unsupported chain: {self.chain}")

        return f"https://{self.ALCHEMY_MAP[self.chain]}-mainnet.g.alchemy.com/v2/{settings.alchemy_api_key}"

    @staticmethod
    def _get_signatures() -> list[str]:
        sigs = [
            "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67",
            "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822",
            "0x8b3e96f2b889fa771c53c981b40daf005f63f637f1869f707052d15a3dd97140",
            "0xd013ca23e77a65003c2c659c5442c00c805371b7fc1ebd4c206c41d1536bd90b",
            "0x769f4ac79fc2a7fdfe0f2b27434977aaf4f89a517fc672d4103f04c05f107224",
            "0xa9ba3ffe0b6c366b81232caab38605a0699ad5398d6cce76f91ee809e322dafc",
            "0x3e1d5e5686e0d1cabb4bcb83fdbe57c97349678fc1fd595d1870eebc0b2fac45",
            "0x9ea7ed25e4b8692d3bbf2e42100437b3dce58c15ddf437c1e099cb5b04a08f94",
        ]

        return sigs

    async def _run_io(self, func: Callable[[], T]) -> T:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, func)

    async def _stream(self, subscription_type: str, params: dict, model: type[TModel], endpoint: str,
                      redis_client: redis.Redis):
        """
        :param subscription_type: websockets subscription type
        :param params: Stream filters
        :param model: Pydantic model structure for data
        :param endpoint: Where we are sending the data
        :return:
        """

        domain = settings.domain

        id_map = {
            "alchemy_pendingTransactions": 1,
            "alchemy_minedTransactions": 2,
            "logs": 1
        }

        batcher = Batcher(
            name=subscription_type,
            model=model,
            endpoint=f"{domain}/api/{endpoint}",
            batch_period=10,
            redis=redis_client,
            http=http_client,
            chain=self.chain
        )

        print(f"({self.chain}) Start listening... {subscription_type}")
        async with websockets.connect(self.WSS) as ws:
            await ws.send(json.dumps({
                "jsonrpc": "2.0",
                "id": id_map[subscription_type],
                "method": "eth_subscribe",
                "params": [subscription_type, params]
            }))

            try:
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    if "error" in data:
                        raise ValueError(data)

                    if "params" in data:
                        data = data["params"]["result"]
                        if subscription_type == "alchemy_minedTransactions":
                            data = data["transaction"]

                        await batcher.enqueue(data)

            finally:
                print("Closing WebSocket...")
                await ws.close()

    async def add_logs_to_blocks(self, blocks: list[BlockData]) -> list[BlockData]:
        coroutines = [self.get_swap_logs(b["number"], SWAP_SIGNATURES) for b in blocks]
        logs = await asyncio.gather(*coroutines)

        enriched_blocks: list[dict[str, Any]] = []
        for block, swap_logs in zip(blocks, logs):
            blk: dict[str, Any] = dict(block)

            # Build tx_hash → [logs] map
            tx_log_map: dict[bytes, list] = {}
            for lg in swap_logs:
                tx_hash = lg["transactionHash"]
                tx_log_map.setdefault(tx_hash, []).append(lg)

            # Deep-copy each tx into mutable dict and attach its logs
            txs = []
            for tx in blk["transactions"]:
                tx_dict = dict(tx)
                tx_dict["swap_logs"] = tx_log_map.get(tx["hash"], [])
                txs.append(tx_dict)

            blk["transactions"] = txs
            enriched_blocks.append(blk)

        return enriched_blocks

    async def get_block(self, block_number: int, full_tx: bool = True) -> BlockData:
        return await self._run_io(lambda: self.web3.eth.get_block(block_number, full_transactions=full_tx))

    async def get_swap_logs(self, block_number: int, signatures: set[str]) -> list[LogReceipt]:
        return await self._run_io(
            lambda: self.web3.eth.get_logs({
                "fromBlock": block_number,
                "toBlock": block_number,
                "topics": [list(signatures)]
            })
        )

    async def get_transaction(self, tx_hash: str) -> TxData:
        return await self._run_io(lambda: self.web3.eth.get_transaction(tx_hash))

    async def get_transaction_receipt(self, tx_hash: str) -> TxReceipt:
        return await self._run_io(lambda: self.web3.eth.get_transaction_receipt(tx_hash))

    async def get_recent_blocks(self, count: int = 5, start_block: Optional[int] = None) -> list[BlockData]:

        latest = start_block or self.web3.eth.block_number
        tasks = [self.get_block(latest - i) for i in range(count)]

        return await asyncio.gather(*tasks)

    def is_dex_trade(self, tx_receipt: TxReceipt) -> bool:
        dex_addresses = {
            "uniswap_v2": "0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f",
            "sushiswap": "0xc0aee478e3658e2610c5f7a4a2e1777ce9e4f2ac",
        }
        return any(log['address'].lower() in dex_addresses.values() for log in tx_receipt['logs'])

    async def stream_mempool(self, redis_client: redis.Redis, to_addresses: list[str] = None):
        """
        Subscribe to mempool transactions
        :param redis_client: Message queue
        :param to_addresses: address filters
        """
        await self._stream(
            subscription_type="alchemy_pendingTransactions",
            params={"toAddress": to_addresses},
            model=MemTx,
            endpoint="mempool",
            redis_client=redis_client
        )

    async def stream_mined_transactions(self, redis_client: redis.Redis, to_addresses: list[str] = None):
        """
        Stream mined transactions to endpoint

        :param redis_client: Message queue
        :param to_addresses: Address filters
        """

        # Format list of addresses
        params = {
            "addresses": [{"to": address} for address in to_addresses]
        }

        await self._stream(
            subscription_type="alchemy_minedTransactions",
            params=params,
            model=MinedTx,
            endpoint="mined-transactions",
            redis_client=redis_client
        )

    async def stream_swaps(self, redis_client: redis.Redis):
        """
         Subscribe to mempool transactions
        :param redis_client: Message queue
        """

        logs = {
            "topics": [self._get_signatures()]
        }

        await self._stream(
            subscription_type="logs",
            params=logs,
            model=LogTx,
            endpoint="blockchain/logs",
            redis_client=redis_client
        )

    async def trace_transaction(self, tx_hash: str) -> dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "alchemy_traceTransaction",
            "params": [tx_hash],
        }
        return await self._run_io(lambda: requests.post(self.rpc_url, json=payload, headers=headers).json())
