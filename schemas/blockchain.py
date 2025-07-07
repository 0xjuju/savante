
from typing import List, Optional

from pydantic import BaseModel, Field


class MemTx(BaseModel):
    hash: str
    sender: str = Field(..., alias="from")
    to: str
    input: str
    gas: str
    gas_price: str = Field(..., alias="gasPrice")


class MinedTx(BaseModel):
    block_number: int = Field(..., alias="blockNumber")
    hash: str
    sender: str = Field(..., alias="from")
    to: str
    input: str
    value: str = Field(..., description="Native Ethereum value")


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
