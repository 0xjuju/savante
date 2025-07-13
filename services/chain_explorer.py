import json
import requests

from eth_utils import keccak

CHAIN_ID = {
    "ethereum": 1,
    "base": 8453,
    "arbitrum": 42161,
}

KEYWORDS = {"swap", "exchange"}

ALT_EVENT_NAMES = {
    "curve": {"tokenexchange", "tokenexchangeunderlying"},
}


def get_contract_abi(address: str, chain: str) -> list[dict] | None:
    url = f"https://sourcify.dev/server/v2/contract/{CHAIN_ID[chain]}/{address}?fields=abi"
    r = requests.get(url, timeout=8)
    if r.status_code != 200:
        return r.json()
    return r.json()["abi"]


def swap_selectors(address: str, chain: str):
    abi = get_contract_abi(address, chain)
    if not isinstance(abi, list):
        raise ValueError(f"ABI missing for {address}")

    selectors, topics = set(), set()
    for item in abi:
        name = item.get("name", "").lower()
        if item["type"] == "function" and any(k in name for k in KEYWORDS):
            sig = f'{item["name"]}(' + ",".join(i["type"] for i in item["inputs"]) + ')'
            selectors.add("0x" + keccak(text=sig)[:4].hex())

        if item["type"] == "event" and (
            any(k in name for k in KEYWORDS) or name in ALT_EVENT_NAMES.get("curve", set())
        ):
            sig = f'{item["name"]}(' + ",".join(i["type"] for i in item["inputs"]) + ')'
            topics.add("0x" + keccak(text=sig).hex())
    return selectors, topics


