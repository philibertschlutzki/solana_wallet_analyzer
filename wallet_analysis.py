import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
import asyncio
from solana_api import SolanaRPCManager

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
    solana_rpc = SolanaRPCManager()

    try:
        for wallet_address in wallet_addresses:
            logger.debug(f"Analyzing wallet: {wallet_address}")
            
            # Abrufen der Transaktionen
            transactions_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignaturesForAddress",
                "params": [
                    wallet_address,
                    {"limit": 1000}
                ]
            }
            transactions_data = await solana_rpc.execute_rpc_call(transactions_payload)
            
            # Abrufen des aktuellen Kontostands
            balance_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [wallet_address]
            }
            balance_data = await solana_rpc.execute_rpc_call(balance_payload)
            
            if transactions_data and 'result' in transactions_data:
                logger.debug(f"Received transaction data for {wallet_address}")
                recent_transactions = [tx for tx in transactions_data['result'] if 'blockTime' in tx and datetime.fromtimestamp(tx['blockTime']) > time_threshold]
                
                if recent_transactions:
                    if balance_data and 'result' in balance_data:
                        current_balance = balance_data['result']['value'] / 1e9  # Konvertierung von Lamports zu SOL
                        oldest_transaction = min(recent_transactions, key=lambda tx: tx['blockTime'])
                        
                        # Abrufen des Kontostands vor 30 Tagen
                        historical_balance_payload = {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "getBalanceAndContext",
                            "params": [wallet_address, {"slot": oldest_transaction['slot']}]
                        }
                        historical_balance_data = await solana_rpc.execute_rpc_call(historical_balance_payload)
                        
                        if historical_balance_data and 'result' in historical_balance_data:
                            balance_30d_ago = historical_balance_data['result']['value'] / 1e9
                            balance_change_30d = current_balance - balance_30d_ago
                            profit = (balance_change_30d / balance_30d_ago) if balance_30d_ago > 0 else 0

                            wallet_info = {
                                "address": wallet_address,
                                "transaction_count": len(recent_transactions),
                                "last_activity": datetime.fromtimestamp(recent_transactions[0]['blockTime']).strftime("%Y-%m-%d %H:%M:%S"),
                                "profit": profit,
                                "current_balance": current_balance,
                                "balance_30d_ago": balance_30d_ago,
                                "balance_change_30d": balance_change_30d
                            }

                            active_wallets.append(wallet_info)
                            if profit > 0.1:  # Mehr als 10% Gewinn
                                top_traders.append(wallet_info)

                            logger.debug(f"Wallet {wallet_address} analyzed. Profit: {profit:.2%}, Balance Change: {balance_change_30d}, Balance 30d ago: {balance_30d_ago}")
                        else:
                            logger.warning(f"Failed to retrieve historical balance for {wallet_address}")
                    else:
                        logger.warning(f"Failed to retrieve current balance for {wallet_address}")
                else:
                    logger.debug(f"No recent transactions found for {wallet_address}")
            else:
                logger.warning(f"Failed to retrieve transaction data for {wallet_address}")

            await asyncio.sleep(1)  # Erhöhte Verzögerung zwischen Anfragen

        logger.info(f"Analysis complete. Found {len(top_traders)} top traders")
        return active_wallets, top_traders

    except Exception as e:
        logger.error(f"Unexpected error during wallet analysis: {str(e)}", exc_info=True)
        return [], []