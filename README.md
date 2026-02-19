# Mempool Monitor

Real-time Ethereum mempool scanner for Uniswap V2/V3 swap transactions. Subscribes to Alchemy WebSocket and filters DEX activity.
<img width="698" height="428" alt="image" src="https://github.com/user-attachments/assets/0a7ef723-5fa4-4178-b956-714f7209b20d" />

## Features

- **WebSocket stream** — `alchemy_pendingTransactions` via Alchemy
- **Uniswap V2/V3** — filters swaps on main routers
- **Auto-reconnect** — handles connection drops
- **Telegram alerts** — optional notifications for large swaps (>50 ETH)
- **Low latency** — see transactions before they land in a block

## Quick Start

1. **Get Alchemy API key**  
   [Alchemy Dashboard](https://dashboard.alchemy.com/) → create app → copy WebSocket URL.

2. **Configure**
   ```bash
   cp .env.example .env
   # Edit .env: ALCHEMY_WS_URL=wss://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
   ```

3. **Run**
   ```bash
   # With uv (recommended)
   uv venv && uv pip install -e .
   uv run python scanner.py

   # Or with pip
   pip install -r requirements.txt
   python scanner.py
   ```

## Output

```
🚀 Mempool Monitor запущен
   Подписываюсь на wss://eth-mainnet.g.alchemy.com/v2/***...
   Фильтр: Uniswap V2/V3 свопы

✅ Подписка активна: subscription_id=0x...
🔄 Swap | 0.11 ETH | from 0x142239af... → ...59f2488d | tx 0x28afb7d8...
🔄 Swap | 0.00 ETH | from 0x9be6e683... → ...59f2488d | tx 0x3e83761b...
```

View any tx on [Etherscan](https://etherscan.io/tx/0x...).

## Supported Selectors

- **Uniswap V2**: swapExactETHForTokens, swapExactTokensForETH, swapExactTokensForTokens, addLiquidityETH, multicall, etc.
- **Uniswap V3**: exactInputSingle, exactInput, exactOutput, multicall

## Telegram (optional)

1. Create bot via [@BotFather](https://t.me/BotFather)
2. Get chat_id from [@userinfobot](https://t.me/userinfobot)
3. Add to `.env`: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
4. Alerts fire for swaps ≥ 50 ETH

## Debug mode

```bash
# PowerShell (Windows)
$env:DEBUG="1"; python scanner.py

# Bash
DEBUG=1 python scanner.py
```

## Project structure

```
mempool-monitor/
├── config.py       # Router addresses, swap selectors
├── scanner.py      # WebSocket subscription + filter
├── pyproject.toml  # Dependencies
├── requirements.txt
├── .env.example
└── README.md
```

## Requirements

- Python 3.10+
- Alchemy account (free tier works)

## License

MIT
