import asyncio
from typing import Dict, Any
from schema import Expense


async def validate(expense: Expense) -> Dict[str, Any]:
    """Return policy check results. Simple synchronous heuristics wrapped for async."""
    await asyncio.sleep(0)  # yield control
    violations = []
    rules = []

    # Example rules
    if expense.amount > 1000:
        violations.append("AMOUNT_EXCEEDS_LIMIT")
        rules.append("amount>1000")

    if expense.amount > 75 and not expense.receipt:
        violations.append("MISSING_RECEIPT")
        rules.append("receipt_required")

    blacklist = {"Shady Supplier", "Fraudulent Co"}
    if expense.merchant in blacklist:
        violations.append("MERCHANT_BLACKLISTED")
        rules.append("merchant_blacklist")

    return {"violations": violations, "rules": rules}


async def handle(message: Dict[str, Any]) -> Dict[str, Any]:
    """Broker-compatible handler. Expects message {'expense': {...}}."""
    data = message.get("expense", {})
    exp = Expense(**data)
    result = await validate(exp)
    return {"policy": result}
