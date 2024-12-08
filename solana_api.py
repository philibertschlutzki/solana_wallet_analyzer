import aiohttp
import logging
from logging.handlers import RotatingFileHandler
import os
import asyncio
from typing import List, Optional, Dict, Any
import json

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

    def get_next_rpc(self) -> str:
        self.current_rpc_index = (self.current_rpc_index + 1) % len(self.rpc_endpoints)
        return self.rpc_endpoints[self.current_rpc_index]

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

async def fetch_recent_signatures(limit: int = 50) -> List[str]:
    rpc_manager = SolanaRPCManager()
    rpc_manager.logger.debug(f"Fetching {limit} recent signatures")
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": ["Vote111111111111111111111111111111111111111", {"limit": limit}]
    }
    
    data = await rpc_manager.execute_rpc_call(payload)
    if data and 'result' in data:
        signatures = [sig['signature'] for sig in data['result']]
        rpc_manager.logger.debug(f"Retrieved {len(signatures)} signatures")
        return signatures
    return []

async def fetch_transaction_details(signature: str) -> Optional[Dict]:
    rpc_manager = SolanaRPCManager()
    rpc_manager.logger.debug(f"Fetching transaction details for signature {signature}")
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [signature, {"encoding": "json", "maxSupportedTransactionVersion": 0}]
    }
    
    data = await rpc_manager.execute_rpc_call(payload)
    return data.get('result') if data else None

async def fetch_wallet_data(wallet_address: str) -> Optional[Dict]:
    rpc_manager = SolanaRPCManager()
    rpc_manager.logger.debug(f"Fetching data for wallet {wallet_address}")
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [wallet_address, {"limit": 1000}]
    }
    
    data = await rpc_manager.execute_rpc_call(payload)
    if data and 'result' in data:
        rpc_manager.logger.debug(f"Retrieved {len(data['result'])} signatures for wallet {wallet_address}")
        return data
    return None

async def fetch_wallet_balance(wallet_address: str) -> Optional[int]:
    rpc_manager = SolanaRPCManager()
    rpc_manager.logger.debug(f"Fetching balance for wallet {wallet_address}")
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBalance",
        "params": [wallet_address]
    }
    
    data = await rpc_manager.execute_rpc_call(payload)
    if data and 'result' in data:
        rpc_manager.logger.debug(f"Retrieved balance for wallet {wallet_address}")
        return data['result']['value']
    return None