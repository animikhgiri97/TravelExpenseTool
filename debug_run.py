import asyncio
from schema import Expense
from orchestrator import process_expense

async def main():
    exp = Expense(employee_id='EMP002', amount=450.0, currency='INR', merchant='Zomato', description='visiting girlfriend', category='taxi', departure_city='Kolkata', arrival_city='Delhi', role='Associate', business_purpose='', employee_base='Kolkata', receipt=False)
    res = await process_expense(exp)
    print('RESULT:', res)

if __name__ == '__main__':
    asyncio.run(main())
