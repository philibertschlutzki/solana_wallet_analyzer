import aiohttp
import asyncio
import logging

async def fetch_with_retry(url, headers, payload, max_retries=3):
    async with aiohttp.ClientSession() as session:
        for attempt in range(max_retries):
            try:
                async with session.post(url, headers=headers, json=payload) as response:
                    return await response.json()
            except aiohttp.ClientError as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponentielles Backoff

async def fetch_recent_signatures(limit=50):
    logging.debug(f"Fetching {limit} recent signatures")
    url = "https://api.mainnet-beta.solana.com"
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": ["Vote111111111111111111111111111111111111111", {"limit": limit}]
    }

    data = await fetch_with_retry(url, headers, payload)
    if data and 'result' in data:
        signatures = [sig['signature'] for sig in data['result']]
        logging.debug(f"Retrieved {len(signatures)} signatures")
        return signatures
    return []

async def fetch_transaction_details(signature):
    logging.debug(f"Fetching transaction details for signature {signature}")
    url = "https://api.mainnet-beta.solana.com"
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [signature, {"encoding": "json", "maxSupportedTransactionVersion": 0}]
    }

    data = await fetch_with_retry(url, headers, payload)
    if data and 'result' in data:
        return data['result']
    return None

async def fetch_wallet_data(wallet_address):
    logging.debug(f"Fetching data for wallet {wallet_address}")
    url = "https://api.mainnet-beta.solana.com"
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [
            wallet_address,
            {"limit": 1000}
        ]
    }

    data = await fetch_with_retry(url, headers, payload)
    if data and 'result' in data:
        logging.debug(f"Retrieved {len(data['result'])} signatures for wallet {wallet_address}")
        return data
    return None

async def fetch_wallet_balance(wallet_address):
    logging.debug(f"Fetching balance for wallet {wallet_address}")
    url = "https://api.mainnet-beta.solana.com"
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBalance",
        "params": [wallet_address]
    }
    
    data = await fetch_with_retry(url, headers, payload)
    if data and 'result' in data:
        balance = data['result']['value'] / 1e9  # Convert lamports to SOL
        logging.debug(f"Balance for wallet {wallet_address}: {balance} SOL")
        return balance
    return None