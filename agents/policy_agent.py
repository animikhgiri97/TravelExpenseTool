import asyncio
from typing import Dict, Any
from schema import Expense


PER_DIEM = {
    "meals": 1500,
    "lodging": 4000,
    "transport": 2000,
    "travel": 5000,
    "other": 1000,
}

ROLE_CAPS = {
    "associate": 5000,
    "manager": 15000,
    "senior manager": 30000,
    "director": 30000,
    "ppmds": 50000,
}

BLACKLISTED_MERCHANTS = {"Shady Supplier", "Fraudulent Co"}

# simple personal keyword detector
PERSONAL_KEYWORDS = {"girlfriend", "boyfriend", "wife", "husband", "vacation", "holiday", "personal", "leisure", "friend", "party", "concert"}

# sample mapping of employee base locations (would normally come from HR/profile service)
EMPLOYEE_BASE = {
    "EMP123": "Mumbai",
    "EMP002": "Delhi",
    "EMP999": "Kolkata",
}


async def validate(expense: Expense) -> Dict[str, Any]:
    """Return policy check results for travel expense validation."""
    await asyncio.sleep(0)
    status = "Compliant"
    findings = []
    rules = []

    category = expense.category.lower() if expense.category else "other"
    limit = PER_DIEM.get(category, PER_DIEM["other"])

    if expense.amount > limit:
        status = "Over-Limit"
        findings.append("Per-diem exceeded")
        rules.append(f"per_diem_{category}")

    role_cap = ROLE_CAPS.get(expense.role.lower(), ROLE_CAPS["associate"])
    if expense.amount > role_cap:
        status = "Violation"
        findings.append("Role spend cap exceeded")
        rules.append("role_spend_cap")

    if expense.merchant in BLACKLISTED_MERCHANTS:
        status = "Violation"
        findings.append("Blacklisted merchant")
        rules.append("merchant_blacklist")

    # business purpose enforcement: require business purpose for travel-related expenses
    travel_categories = {"airfare", "hotel", "taxi", "rail", "transport", "travel"}
    if category in travel_categories and not expense.business_purpose:
        # missing business purpose should flag for review
        if status != "Violation":
            status = "Over-Limit"
        findings.append("Missing business purpose")
        rules.append("missing_business_purpose")

    # detect personal keywords in description or business_purpose
    desc_lower = (expense.description or "").lower()
    bp_lower = (expense.business_purpose or "").lower()
    personal_found = [w for w in PERSONAL_KEYWORDS if w in desc_lower or w in bp_lower]
    if personal_found:
        status = "Violation"
        findings.append("Personal/non-business expense detected")
        rules.append("personal_expense")

    # hometown check: if arrival city equals employee base, verify business purpose
    emp_base = EMPLOYEE_BASE.get(expense.employee_id)
    if emp_base and expense.arrival_city:
        if expense.arrival_city.lower() == emp_base.lower() and (expense.departure_city and expense.departure_city.lower() != emp_base.lower()):
            # travel to hometown — require explicit business purpose
            if not expense.business_purpose or any(w in bp_lower for w in PERSONAL_KEYWORDS):
                status = "Violation"
                findings.append("Travel to hometown without valid business purpose")
                rules.append("hometown_travel_check")

    # determine a canonical city for legacy and travel fields
    city = ""
    if getattr(expense, "arrival_city", None):
        city = expense.arrival_city
    elif getattr(expense, "departure_city", None):
        city = expense.departure_city

    submitted_key = (expense.employee_id, expense.amount, expense.merchant, city)

    def prev_key(prev: Dict[str, Any]):
        return (
            prev.get("employee_id"),
            prev.get("amount"),
            prev.get("merchant"),
            prev.get("city") or prev.get("arrival_city") or prev.get("departure_city"),
        )

    seen = any(prev_key(prev) == submitted_key for prev in expense.previous_submissions)
    if seen:
        status = "Violation"
        findings.append("Duplicate submission detected")
        rules.append("duplicate_expense")

    return {
        "policy_status": status,
        "findings": findings,
        "rules": rules,
        "city": city,
        "category": category,
        "role": expense.role,
    }


async def handle(message: Dict[str, Any]) -> Dict[str, Any]:
    data = message.get("expense", {})
    print("policy_agent.handle received keys:", list(data.keys()))
    exp = Expense(**data)
    if "previous_submissions" in data:
        exp.previous_submissions = data.get("previous_submissions", [])
    result = await validate(exp)
    return {"policy": result}
