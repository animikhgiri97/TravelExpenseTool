import asyncio
from datetime import datetime
from typing import Dict, Any
from schema import Expense


async def recommend(expense: Expense) -> Dict[str, Any]:
    """Return final decision based on policy and classification outputs."""
    await asyncio.sleep(0)
    policy = expense.metadata.get("policy", {})
    classification = expense.metadata.get("classification", {})

    policy_status = policy.get("policy_status", "Compliant")
    risk_score = classification.get("risk_score", 0)
    reason_lines = []
    manager_tier = "manager"
    decision = "APPROVED"

    if policy_status == "Violation":
        decision = "REJECTED"
        reason_lines.append("Policy violation detected")
        manager_tier = "director"
    elif policy_status == "Over-Limit":
        decision = "FLAGGED"
        reason_lines.append("Expense over per-diem limit")
        manager_tier = "manager"
    else:
        reason_lines.append("Policy compliant")

    if risk_score >= 85:
        if decision != "REJECTED":
            decision = "FLAGGED"
        reason_lines.append("High anomaly/fraud risk")
        manager_tier = "director"
    elif risk_score >= 60:
        if decision == "APPROVED":
            decision = "FLAGGED"
        reason_lines.append("Moderate risk score")

    if classification.get("gl_code") == "GL-5009":
        reason_lines.append("Mapped to generic ledger code")

    audit_log = [
        {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": "policy_evaluation",
            "details": policy,
        },
        {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": "classification_evaluation",
            "details": classification,
        },
        {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": "final_decision",
            "details": {
                "decision": decision,
                "reason": " | ".join(reason_lines),
                "manager_tier": manager_tier,
            },
        },
        {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": "erp_sync",
            "details": {
                "status": "pending",
                "payload": {
                    "expense_id": expense.metadata.get("expense_id") if expense.metadata else None,
                    "gl_code": classification.get("gl_code"),
                    "amount": expense.amount,
                    "currency": expense.currency,
                },
            },
        },
    ]

    return {
        "final_decision": decision,
        "justification": " | ".join(reason_lines),
        "manager_tier": manager_tier,
        "audit_log": audit_log,
    }


async def handle(message: Dict[str, Any]) -> Dict[str, Any]:
    data = message.get("expense", {})
    metadata = message.get("metadata", {})
    exp = Expense(**data)
    exp.metadata = metadata
    result = await recommend(exp)
    return {"recommendation": result}
