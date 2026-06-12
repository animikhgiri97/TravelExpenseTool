from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class Expense:
    employee_id: str
    amount: float
    currency: str = "INR"
    merchant: str = ""
    description: str = ""
    category: str = ""
    # travel-specific fields
    departure_city: str = ""
    arrival_city: str = ""
    role: str = ""
    business_purpose: str = ""
    employee_base: str = ""
    receipt: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    previous_submissions: List[Dict[str, Any]] = field(default_factory=list)
