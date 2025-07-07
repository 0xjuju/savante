import asyncio

from app.services.blockchain import BlockchainParser

parser = BlockchainParser("ethereum")


if __name__ == "__main__":
    print("Mined Transactions")
    asyncio.run(parser.stream_mined_transactions(parser.ROUTERS))


