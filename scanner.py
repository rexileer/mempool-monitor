"""
Mempool Monitor — сканер транзакций в мемпуле Ethereum.
Подписывается на alchemy_mempool и фильтрует свопы Uniswap V2/V3.
"""
import asyncio
import json
import os
from dotenv import load_dotenv
import websockets

from config import (
    UNISWAP_V2_ROUTER,
    UNISWAP_V3_ROUTER,
    UNISWAP_V3_ROUTER_02,
    SWAP_SELECTORS,
    BIG_SWAP_THRESHOLD_ETH,
)

load_dotenv()

ALCHEMY_WS = os.getenv("ALCHEMY_WS_URL")
if not ALCHEMY_WS:
    print("⚠️  Задай ALCHEMY_WS_URL в .env (скопируй из .env.example)")
    exit(1)

DEBUG = os.getenv("DEBUG", "").lower() in ("1", "true", "yes")

# Целевые роутеры (должны совпадать с toAddress в подписке)
TARGET_ROUTERS = {UNISWAP_V2_ROUTER, UNISWAP_V3_ROUTER, UNISWAP_V3_ROUTER_02}


def wei_to_eth(wei_hex: str) -> float:
    """Преобразует value из wei (hex) в ETH."""
    if not wei_hex or wei_hex == "0x":
        return 0.0
    wei = int(wei_hex, 16)
    return wei / 10**18


def is_uniswap_swap(tx: dict) -> bool:
    """Проверяет, идёт ли транзакция на Uniswap роутер и вызывает swap."""
    to_addr = (tx.get("to") or "").lower()
    if to_addr not in TARGET_ROUTERS:
        return False

    data = tx.get("input", "0x")
    if len(data) < 10:
        return False

    selector = data[:10].lower()
    return selector in {s.lower() for s in SWAP_SELECTORS}


def format_tx_log(tx: dict, value_eth: float) -> str:
    """Форматирует лог по транзакции."""
    h = tx.get("hash", "?")[:18] + "..."
    sender = (tx.get("from") or "?")[:10] + "..."
    to = (tx.get("to") or "?")[-8:]
    return f"🔄 Swap | {value_eth:.2f} ETH | from {sender} → ...{to} | tx {h}"


async def send_telegram_alert(text: str) -> None:
    """Отправляет сообщение в Telegram (если настроен)."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return

    try:
        import aiohttp
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        async with aiohttp.ClientSession() as session:
            await session.post(url, json={"chat_id": chat_id, "text": text})
    except Exception as e:
        print(f"Telegram error: {e}")


async def run_scanner_session(ws):
    """Одна сессия: подписка + обработка сообщений."""
    # Фильтр toAddress — только транзакции К Uniswap роутерам (иначе может не слать или слать всё подряд)
    subscribe_payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "eth_subscribe",
        "params": [
            "alchemy_pendingTransactions",
            {"toAddress": list(TARGET_ROUTERS), "hashesOnly": False},
        ],
    }
    await ws.send(json.dumps(subscribe_payload))

    while True:
        msg = await ws.recv()
        try:
            data = json.loads(msg)
        except json.JSONDecodeError:
            continue

        if "result" in data and isinstance(data["result"], str):
            print(f"✅ Подписка активна: subscription_id={data['result'][:16]}...")
            continue

        if "params" not in data:
            if DEBUG:
                print("[DEBUG] Пропуск: нет params", list(data.keys()))
            continue

        params = data["params"]
        result = params.get("result")
        if result is None:
            if DEBUG:
                print("[DEBUG] result пустой", params.keys())
            continue

        # Одна транзакция = один объект; иногда массив
        txs = [result] if isinstance(result, dict) else (result if isinstance(result, list) else [])
        if not txs:
            continue

        if DEBUG and txs:
            print(f"[DEBUG] Получено {len(txs)} tx, to={txs[0].get('to','?')[:18]}...")

        for tx in txs:
            if not is_uniswap_swap(tx):
                if DEBUG:
                    sel = (tx.get("input") or "0x")[:10]
                    print(f"[DEBUG] Не своп: to={tx.get('to','?')} selector={sel}")
                continue

            value_eth = wei_to_eth(tx.get("value", "0x"))
            log_line = format_tx_log(tx, value_eth)
            print(log_line)

            if value_eth >= BIG_SWAP_THRESHOLD_ETH:
                alert = f"🚨 Крупный своп: {value_eth:.1f} ETH (~{value_eth * 2000:.0f}$)\n{log_line}"
                await send_telegram_alert(alert)


async def mempool_scanner():
    """Главный цикл: подключение, переподключение при обрыве."""
    # Маскируем API ключ в логах
    masked_url = ALCHEMY_WS.split("/v2/")[0] + "/v2/***" if "/v2/" in ALCHEMY_WS else "wss://***"
    print("🚀 Mempool Monitor запущен")
    print(f"   Подписываюсь на {masked_url}...")
    print("   Фильтр: Uniswap V2/V3 свопы\n")

    retry_delay = 5

    while True:
        try:
            # Отключаем ping — Alchemy может не отвечать на pings, из-за чего падает соединение
            async with websockets.connect(
                ALCHEMY_WS,
                ping_interval=None,
                ping_timeout=None,
                close_timeout=10,
                max_size=2**20,
            ) as ws:
                await run_scanner_session(ws)

        except websockets.ConnectionClosed as e:
            print(f"⚠️  Соединение закрыто: {e.reason or e.code}. Переподключение через {retry_delay} сек...")
        except Exception as e:
            print(f"⚠️  Ошибка: {e}. Переподключение через {retry_delay} сек...")

        await asyncio.sleep(retry_delay)


if __name__ == "__main__":
    asyncio.run(mempool_scanner())
