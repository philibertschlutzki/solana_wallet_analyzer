import aiohttp
import logging
from logging.handlers import RotatingFileHandler
import os
import asyncio
from typing import Dict, Any, Optional

class SolanaRPCManager:
    def __init__(self):
        self.rpc_endpoints = [
            "https://api.mainnet-beta.solana.com",
            "https://solana-api.projectserum.com",
            "https://rpc.ankr.com/solana",
            "https://mainnet.rpcpool.com",
            "https://solana-mainnet.rpc.extrnode.com"
        ]
        self.current_rpc_index = 0
        self.retry_count = 0
        self.max_retries = 3
        self.setup_logger()

    def setup_logger(self):
        project_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(project_dir, 'logs', 'api', 'solana_api.log')
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        self.logger = logging.getLogger('solana_api')
        if not self.logger.handlers:
            handler = RotatingFileHandler(
                log_path,
                maxBytes=1024 * 1024,
                backupCount=3,
                mode='a'
            )
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    async def execute_rpc_call(self, payload: Dict[str, Any]) -> Optional[Dict]:
        while self.retry_count < self.max_retries * len(self.rpc_endpoints):
            current_endpoint = self.rpc_endpoints[self.current_rpc_index]
            headers = {"Content-Type": "application/json"}
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(current_endpoint, json=payload, headers=headers) as response:
                        data = await response.json()
                        if 'error' in data and ('rate limit' in str(data['error']).lower() or
                                                'too many requests' in str(data['error']).lower()):
                            self.logger.warning(f"Rate limit reached for {current_endpoint}, switching RPC...")
                            self.current_rpc_index = (self.current_rpc_index + 1) % len(self.rpc_endpoints)
                            self.retry_count += 1
                            await asyncio.sleep(1)
                            continue
                        return data
            except Exception as e:
                self.logger.error(f"Error with RPC {current_endpoint}: {str(e)}")
                self.current_rpc_index = (self.current_rpc_index + 1) % len(self.rpc_endpoints)
                self.retry_count += 1
                await asyncio.sleep(1)
        self.logger.error("All RPC endpoints exhausted")
        return None

class SolscanAPIManager:
    def __init__(self):
        self.base_url = "https://pro-api.solscan.io"
        self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MzM2ODc2MjExMjMsImVtYWlsIjoic3ByYXkta2xlaWRlcjB5QGljbG91ZC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJhcGlWZXJzaW9uIjoidjIiLCJpYXQiOjE3MzM2ODc2MjF9.Ehi-NUuiHCpPegfMxFTthdTKz9pjYk7Jr8L7ShEgCg0"
        self.headers = {
            "Content-Type": "application/json",
            "token": self.api_key
        }

    async def fetch_account_transactions(self, address: str, limit: int = 50, before: str = ""):
        endpoint = f"{self.base_url}/v2.0/account/transactions"
        params = {"account": address, "limit": limit}
        if before:
            params["before"] = before
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=params, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Error: Status {response.status}, {await response.text()}")
                        return None
        except Exception as e:
            print(f"Error fetching transactions: {str(e)}")
            return None

    async def fetch_account_tokens(self, address: str):
        endpoint = f"{self.base_url}/v2.0/account/token-accounts"
        params = {"account": address}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=params, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Error: Status {response.status}, {await response.text()}")
                        return None
        except Exception as e:
            print(f"Error fetching account tokens: {str(e)}")
            return None

async def fetch_recent_signatures(num_signatures=10):
    solana_rpc = SolanaRPCManager()
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [
            "Vote111111111111111111111111111111111111111",
            {"limit": num_signatures}
        ]
    }
    response = await solana_rpc.execute_rpc_call(payload)
    if response and 'result' in response:
        return [tx['signature'] for tx in response['result']]
    return []

async def fetch_transaction_details(signature: str):
    solana_rpc = SolanaRPCManager()
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            signature,
            {"encoding": "json", "maxSupportedTransactionVersion": 0}
        ]
    }
    response = await solana_rpc.execute_rpc_call(payload)
    if response and 'result' in response:
        return response['result']
    return None

async def test_api_connection():
    test_address = "Vote111111111111111111111111111111111111111"
    solscan_api = SolscanAPIManager()
    try:
        transactions_data = await solscan_api.fetch_account_transactions(test_address, limit=1)
        if transactions_data and 'data' in transactions_data:
            print("API-Verbindung erfolgreich!")
            return True
        else:
            print("API-Antwort ungültig.")
            return False
    except Exception as e:
        print(f"Fehler bei API-Verbindung: {str(e)}")
        return False

__all__ = ['SolanaRPCManager', 'SolscanAPIManager', 'fetch_recent_signatures', 'fetch_transaction_details', 'test_api_connection']