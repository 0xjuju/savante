from __future__ import annotations

from app.services.blockchain import SWAP_SIGNATURES
from typing import List, Dict, Any, Tuple, Optional

from pydantic import BaseModel, Field
from web3.types import BlockData, TxReceipt


class BotDetectionResult(BaseModel):
    """Structured result of a single bot‑detection check."""

    is_bot: bool = Field(..., description="True if bot detected for this tx")
    wallet_address: Optional[str] = Field(
        None, description="Wallet address responsible for the bot activity"
    )
    tx_hash: Optional[str] = Field(None, description="Transaction hash examined")
    bot_type: Optional[str] = Field(
        None, description="Identifier for the bot variation (e.g., 'sandwich')"
    )


class DetectionSummary(BaseModel):
    """Aggregate of results over many blocks."""

    blocks_scanned: int
    detections: List[BotDetectionResult]


class SwapBotDetector:
    """High‑level async detector for bot activity in swap transactions."""

    def __init__(self, blocks: List[BlockData]):
        self.blocks = blocks

    async def run(self) -> DetectionSummary:
        """Asynchronously iterate over all blocks & swap txs, applying
        detection heuristics. Returns a structured `DetectionSummary`.
        """
        all_detections: List[BotDetectionResult] = []

        for block in self.blocks:
            detections = await self.detect_sandwich_bot(block)
            all_detections.extend(detections)

        return DetectionSummary(blocks_scanned=len(self.blocks), detections=all_detections)

    async def detect_sandwich_bot(
            self, block: Dict[str, Any]
    ) -> List[BotDetectionResult]:
        """
        Return a list of detected sandwich-bot wallets in **one** block.

        We build an ordered list of every Swap log in the block, then slide a
        3-event window:

            A  (bot)   ➜ pool P
            B  (victim)➜ pool P
            C  (bot)   ➜ pool P   &  sender(A)==sender(C) != sender(B)

        The bot wallet is extracted from `log.topics[1]`, not `tx["from"]`,
        because the latter is usually the router contract.
        """
        swaps: List[Dict[str, Any]] = []

        # ------------------------------------------------------------------ #
        # 1️⃣  Collect every Swap log in this block ------------------------- #
        # ------------------------------------------------------------------ #
        for tx in block["transactions"]:
            for lg in tx.get("swap_logs", []):  # ← list we attached earlier
                if lg["topics"][0].hex().lower() not in SWAP_SIGNATURES:
                    continue  # not a Swap() we care about

                # true wallet = last 20 B of topic[1] (indexed sender)
                sender = "0x" + lg["topics"][1][-20:].hex()

                swaps.append(
                    {
                        "tx_index": tx["transactionIndex"],
                        "log_index": lg["logIndex"],
                        "sender": sender.lower(),
                        "pool": lg["address"].lower(),
                        "tx_hash": tx["hash"].hex()
                        if isinstance(tx["hash"], (bytes, bytearray))
                        else tx["hash"],
                    }
                )

        if len(swaps) < 3:  # not enough events → no sandwich
            return []

        # ------------------------------------------------------------------ #
        # 2️⃣  Order swaps exactly as mined --------------------------------- #
        # ------------------------------------------------------------------ #
        swaps.sort(key=lambda x: (x["tx_index"], x["log_index"]))

        # ------------------------------------------------------------------ #
        # 3️⃣  Sliding-window pattern match -------------------------------- #
        # ------------------------------------------------------------------ #
        detections: List[BotDetectionResult] = []
        i, n = 0, len(swaps)

        while i + 2 < n:
            a, b, c = swaps[i], swaps[i + 1], swaps[i + 2]

            if (
                    a["sender"] == c["sender"]  # same wallet front+back
                    and a["sender"] != b["sender"]  # victim is different wallet
                    and a["pool"] == b["pool"] == c["pool"]
            ):
                detections.append(
                    BotDetectionResult(
                        is_bot=True,
                        wallet_address=a["sender"],
                        tx_hash=a["tx_hash"],
                        bot_type="sandwich",
                    )
                )
                i += 3  # skip ahead past this pattern
            else:
                i += 1  # advance one log and keep scanning

        return detections


__all__ = [
    "SwapBotDetector",
    "BotDetectionResult",
    "DetectionSummary",
]