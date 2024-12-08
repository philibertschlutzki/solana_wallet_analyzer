# wallet.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Wallet:
    address: str
    transaction_count: int
    last_activity: Optional[datetime]
    profit: float