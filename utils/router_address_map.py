

ROUTER_MAP = {
    "ethereum": {
        "dex": [
            "0x7a250d5630b4cf539739df2c5dacb4c659f2488d",  # Uniswap v2
            "0xe592427a0aece92de3edee1f18e0157c05861564",  # Uniswap v3
            "0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f",  # Sushiswap
            "0x99a58482bd75cbab83b27ec03ca68ff489b5788f",  # Curve Finance
            "0xba12222222228d8ba445958a75a0704d566bf2c8",  # Balancer
            "0x0045f933adf0607292468ad1c1dedaa74d5ad166",  # Ekubo
        ],
        "aggregators": [
            "0x1111111254EEB25477B68fb85Ed929f73A960582",  # 1Inch
            "0x84f84667dcd56091f289466a7dc0e2620b562e24",  # CoW Swap
            "0xdef1c0ded9bec7f1a1670819833240f027b25eff",  # Matcha
            "0xdef1c0ded9bec7f1a1670819833240f027b25eff",  # ParaSwap
            "0xb98325b54cB1B06C2bD6581D61A48eDbCeD95e0C",  # Bebop
        ]
    },

    "base": {
        "dex": [
            "0x6ff5693b99212da76ad316178a184ab56d299b43",  # Uniswap V3
            "0x2626664c2603336e57b271c5c0b26f421741e481",
            "0x4752ba5dbc23f44d87826276bf6fd6b1c372ad24",  # Uniswap v2
            "0x0573b0ce977bba12e31ad7a3ccc02d0b004d57a",  # Sharkswap
            "0x4f37a9d177470499a2dd084621020b023fcffc1f",  # Curve
            "0x1b81d678ffb9c0263b24a97847620c99d213eb14",  # Pancakeswap v3
            "0x13f4ea83d0bd40e75c8222255bc855a974568dd4",  # Pancakeswap v2
            "0x6cb442acf35158d5eda88fe602221b67b400be3e",  # Aerodrome


        ],
        "aggregators": [
            "0x111111125421ca6dc452d289314280a0f8842a65",  # 1inch
            "0x69460570c93f9de5e2edbc3052bf10125f0ca22d",  # Rango
        ]
    },
}


def get_all_addresses(chain: str) -> list[str]:
    return ROUTER_MAP[chain]["dex"] + ROUTER_MAP[chain]["aggregators"]




