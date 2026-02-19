"""
Адреса контрактов Uniswap V2/V3 — сюда идут свопы.
Полный список: https://docs.uniswap.org/contracts/v2/reference/smart-contracts
"""
UNISWAP_V2_ROUTER = "0x7a250d5630b4cf539739df2c5dacb4c659f2488d".lower()
UNISWAP_V3_ROUTER = "0xe592427a0aece92de3edee1f18e0157c05861564".lower()
UNISWAP_V3_ROUTER_02 = "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45".lower()

# Селекторы swap: Uniswap V2 + V3
SWAP_SELECTORS = {
    # Uniswap V2
    "0x7ff36ab5",  # swapExactETHForTokens
    "0x18cbafe5",  # swapExactTokensForETH
    "0x38ed1739",  # swapExactTokensForTokens
    "0x8803dbee",  # swapTokensForExactTokens
    "0xfb3bdb41",  # swapETHForExactTokens
    "0x4a25d94a",  # swapTokensForExactETH
    "0x5c11d795",  # swapExactTokensForTokensSupportingFeeOnTransferTokens
    "0x791ac947",  # swapExactTokensForETHSupportingFeeOnTransferTokens
    "0xb6f9de95",  # swapExactETHForTokensSupportingFeeOnTransferTokens
    "0x42712a67",  # multicall
    # Uniswap V3
    "0x04e45aaf",  # exactInputSingle
    "0x414bf389",  # exactInputSingle((address,address,uint24,...))
    "0xb858183f",  # exactInput
    "0xc04b8d59",  # exactInput((bytes,...)) — Uniswap V3
    "0x5023b4df",  # exactOutputSingle
    "0x09b81346",  # exactOutput
    "0xac9650d8",  # multicall (V3)
    # Прочие (addLiquidity и т.п. — показываем как активность DEX)
    "0xf305d719",  # addLiquidityETH
}

# Порог для "крупного" свопа в ETH (для алертов)
BIG_SWAP_THRESHOLD_ETH = 50.0  # ~50 ETH ≈ 100k$ при ETH ~2000
