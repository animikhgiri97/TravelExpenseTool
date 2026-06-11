import asyncio
from schema import Expense
from agents import policy_agent, classifier_agent, recommendation_agent
from broker import Broker


async def process_expense(expense: Expense) -> dict:
    """Runs the expense through Policy -> Classifier -> Recommender agents
    using the in-memory A2A broker.
    """
    broker = Broker()

    # register agent handlers
    broker.subscribe("policy", policy_agent.handle)
    broker.subscribe("classification", classifier_agent.handle)
    broker.subscribe("recommendation", recommendation_agent.handle)

    # Policy check via broker
    policy_res = await broker.request("policy", {"expense": expense.__dict__})
    expense.metadata["policy"] = policy_res.get("policy") if policy_res else {}

    # Classification via broker
    class_res = await broker.request("classification", {"expense": expense.__dict__})
    expense.metadata["classification"] = class_res.get("classification") if class_res else {}

    # Recommendation via broker (pass metadata)
    reco_res = await broker.request(
        "recommendation",
        {"expense": expense.__dict__, "metadata": expense.metadata},
    )
    expense.metadata["recommendation"] = reco_res.get("recommendation") if reco_res else {}

    return expense.metadata


async def process_batch(expenses):
    tasks = [process_expense(e) for e in expenses]
    return await asyncio.gather(*tasks)
