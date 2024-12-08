from solana_api import fetch_recent_signatures, fetch_transaction_details
import logging
import asyncio
import json
from datetime import datetime

async def identify_active_wallets_from_signatures(num_signatures=10, min_transactions=1):
    logging.info(f"Identifying active wallets from {num_signatures} recent signatures")
    signatures = await fetch_recent_signatures(num_signatures)
    active_wallets = {}

    async def process_signature(signature):
        tx_details = await fetch_transaction_details(signature)
        if tx_details and 'transaction' in tx_details and 'message' in tx_details['transaction']:
            account_keys = tx_details['transaction']['message']['accountKeys']
            for account in account_keys:
                if isinstance(account, str):
                    wallet_address = account
                elif isinstance(account, dict) and 'pubkey' in account:
                    wallet_address = account['pubkey']
                else:
                    logging.warning(f"Unexpected account format in transaction {signature}")
                    continue
                
                if wallet_address not in active_wallets:
                    active_wallets[wallet_address] = 1
                else:
                    active_wallets[wallet_address] += 1

    await asyncio.gather(*[process_signature(sig) for sig in signatures])

    identified_wallets = [wallet for wallet, count in active_wallets.items() if count >= min_transactions]
    logging.info(f"Identified {len(identified_wallets)} active wallets")

    # Speichere die identifizierten Wallets in einer Datei
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"identified_wallets_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(identified_wallets[:10], f, indent=2)
    logging.info(f"Saved identified wallets to {filename}")

    return identified_wallets[:10]  # Nur die ersten 10 Wallets zurückgeben

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    asyncio.run(identify_active_wallets_from_signatures())