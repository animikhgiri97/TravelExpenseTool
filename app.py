from flask import Flask, render_template, request, jsonify
import asyncio
from schema import Expense
from orchestrator import process_expense

# simple in-memory employee profile lookup (mock HR/profile service)
EMPLOYEE_DB = {
    "EMP001": {"role": "Analyst", "base": "Mumbai"},
    "EMP002": {"role": "Consultant", "base": "Delhi"},
    "EMP123": {"role": "Senior Consultant", "base": "Kolkata"},
}

FALLBACK_ROLES = ["Analyst", "Consultant", "Senior Consultant", "Manager", "Senior Manager", "PPMDs"]

app = Flask(__name__, static_folder='static', template_folder='templates')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/process', methods=['POST'])
def api_process():
    data = request.get_json() or {}
    # diagnostic: show which orchestrator and policy_agent modules are loaded
    try:
        import orchestrator as _orch
        import agents.policy_agent as _policy
        print(f"api_process: orchestrator module -> {_orch.__file__}", flush=True)
        print(f"api_process: policy_agent module -> {_policy.__file__}", flush=True)
    except Exception:
        print("api_process: failed to introspect modules", flush=True)
    # look up employee profile (role, base) using employee_id
    emp_id = data.get('employee_id', 'unknown')
    profile = EMPLOYEE_DB.get(emp_id, {})

    role = profile.get('role')
    if not role:
        import random
        role = random.choice(FALLBACK_ROLES)

    expense = Expense(
        employee_id=emp_id,
        amount=float(data.get('amount', 0)),
        currency=data.get('currency', 'INR'),
        merchant=data.get('merchant', ''),
        description=data.get('description', ''),
        category=data.get('category', ''),
        departure_city=data.get('departure_city', '') or data.get('city', ''),
        arrival_city=data.get('arrival_city', ''),
        role=role,
        business_purpose=data.get('business_purpose', '').strip(),
        employee_base=profile.get('base', ''),
        receipt=bool(data.get('receipt', False)),
    )

    result = asyncio.run(process_expense(expense))
    result["employee_role"] = expense.role
    result["employee_base"] = expense.employee_base
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
