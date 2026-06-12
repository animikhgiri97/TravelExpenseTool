import asyncio
import uuid
from schema import Expense
from agents import policy_agent, classifier_agent, recommendation_agent
from broker import Broker


async def process_expense(expense: Expense) -> dict:
    """Runs policy and classification agents in parallel, then recommendation."""
    broker = Broker()

    broker.subscribe("policy", policy_agent.handle)
    broker.subscribe("classification", classifier_agent.handle)
    broker.subscribe("recommendation", recommendation_agent.handle)

    payload = expense.__dict__.copy()
    payload["previous_submissions"] = expense.previous_submissions
    # attach an internal expense id to metadata for downstream systems
    expense_id = f"e{uuid.uuid4().hex[:12]}"
    expense.metadata["expense_id"] = expense_id
    print("orchestrator: payload keys ->", list(payload.keys()), flush=True)

    policy_task = broker.request("policy", {"expense": payload})
    classification_task = broker.request("classification", {"expense": payload})

    policy_res, class_res = await asyncio.gather(policy_task, classification_task)
    print("orchestrator: policy_res=", policy_res, flush=True)
    print("orchestrator: class_res=", class_res, flush=True)
    policy_data = policy_res.get("policy") if policy_res else {}
    classification_data = class_res.get("classification") if class_res else {}

    expense.metadata["policy"] = policy_data
    expense.metadata["classification"] = classification_data

    reco_res = await broker.request(
        "recommendation",
        {"expense": payload, "metadata": expense.metadata},
    )
    expense.metadata["recommendation"] = reco_res.get("recommendation") if reco_res else {}

    return {
        "decision": expense.metadata["recommendation"]["final_decision"],
        "audit_log": expense.metadata["recommendation"]["audit_log"],
    }


async def process_batch(expenses):
    tasks = [process_expense(e) for e in expenses]
    return await asyncio.gather(*tasks)
