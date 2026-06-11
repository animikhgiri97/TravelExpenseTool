import asyncio
from schema import Expense
from orchestrator import process_batch


async def run_demo():
    expenses = [
        Expense(id="e1", amount=45.0, merchant="Cafe Goodfood", description="Lunch with client", receipt=True),
        Expense(id="e2", amount=1200.0, merchant="Hotel Grand", description="Conference lodging", receipt=True),
        Expense(id="e3", amount=200.0, merchant="Shady Supplier", description="Misc services", receipt=False),
    ]

    results = await process_batch(expenses)
    for e, res in zip(expenses, results):
        print(f"Expense {e.id}: amount={e.amount} merchant={e.merchant}")
        print(res)
        print("---")


if __name__ == '__main__':
    asyncio.run(run_demo())
