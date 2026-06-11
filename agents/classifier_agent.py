import asyncio
from typing import Dict, Any
from schema import Expense


async def classify(expense: Expense) -> Dict[str, Any]:
    """Return a simple classification for the expense."""
    await asyncio.sleep(0)
    text = (expense.merchant + " " + expense.description).lower()
    if any(k in text for k in ("hotel", "airbnb", "inn", "lodging")):
        category = "lodging"
    elif any(k in text for k in ("uber", "taxi", "lyft", "transport")):
        category = "transport"
    elif any(k in text for k in ("meal", "dinner", "lunch", "breakfast", "restaurant")):
        category = "meals"
    elif any(k in text for k in ("train", "flight", "airline", "ticket")):
        category = "travel"
    else:
        category = "other"

    confidence = 0.8
    return {"category": category, "confidence": confidence}


async def handle(message: Dict[str, Any]) -> Dict[str, Any]:
    data = message.get("expense", {})
    exp = Expense(**data)
    result = await classify(exp)
    return {"classification": result}
