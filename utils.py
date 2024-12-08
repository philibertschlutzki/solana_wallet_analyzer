import requests
import json
import time
import logging
import random
from datetime import datetime, timedelta

logging.basicConfig(filename='solana_wallet_analysis.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_with_retry(url, headers, payload, max_retries=5, initial_delay=1):
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                delay = initial_delay * (2 ** attempt) + random.uniform(0, 1)
                logging.warning(f"Rate limit hit. Retrying in {delay:.2f} seconds.")
                time.sleep(delay)
            else:
                logging.error(f"Request failed with status code: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error: {e}")
    logging.error("Max retries reached. Giving up.")
    return None

def calculate_profit(transactions):
    logging.info(f"Calculating profit for {len(transactions)} transactions")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    recent_transactions = [tx for tx in transactions if 'blockTime' in tx and start_date <= datetime.fromtimestamp(tx['blockTime']) <= end_date]
    
    total_in = 0
    total_out = 0
    for tx in recent_transactions:
        if 'postBalances' in tx and 'preBalances' in tx:
            balance_change = tx['postBalances'][0] - tx['preBalances'][0]
            if balance_change > 0:
                total_in += balance_change
            else:
                total_out += abs(balance_change)
    
    profit = (total_in - total_out) / max(total_out, 1)
    logging.info(f"Calculated profit: {profit:.2%}")
    return profit