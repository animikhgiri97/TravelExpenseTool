Multi-Agent Travel Expense Approval System

Overview
--------
This prototype demonstrates a simple multi-agent (A2A) flow for corporate card expense approvals.

Agents:
- Policy Validation Agent: checks policy violations
- Expense Classification Agent: assigns category labels
- Approval Recommendation Agent: returns approve/deny/escalate

Run
---
Run the demo:

```bash
python demo.py
```

Web UI
------
Start the Flask app and open http://localhost:5000

```bash
pip install -r requirements.txt
python app.py
```

Architecture
------------
Orchestrator -> Policy Agent -> Classification Agent -> Recommendation Agent
