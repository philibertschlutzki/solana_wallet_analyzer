import os
import asyncio
from wallet_identification import identify_active_wallets_from_signatures
from wallet_analysis import analyze_active_wallets
import logging
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime

def setup_logger(name, log_file, level=logging.INFO):
    # Erstelle absoluten Pfad zum Log-Verzeichnis
    project_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(project_dir, 'logs', log_file)
    
    # Erstelle Log-Verzeichnis
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    # Erstelle Logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Entferne existierende Handler
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Rotating File Handler
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=1024 * 1024,  # 1MB
        backupCount=3,
        mode='a'
    )
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def write_to_log(logger, data, message):
    logger.info(message)
    logger.info(json.dumps(data, indent=2))

async def main():
    # Erstelle Timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Setup Logger
    start_logger = setup_logger('start_logger', f'process/start_process_{timestamp}.log')
    start_logger.info("Starting Solana Wallet Analysis")

    print("Identifying active wallets...")
    identified_wallets = await identify_active_wallets_from_signatures(num_signatures=10, min_transactions=1)

    identified_logger = setup_logger('identified_logger', f'wallets/identified_wallets_{timestamp}.log')
    write_to_log(identified_logger, identified_wallets, f"Found {len(identified_wallets)} active wallets")

    print(f"Found active wallets: {len(identified_wallets)}")
    print("\nAnalyzing the identified active wallets...")
    
    active_wallets, top_traders = await analyze_active_wallets(identified_wallets, time_frame_days=30)

    analyzed_logger = setup_logger('analyzed_logger', f'analysis/analyzed_wallets_{timestamp}.log')
    write_to_log(analyzed_logger, active_wallets, "Analysis Results")

    # Speichere Top Trader Informationen
    if top_traders:
        top_traders_logger = setup_logger('top_traders_logger', f'traders/top_traders_{timestamp}.log')
        write_to_log(top_traders_logger, top_traders, "Top Traders (>10% profit in 30 days)")

    print("\nAnalysis Results:")
    for wallet in active_wallets:
        print(f"Address: {wallet['address']}")
        print(f"Transactions in the last 30 days: {wallet['transaction_count']}")
        print(f"Last activity: {wallet['last_activity']}")
        print(f"Profit: {wallet['profit']:.2%}")
        print("-" * 50)

    if top_traders:
        print("\nTop Traders (>10% profit in 30 days):")
        for trader in top_traders:
            print(f"Address: {trader['address']}")
            print(f"Profit: {trader['profit']:.2%}")
            print("-" * 50)

    end_logger = setup_logger('end_logger', f'process/end_process_{timestamp}.log')
    end_logger.info("Solana Wallet Analysis completed")

if __name__ == "__main__":
    asyncio.run(main())