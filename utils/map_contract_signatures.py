
SELECTOR_MAP: dict[str, str] = {
    # Uniswap V2 & Sushi
    "0x38ed1739": "swapExactTokensForTokens(uint256,uint256,address[],address,uint256)",
    "0x8803dbee": "swapTokensForExactTokens(uint256,uint256,address[],address,uint256)",
    "0x18cbafe5": "swapExactTokensForETH(uint256,uint256,address[],address,uint256)",
    "0x7ff36ab5": "swapExactETHForTokens(uint256,address[],address,uint256)",
    # Uniswap V3
    "0x414bf389": "exactInputSingle((address,address,uint24,address,uint256,uint256,uint160))",
    "0xb858183f": "exactInput((bytes,address,uint256,uint256))",
    "0x04e45aaf": "exactOutputSingle((address,address,uint24,address,uint256,uint256,uint160))",
    # Curve Finance
    "0x3df02124": "exchange(int128,int128,uint256,uint256)",
    "0xa6417ed6": "exchange_underlying(int128,int128,uint256,uint256)",
    "0x33e6f528": "exchange_multiple((address,address,uint256,uint256,address,address,address,uint256,uint256,bytes))",
    # Balancer V2 Vault
    "0x52bbbe29": "swap((bytes32,uint8,address,address,uint256,bytes),(address,bool,address,bool),uint256,uint256)",
    "0x945bcec9": "batchSwap(uint8,(bytes32,uint256,uint256,uint256,bytes32)[],(address,bool,address,bool),int256[],uint256)",
    # Ekubo V3
    "0x18fbbb04": "lock(address,uint256,bytes)",
    #  1inch Aggregation Router
    "0x12aa3caf": "swap(address,(address,address,address,address,uint256,uint256,uint256,uint256),bytes,bytes)",
    "0x2e95b6c8": "unoswap(address,uint256,uint256,bytes32[])",
    # CoW Swap Settlement GPv2
    "0xb9ab4396": "setPreSignature(bytes,bool)",
    "0xbaa2abde": "settle((bytes,bytes)[],(address,bool,address,bool),bytes)",
    # 0x / Matcha / ParaSwap Router
    "0x415565b0": "transformERC20(address,address,uint256,uint256,(uint32,bytes)[])",
    # Bebop Router
    "0xfe67a8e3": "swap(address,(address[],uint256[],address,uint256,uint256),bytes)",
}





