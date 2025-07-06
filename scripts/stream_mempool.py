import asyncio

from app.services.blockchain import BlockchainParser

parser = BlockchainParser("ethereum")


if __name__ == "__main__":
    asyncio.run(parser.stream_mempool(parser.ROUTERS))


