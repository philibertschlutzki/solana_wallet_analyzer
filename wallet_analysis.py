import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
import asyncio
from solana_api import fetch_wallet_data, fetch_wallet_balance

def get_logger():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(project_dir, 'logs', 'analysis', 'wallet_analysis.log')
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    logger = logging.getLogger('wallet_analysis')
    if not logger.handlers:
        handler = RotatingFileHandler(
            log_path,
            maxBytes=1024 * 1024,
            backupCount=3,
            mode='a'
        )
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

async def analyze_active_wallets(wallet_addresses, time_frame_days=30):
    logger = get_logger()
    logger.info(f"Analyzing {len(wallet_addresses)} wallets in the last {time_frame_days} days")
    
    active_wallets = []
    top_traders = []
    current_time = datetime.now()
    time_threshold = current_time - timedelta(days=time_frame_days)

    try:
        for wallet_address in wallet_addresses:
            data = await fetch_wallet_data(wallet_address)
            if data and 'result' in data:
                recent_transactions = [tx for tx in data['result'] if 'blockTime' in tx and datetime.fromtimestamp(tx['blockTime']) > time_threshold]
                
                if recent_transactions:
                    current_balance = await fetch_wallet_balance(wallet_address)
                    
                    # Sicherere Berechnung der Bilanzänderung
                    balance_change = 0
                    for tx in recent_transactions:
                        if 'postBalances' in tx and 'preBalances' in tx and len(tx['postBalances']) > 0 and len(tx['preBalances']) > 0:
                            balance_change += tx['postBalances'][0] - tx['preBalances'][0]
                    
                    initial_balance = current_balance - balance_change if current_balance is not None else 0
                    profit = (balance_change / initial_balance) if initial_balance > 0 else 0

                    wallet_info = {
                        "address": wallet_address,
                        "transaction_count": len(recent_transactions),
                        "last_activity": datetime.fromtimestamp(recent_transactions[0]['blockTime']).strftime("%Y-%m-%d %H:%M:%S"),
                        "profit": profit,
                        "current_balance": current_balance,
                        "balance_change_30d": balance_change
                    }

                    active_wallets.append(wallet_info)
                    if profit > 0.1:  # Mehr als 10% Gewinn
                        top_traders.append(wallet_info)

                    logger.debug(f"Wallet {wallet_address} analyzed. Profit: {profit:.2%}")
                    
            await asyncio.sleep(0.2)
            
        logger.info(f"Analysis complete. Found {len(top_traders)} top traders")
        return active_wallets, top_traders
        
    except Exception as e:
        logger.error(f"Error during wallet analysis: {str(e)}")
        return [], []  # Leere Listen zurückgeben im Fehlerfall