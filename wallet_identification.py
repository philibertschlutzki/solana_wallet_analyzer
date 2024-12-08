import os
import logging
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime
from solana_api import fetch_recent_signatures, fetch_transaction_details
import asyncio

def get_logger():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(project_dir, 'logs', 'wallets', 'wallet_identification.log')
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    logger = logging.getLogger('wallet_identification')
    if not logger.handlers:
        handler = RotatingFileHandler(
            log_path,
            maxBytes=1024 * 1024,  # 1MB
            backupCount=3,
            mode='a'
        )
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

async def identify_active_wallets_from_signatures(num_signatures=10, min_transactions=1):
    logger = get_logger()
    logger.info(f"Identifying active wallets from {num_signatures} recent signatures")
    
    signatures = await fetch_recent_signatures(num_signatures)
    active_wallets = {}
    
    for signature in signatures:
        tx_details = await fetch_transaction_details(signature)
        if tx_details and 'transaction' in tx_details and 'message' in tx_details['transaction']:
            account_keys = tx_details['transaction']['message']['accountKeys']
            for account in account_keys:
                if isinstance(account, str):
                    wallet_address = account
                elif isinstance(account, dict) and 'pubkey' in account:
                    wallet_address = account['pubkey']
                else:
                    logger.warning(f"Unexpected account format in transaction {signature}")
                    continue
                
                if wallet_address not in active_wallets:
                    active_wallets[wallet_address] = 1
                else:
                    active_wallets[wallet_address] += 1
        
        await asyncio.sleep(0.2)
    
    identified_wallets = [wallet for wallet, count in active_wallets.items() if count >= min_transactions]
    logger.info(f"Identified {len(identified_wallets)} active wallets")
    
    # Speichere die identifizierten Wallets in einer Datei
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(project_dir, 'logs', 'wallets', f'identified_wallets_{timestamp}.json')
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w') as f:
        json.dump(identified_wallets[:10], f, indent=2)
    logger.info(f"Saved identified wallets to {filename}")
    
    return identified_wallets[:10]

if __name__ == "__main__":
    asyncio.run(identify_active_wallets_from_signatures())