import pytest
from unittest.mock import AsyncMock, patch
from web3.types import BlockData, TxData, TxReceipt, BlockNumber

from app.services.blockchain import BlockchainParser


@pytest.fixture
def parser():
    return BlockchainParser("ethereum")


@pytest.mark.asyncio
async def test_get_block(parser):
    fake_block: BlockData = {
        "number": BlockNumber(12345678),
        "hash": b"0xabc",
        "transactions": []
    }

    with patch.object(parser.web3.eth, "get_block", return_value=fake_block):
        block = await parser.get_block(12345678)
        assert block["number"] == 12345678


@pytest.mark.asyncio
async def test_get_transaction(parser):
    fake_tx: TxData = {
        "hash": b"0x123",
        "from": "0xabc",
        "to": "0xdef",
        "value": 1000000000000000000
    }

    with patch.object(parser.web3.eth, "get_transaction", return_value=fake_tx):
        tx = await parser.get_transaction("0x123")
        assert tx["from"] == "0xabc"
        assert tx["to"] == "0xdef"


@pytest.mark.asyncio
async def test_get_transaction_receipt(parser):
    fake_receipt = {
        "transactionHash": b"0x123",
        "status": 1,
        "logs": []
    }

    with patch.object(parser.web3.eth, "get_transaction_receipt", return_value=fake_receipt):
        receipt = await parser.get_transaction_receipt("0x123")
        assert receipt["status"] == 1
        assert isinstance(receipt["logs"], list)


@pytest.mark.asyncio
async def test_is_dex_trade_detects_known_addresses(parser):
    known_log = {"address": "0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f"}  # uniswap_v2
    unknown_log = {"address": "0x000000000000000000000000000000000000dead"}
    tx_receipt = {"logs": [unknown_log, known_log]}

    assert parser.is_dex_trade(tx_receipt) is True


@pytest.mark.asyncio
async def test_is_dex_trade_returns_false(parser):
    unrelated_logs = [{"address": "0x000000000000000000000000000000000000dead"}]
    tx_receipt = {"logs": unrelated_logs}

    assert parser.is_dex_trade(tx_receipt) is False
