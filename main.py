import asyncio
from wallet_identification import identify_active_wallets_from_signatures
from wallet_analysis import analyze_active_wallets
import logging
import json
from datetime import datetime
import os

def ensure_log_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def setup_logger(name, log_file, level=logging.INFO):
    log_directory = "logs"
    ensure_log_directory(log_directory)
    log_path = os.path.join(log_directory, log_file)
    handler = logging.FileHandler(log_path)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

def write_to_log(logger, data, message):
    logger.info(message)
    logger.info(json.dumps(data, indent=2))

async def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    start_logger = setup_logger('start_logger', f'start_process_{timestamp}.log')
    start_logger.info("Starting Solana Wallet Analysis")

    print("Identifying active wallets...")
    identified_wallets = await identify_active_wallets_from_signatures(num_signatures=10, min_transactions=1)
    
    identified_logger = setup_logger('identified_logger', f'identified_wallets_{timestamp}.log')
    write_to_log(identified_logger, identified_wallets, f"Found {len(identified_wallets)} active wallets")
    
    print(f"Found active wallets: {len(identified_wallets)}")

    print("\nAnalyzing the identified active wallets...")
    active_wallets, top_traders = await analyze_active_wallets(identified_wallets, time_frame_days=30)
    
    analyzed_logger = setup_logger('analyzed_logger', f'analyzed_wallets_{timestamp}.log')
    write_to_log(analyzed_logger, active_wallets, "Analysis Results")
    
    top_traders_logger = setup_logger('top_traders_logger', f'top_traders_{timestamp}.log')
    write_to_log(top_traders_logger, top_traders, "Top Traders (>10% profit in 30 days)")

    print("\nAnalysis Results:")
    for wallet in active_wallets:
        print(f"Address: {wallet['address']}")
        print(f"Transactions in the last 30 days: {wallet['transaction_count']}")
        print(f"Last activity: {wallet['last_activity']}")
        print(f"Profit: {wallet['profit']:.2%}")
        print("-" * 50)

    print("\nTop Traders (>10% profit in 30 days):")
    for trader in top_traders:
        print(f"Address: {trader['address']}")
        print(f"Profit: {trader['profit']:.2%}")
        print("-" * 50)

    end_logger = setup_logger('end_logger', f'end_process_{timestamp}.log')
    end_logger.info("Solana Wallet Analysis completed")

if __name__ == "__main__":
    asyncio.run(main())