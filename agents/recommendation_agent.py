import asyncio
from typing import Dict, Any
from schema import Expense


async def recommend(expense: Expense) -> Dict[str, Any]:
    """Return approval recommendation based on policy and classification."""
    await asyncio.sleep(0)
    policy = expense.metadata.get("policy", {})
    classification = expense.metadata.get("classification", {})

    violations = policy.get("violations", [])
    category = classification.get("category", "other")

    # Simple decision rules
    if "MERCHANT_BLACKLISTED" in violations:
        decision = "deny"
        reason = "blacklisted_merchant"
    elif "AMOUNT_EXCEEDS_LIMIT" in violations:
        decision = "escalate"
        reason = "amount_over_limit"
    elif "MISSING_RECEIPT" in violations and expense.amount > 75:
        decision = "escalate"
        reason = "missing_receipt"
    else:
        decision = "approve"
        reason = "ok"

    # Category-based advisory
    advisory = f"category:{category}"

    return {"decision": decision, "reason": reason, "advisory": advisory}


async def handle(message: Dict[str, Any]) -> Dict[str, Any]:
    data = message.get("expense", {})
    metadata = message.get("metadata", {})
    exp = Expense(**data)
    exp.metadata = metadata
    result = await recommend(exp)
    return {"recommendation": result}
