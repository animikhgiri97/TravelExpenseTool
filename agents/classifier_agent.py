import asyncio
from random import randint
from typing import Dict, Any
from schema import Expense


CATEGORY_TO_GL = {
    "meals": "GL-5001",
    "lodging": "GL-5002",
    "transport": "GL-5003",
    "travel": "GL-5004",
    "other": "GL-5009",
}

TAX_TREATMENT = {
    "meals": "GST Deductible",
    "lodging": "GST Deductible",
    "transport": "GST Exempt",
    "travel": "GST Deductible",
    "other": "GST Standard",
}


async def classify(expense: Expense) -> Dict[str, Any]:
    """Return classification, GL code, tax treatment, and risk score."""
    await asyncio.sleep(0)
    category = expense.category.lower() if expense.category else "other"
    gl_code = CATEGORY_TO_GL.get(category, CATEGORY_TO_GL["other"])
    tax = TAX_TREATMENT.get(category, TAX_TREATMENT["other"])

    risk = 20
    if category in ("other", "travel"):
        risk += 20
    if expense.amount > 5000:
        risk += 20
    if not expense.receipt:
        risk += 30
    risk_score = min(100, max(0, risk + randint(-5, 5)))

    return {
        "gl_code": gl_code,
        "tax_treatment": tax,
        "risk_score": risk_score,
        "category": category,
    }


async def handle(message: Dict[str, Any]) -> Dict[str, Any]:
    data = message.get("expense", {})
    exp = Expense(**data)
    result = await classify(exp)
    return {"classification": result}
