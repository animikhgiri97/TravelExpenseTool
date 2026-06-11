from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class Expense:
    id: str
    amount: float
    currency: str = "USD"
    merchant: str = ""
    description: str = ""
    receipt: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
