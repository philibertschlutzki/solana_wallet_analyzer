from solana_api import fetch_wallet_data, fetch_wallet_balance
from utils import calculate_profit
from datetime import datetime, timedelta
import logging
import asyncio

async def analyze_active_wallets(wallet_addresses, time_frame_days=30):
    logging.info(f"Analyzing {len(wallet_addresses)} wallets in the last {time_frame_days} days")
    active_wallets = []
    top_traders = []
    current_time = datetime.now()
    time_threshold = current_time - timedelta(days=time_frame_days)

    for wallet_address in wallet_addresses:
        data = await fetch_wallet_data(wallet_address)
        if data and 'result' in data:
            recent_transactions = [tx for tx in data['result'] if 'blockTime' in tx and datetime.fromtimestamp(tx['blockTime']) > time_threshold]
            profit = calculate_profit(recent_transactions)
            
            current_balance = await fetch_wallet_balance(wallet_address)
            
            balance_change = 0
            for tx in recent_transactions:
                if 'postBalances' in tx and 'preBalances' in tx and len(tx['postBalances']) > 0 and len(tx['preBalances']) > 0:
                    balance_change += tx['postBalances'][0] - tx['preBalances'][0]
            
            wallet_info = {
                "address": wallet_address,
                "transaction_count": len(recent_transactions),
                "last_activity": datetime.fromtimestamp(recent_transactions[0]['blockTime']).strftime("%Y-%m-%d %H:%M:%S") if recent_transactions else "N/A",
                "profit": profit,
                "current_balance": current_balance,
                "balance_change_30d": balance_change
            }
            
            active_wallets.append(wallet_info)
            if profit > 0.1:  # Mehr als 10% Gewinn
                top_traders.append(wallet_info)
            
            logging.debug(f"Wallet {wallet_address} analyzed. Profit: {profit:.2%}, Current Balance: {current_balance}, Balance Change (30d): {balance_change}")
        
        await asyncio.sleep(0.2)  # Rate limiting

    logging.info(f"Analysis complete. Found {len(top_traders)} top traders")
    return active_wallets, top_traders