# Savante (In-progess)

**Savante** is an LLM-driven trading bot that makes trades using data from Ethereum main-net. It ingests real-time 
on-chain data, combines it with machine-learning insights, and decides when to buy, sell, or hold ETH.

---

## Features

| Layer | Purpose                                                                                                                                                   |
|-------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Transaction Ingestion** | WebSocket listeners batch pending and mined transactions every 30 s and push them into FastAPI endpoints (`/api/mempool`, `/api/mined-transactions`).     |
| **Filtering** | Only swaps routed through the major **DEX routers** and **aggregator contracts** are accepted (addresses below). Duplicate transactoins hashes are removed. |
| **Bot vs Human Classification** | An XGBoost model labels each swap; synthetic human samples balance the dataset.                                                                           |
| **Weighted Wallet Scores** | Wallets that historically buy/sell before large moves gain weight in the RAG context.                                                                     |
| **Macro Predictor** | A second XGBoost model combines on-chain flows, liquidation spikes, perp funding, and TA to predict ETH movement.                                         |
| **Savante Agent** | All features are fed to an OpenAI Assistant that issues the final **buy / sell / hold** decision.                                                    |

---

## 🔗 Router Addresses

### DEX Routers

| DEX            | Version        | Address |
|----------------|----------------|------------------------------------------|
| Uniswap        | V3 SwapRouter  | `0xe592427a0aece92de3edee1f18e0157c05861564` |
|                | V2 Router      | `0x7a250d5630b4cf539739df2c5dacb4c659f2488d` |
| SushiSwap      | V2 Router      | `0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f` |
| Curve Finance  | Exchange Router | `0x99a58482bd75cbab83b27ec03ca68ff489b5788f` |
| Balancer V2    | Vault (entry)  | `0xba12222222228d8ba445958a75a0704d566bf2c8` |
| Ekubo          | V3 Router      | `0x0045f933adf0607292468ad1c1dedaa74d5ad166` |

### Aggregator Routers

| Aggregator | Address |
|------------|------------------------------------------|
| 1inch      | `0x1111111254EEB25477B68fb85Ed929f73A960582` |
| CoW Swap   | `0x84f84667dcd56091f289466a7dc0e2620b562e24` |
| Matcha     | `0xdef1c0ded9bec7f1a1670819833240f027b25eff` |
| ParaSwap   | `0xdef1c0ded9bec7f1a1670819833240f027b25eff` |
| Bebop      | `0xb98325b54cB1B06C2bD6581D61A48eDbCeD95e0C` |

> **Why aggregators matter**: when a user trades through 1inch or CoW, the
> swap settles on a DEX (e.g. Uniswap) with the aggregator contract as the
> caller, hiding the original wallet. We therefore parse aggregator calls
> separately and deduplicate by `tx_hash`.

---

## Dataset-Building Mode

Set `BUILD_DATASET=true` in `.env` to record labelled CSVs:

* **`bot_data.csv`** – high-confidence bot txs  
* **`human_data.csv`** – heuristic human txs  
* **`human_synth_data.py`** – upsamples humans to balance the classes

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/0xjuju/savante.git
cd savante

# 2. Python env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. .env
cp .env.example .env
# ─────────────────────────────────
# ALCHEMY_API_KEY = <your-key>
# DOMAIN = http://127.0.0.1:8000
# REDIS_URL = redis://localhost:6379
# SECRET_KEY_MIDDLEWARE = <run python -m app.scripts.generate_secret>
# BUILD_DATASET = false
# ─────────────────────────────────

# 4. Run API + transactoin streamers (dev)
uvicorn app.main:app --reload
