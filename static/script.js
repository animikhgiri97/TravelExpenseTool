document.getElementById('expenseForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const form = e.target;
  const data = Object.fromEntries(new FormData(form).entries());
  data.receipt = form.querySelector('[name=receipt]').checked;
  data.amount = parseFloat(data.amount || 0);

  const res = await fetch('/api/process', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  const json = await res.json();
  const resultEl = document.getElementById('result');
  resultEl.innerHTML = renderResultCard(json, data);
});

function renderResultCard(data, request) {
  const decision = data.decision || 'UNKNOWN';
  const meta = data.audit_log || [];
  const policy = meta.find((item) => item.event === 'policy_evaluation');
  const classification = meta.find((item) => item.event === 'classification_evaluation');
  const finalDecision = meta.find((item) => item.event === 'final_decision');

  const statusClass = decision === 'APPROVED' ? 'status-approved' : decision === 'REJECTED' ? 'status-rejected' : 'status-flagged';
  const statusText = decision === 'APPROVED' ? 'Approved' : decision === 'REJECTED' ? 'Rejected' : 'Flagged';

  const category = classification?.details?.category || request.category || 'Travel';
  const tripType = request.category ? startCase(request.category) : 'Travel';
  const route = request.departure_city && request.arrival_city ? `${request.departure_city} → ${request.arrival_city}` : request.arrival_city || request.departure_city || 'Unknown route';
  const role = data.employee_role || policy?.details?.role || request.role || 'Unknown';
  const employeeName = request.employee_name || 'Me';
  const reason = finalDecision?.details?.reason || 'No decision reason provided';
  const glCode = classification?.details?.gl_code || 'N/A';
  const riskScore = classification?.details?.risk_score ?? '-';
  const policyFindings = policy?.details?.findings || [];
  const policyStatus = policy?.details?.policy_status || 'Unknown';

  return `
    <div class="card">
      <div class="status-line ${statusClass === 'status-approved' ? 'status-approved-line' : statusClass === 'status-rejected' ? 'status-rejected-line' : 'status-flagged-line'}"></div>
      <div class="card-top">
        <div>
          <div class="status-badge ${statusClass}">${statusText}</div>
          <h3 class="card-title">${tripType} expense for ${role}</h3>
          <div class="card-meta">${formatCurrency(request.amount, request.currency)} · ${route} · ${request.description || 'Travel expense'}</div>
        </div>
        <div class="trip-pill">${tripType}</div>
      </div>

      <div class="card-grid">
        <div class="card-block">
          <strong>Employee</strong>
          <span>${request.employee_id || 'Unknown'}</span>
        </div>
        <div class="card-block">
          <strong>Name</strong>
          <span>${employeeName}</span>
        </div>
        <div class="card-block">
          <strong>Role</strong>
          <span>${role}</span>
        </div>
        <div class="card-block">
          <strong>Route</strong>
          <span>${route}</span>
        </div>
      </div>

      <div class="card-grid">
        <div class="card-block">
          <strong>Policy status</strong>
          <span>${policyStatus}</span>
        </div>
        <div class="card-block">
          <strong>GL code</strong>
          <span>${glCode}</span>
        </div>
        <div class="card-block risk-${getRiskClass(riskScore)}">
          <strong>Risk score</strong>
          <span>${formatRisk(riskScore)} (${riskScore}/100)</span>
        </div>
      </div>

      <div class="section">
        <div class="section-title">Policy agent</div>
        <div class="section-text">${policyFindings.length ? policyFindings.map((f) => `• ${f}`).join('<br>') : 'Passes all policy checks.'}</div>
      </div>

      <div class="section">
        <div class="section-title">Decision</div>
        <div class="decision-box"><strong>${formatDecisionText(decision, reason)}</strong></div>
      </div>
    </div>
  `;
}

function startCase(value) {
  return value
    .split(/[_-]/)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

function formatCurrency(amount, currency) {
  const code = currency || 'USD';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: code }).format(amount || 0);
}

function formatRisk(score) {
  if (typeof score !== 'number') return 'N/A';
  if (score >= 80) return 'HIGH';
  if (score >= 60) return 'MEDIUM';
  return 'LOW';
}

function formatDecisionText(decision, reason) {
  if (decision === 'APPROVED') return 'Auto-approved. No exceptions triggered.';
  if (decision === 'FLAGGED') return 'Routed to line manager for manual review.';
  if (decision === 'REJECTED') return `Rejected. ${reason}`;
  return reason;
}

function getRiskClass(score) {
  if (typeof score !== 'number') return 'low';
  if (score >= 80) return 'high';
  if (score >= 60) return 'medium';
  return 'low';
}
