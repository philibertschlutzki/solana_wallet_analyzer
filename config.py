import os
from dotenv import load_dotenv

# Lade Umgebungsvariablen aus .env Datei
load_dotenv()

# API Konfiguration
API_URL = os.getenv('API_URL', 'https://api.mainnet-beta.solana.com')
API_KEY = os.getenv('API_KEY', '')

# Analyse Parameter
TIME_FRAME_DAYS = int(os.getenv('TIME_FRAME_DAYS', 30))
MIN_TRANSACTIONS = int(os.getenv('MIN_TRANSACTIONS', 1))
NUM_SIGNATURES = int(os.getenv('NUM_SIGNATURES', 10))
TOP_TRADER_THRESHOLD = float(os.getenv('TOP_TRADER_THRESHOLD', 0.1))

# Logging Konfiguration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(levelname)s - %(message)s')

# Rate Limiting
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 5))
INITIAL_DELAY = float(os.getenv('INITIAL_DELAY', 1.0))

# Weitere Konfigurationsoptionen können hier hinzugefügt werden