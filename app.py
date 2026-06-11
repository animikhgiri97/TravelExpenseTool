from flask import Flask, render_template, request, jsonify
import asyncio
from schema import Expense
from orchestrator import process_expense

app = Flask(__name__, static_folder='static', template_folder='templates')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/process', methods=['POST'])
def api_process():
    data = request.get_json() or {}
    expense = Expense(
        id=data.get('id', 'e-auto'),
        amount=float(data.get('amount', 0)),
        currency=data.get('currency', 'USD'),
        merchant=data.get('merchant', ''),
        description=data.get('description', ''),
        receipt=bool(data.get('receipt', False)),
    )

    # run orchestrator synchronously for demo
    result = asyncio.run(process_expense(expense))
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
