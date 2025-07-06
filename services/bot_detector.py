from __future__ import annotations
from typing import Any, Dict, List

from app.schemas.blockchain import BotDetectionResult, DetectionSummary
from app.services.blockchain import SWAP_SIGNATURES
from web3.types import BlockData


class SwapBotDetector:
    """High‑level async detector for bot activity in swap transactions"""

    def __init__(self, blocks: List[BlockData]):
        self.blocks = blocks

    async def run(self) -> DetectionSummary:
        all_detections: List[BotDetectionResult] = []

        for block in self.blocks:
            detections = await self.detect_sandwich_bot(block)
            all_detections.extend(detections)

        return DetectionSummary(blocks_scanned=len(self.blocks), detections=all_detections)

    async def detect_sandwich_bot(
            self, block: Dict[str, Any]
    ) -> List[BotDetectionResult]:

        swaps: List[Dict[str, Any]] = []

        for tx in block["transactions"]:
            for lg in tx.get("swap_logs", []):  # ← list we attached earlier
                if lg["topics"][0].hex().lower() not in SWAP_SIGNATURES:
                    continue

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

        if len(swaps) < 3:
            return []

        swaps.sort(key=lambda x: (x["tx_index"], x["log_index"]))

        detections: List[BotDetectionResult] = []
        i, n = 0, len(swaps)

        while i + 2 < n:
            a, b, c = swaps[i], swaps[i + 1], swaps[i + 2]

            if (
                    a["sender"] == c["sender"]
                    and a["sender"] != b["sender"]
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
                i += 3
            else:
                i += 1

        return detections


__all__ = [
    "SwapBotDetector",
    "BotDetectionResult",
    "DetectionSummary",
]