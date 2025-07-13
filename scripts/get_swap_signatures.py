from app.services.chain_explorer import swap_selectors


if __name__ == "__main__":

    pools = [
        {"chain": "ethereum", "address": "0x5b45b414c6cd2a3341be70ba22be786b0124003f", "dex": "Euler"},
        {"chain": "ethereum", "address": "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8", "dex": "Uniswap v3"},
        {"chain": "ethereum", "address": "0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc", "dex": "Uniswap v2"},
        {"chain": "ethereum", "address": "0x397ff1542f962076d0bfe58ea045ffa2d347aca0", "dex": "Sushiswap v2"},
        {"chain": "ethereum", "address": "0x4f493B7dE8aAC7d55F71853688b1F7C8F0243C85", "dex": "Curve"},
        {"chain": "ethereum", "address": "0xebc5028d2a6080d0455348e352b16c58e1771fdf", "dex": "Balancer"},
        {"chain": "base", "address": "0xd0b53d9277642d899df5c87a3966a349a798f224", "dex": "Uniswap v3"},
        {"chain": "base", "address": "0x88a43bbdf9d098eec7bceda4e2494615dfd9bb9c", "dex": "Uniswap v2"},
        {"chain": "base", "address": "0xaE45F7Eb428Eb6403F2567C3A3eC47E9230Bc823", "dex": "sharkswap"},
    ]

    for pool in pools:
        chain = pool["chain"]
        address = pool["address"]
        dex = pool["dex"]
        res = swap_selectors(address=address, chain=chain)
        print(f"{chain} | {dex}")
        print(res)
        print("_____________________________")










