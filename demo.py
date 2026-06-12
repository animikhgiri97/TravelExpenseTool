import asyncio
from schema import Expense
from orchestrator import process_batch


async def run_demo():
    expenses = [
        Expense(
            employee_id="EMP001",
            amount=1200.0,
            currency="INR",
            merchant="Hotel Grand",
            description="Conference lodging",
            category="lodging",
            departure_city="",
            arrival_city="Mumbai",
            role="Associate",
            receipt=True,
            previous_submissions=[
                {"employee_id": "EMP001", "amount": 1200.0, "merchant": "Hotel Grand", "city": "Mumbai"}
            ],
        ),
        Expense(
            employee_id="EMP002",
            amount=1800.0,
            currency="INR",
            merchant="City Cab",
            description="Airport transfer",
            category="transport",
            departure_city="",
            arrival_city="Delhi",
            role="Manager",
            receipt=True,
        ),
        Expense(
            employee_id="EMP003",
            amount=90.0,
            currency="INR",
            merchant="Office Deli",
            description="Team lunch",
            category="meals",
            departure_city="",
            arrival_city="Bengaluru",
            role="Associate",
            receipt=False,
        ),
    ]

    results = await process_batch(expenses)
    for e, res in zip(expenses, results):
        print(f"Expense employee={e.employee_id} amount={e.amount} arrival={e.arrival_city} category={e.category}")
        print(res)
        print("---")


if __name__ == '__main__':
    asyncio.run(run_demo())
