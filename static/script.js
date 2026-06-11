document.getElementById('expenseForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const form = e.target;
  const data = Object.fromEntries(new FormData(form).entries());
  data.receipt = form.querySelector('[name=receipt]').checked;
  // coerce amount
  data.amount = parseFloat(data.amount || 0);

  const res = await fetch('/api/process', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  const json = await res.json();
  document.getElementById('result').textContent = JSON.stringify(json, null, 2);
});
