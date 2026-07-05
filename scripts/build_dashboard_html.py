import csv
import json
import os

def build_dashboard():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "power_bi", "gold_obt_healthcare_analytics.csv")
    out_html = os.path.join(base_dir, "power_bi", "dashboard.html")

    records = []
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)

    json_data = json.dumps(records)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hospital Operations & Patient Analytics</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {{
      --bg-main: #f8fafc;
      --bg-card: #ffffff;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --border: #e2e8f0;
      --primary: #2563eb;
      --success: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
      --purple: #8b5cf6;
      --font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      background-color: var(--bg-main);
      color: var(--text-main);
      font-family: var(--font-family);
      padding: 24px;
      line-height: 1.5;
    }}

    /* HEADER */
    .dashboard-header {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px 24px;
      margin-bottom: 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}

    .header-text h1 {{
      font-size: 22px;
      font-weight: 700;
      color: var(--text-main);
    }}

    .header-text p {{
      font-size: 13px;
      color: var(--text-muted);
      margin-top: 2px;
    }}

    .controls {{
      display: flex;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
    }}

    .control-item {{
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}

    .control-item label {{
      font-size: 11px;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
    }}

    select {{
      background-color: #ffffff;
      color: var(--text-main);
      border: 1px solid var(--border);
      padding: 8px 12px;
      border-radius: 6px;
      font-size: 13px;
      font-family: var(--font-family);
      outline: none;
      cursor: pointer;
    }}

    select:focus {{
      border-color: var(--primary);
    }}

    .btn-reset {{
      background: #f1f5f9;
      color: var(--text-main);
      border: 1px solid var(--border);
      padding: 8px 14px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      align-self: flex-end;
    }}

    .btn-reset:hover {{
      background: #e2e8f0;
    }}

    /* KPI METRICS */
    .kpi-row {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}

    .kpi-box {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 16px 20px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}

    .kpi-label {{
      font-size: 12px;
      font-weight: 600;
      color: var(--text-muted);
    }}

    .kpi-val {{
      font-size: 24px;
      font-weight: 700;
      color: var(--text-main);
      margin-top: 4px;
    }}

    /* TABS */
    .tabs-bar {{
      display: flex;
      gap: 8px;
      border-bottom: 1px solid var(--border);
      margin-bottom: 20px;
    }}

    .tab-item {{
      background: none;
      border: none;
      padding: 10px 16px;
      font-size: 14px;
      font-weight: 500;
      font-family: var(--font-family);
      color: var(--text-muted);
      cursor: pointer;
      border-bottom: 2px solid transparent;
    }}

    .tab-item.active {{
      color: var(--primary);
      border-bottom-color: var(--primary);
      font-weight: 600;
    }}

    .tab-page {{
      display: none;
    }}

    .tab-page.active {{
      display: block;
    }}

    /* CARDS & CHARTS */
    .chart-grid-2 {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
      gap: 20px;
      margin-bottom: 20px;
    }}

    .card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 20px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}

    .card-title {{
      font-size: 15px;
      font-weight: 600;
      color: var(--text-main);
      margin-bottom: 16px;
    }}

    .chart-box {{
      position: relative;
      min-height: 250px;
    }}

    /* TABLES */
    .table-wrapper {{
      overflow-x: auto;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
      text-align: left;
    }}

    th {{
      background-color: #f8fafc;
      color: var(--text-muted);
      font-weight: 600;
      padding: 10px 12px;
      border-bottom: 1px solid var(--border);
      font-size: 12px;
    }}

    td {{
      padding: 10px 12px;
      border-bottom: 1px solid var(--border);
      color: var(--text-main);
    }}

    tr:hover td {{
      background-color: #f1f5f9;
    }}

    @media (max-width: 768px) {{
      .chart-grid-2 {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>

  <!-- HEADER -->
  <div class="dashboard-header">
    <div class="header-text">
      <h1>Hospital Operations & Patient Analytics</h1>
      <p>Executive Performance & Billing Summary</p>
    </div>
    <div class="controls">
      <div class="control-item">
        <label>Hospital</label>
        <select id="filter-hospital"><option value="ALL">All Facilities</option></select>
      </div>
      <div class="control-item">
        <label>Insurance Payer</label>
        <select id="filter-payer"><option value="ALL">All Payers</option></select>
      </div>
      <div class="control-item">
        <label>Encounter Type</label>
        <select id="filter-class"><option value="ALL">All Visit Types</option></select>
      </div>
      <button class="btn-reset" onclick="resetFilters()">Reset Filters</button>
    </div>
  </div>

  <!-- KPI SUMMARY CARDS -->
  <div class="kpi-row">
    <div class="kpi-box">
      <div class="kpi-label">Total Patient Encounters</div>
      <div class="kpi-val" id="kpi-encounters">0</div>
    </div>
    <div class="kpi-box">
      <div class="kpi-label">Total Billed Revenue</div>
      <div class="kpi-val" id="kpi-revenue">$0</div>
    </div>
    <div class="kpi-box">
      <div class="kpi-label">Payer Coverage Rate</div>
      <div class="kpi-val" id="kpi-coverage">0%</div>
    </div>
    <div class="kpi-box">
      <div class="kpi-label">Avg Out-of-Pocket Cost</div>
      <div class="kpi-val" id="kpi-copay">$0</div>
    </div>
    <div class="kpi-box">
      <div class="kpi-label">Avg Length of Stay</div>
      <div class="kpi-val" id="kpi-stay">0 hrs</div>
    </div>
  </div>

  <!-- NAVIGATION TABS -->
  <div class="tabs-bar">
    <button class="tab-item active" onclick="showTab('tab-overview', this)">Executive Summary</button>
    <button class="tab-item" onclick="showTab('tab-financials', this)">Financial & Payer Breakdown</button>
    <button class="tab-item" onclick="showTab('tab-operations', this)">Hospital & Physician Metrics</button>
    <button class="tab-item" onclick="showTab('tab-clinical', this)">Clinical & Demographics</button>
  </div>

  <!-- TAB 1: EXECUTIVE SUMMARY -->
  <div id="tab-overview" class="tab-page active">
    <div class="chart-grid-2">
      <div class="card">
        <div class="card-title">Monthly Patient Encounter Volume</div>
        <div class="chart-box"><canvas id="chart-monthly"></canvas></div>
      </div>
      <div class="card">
        <div class="card-title">Encounter Class Breakdown</div>
        <div class="chart-box"><canvas id="chart-class"></canvas></div>
      </div>
    </div>
    <div class="card">
      <div class="card-title">Top Diagnosed Conditions</div>
      <div class="chart-box" style="min-height: 220px;"><canvas id="chart-conditions"></canvas></div>
    </div>
  </div>

  <!-- TAB 2: FINANCIALS -->
  <div id="tab-financials" class="tab-page">
    <div class="chart-grid-2">
      <div class="card">
        <div class="card-title">Billed Cost vs Insurance Coverage by Visit Type</div>
        <div class="chart-box"><canvas id="chart-coverage"></canvas></div>
      </div>
      <div class="card">
        <div class="card-title">Patient Out-of-Pocket Expense by Race</div>
        <div class="chart-box"><canvas id="chart-copay-race"></canvas></div>
      </div>
    </div>
    <div class="card">
      <div class="card-title">Insurance Payer Financial Performance</div>
      <div class="table-wrapper">
        <table id="table-payers">
          <thead>
            <tr>
              <th>Payer Name</th>
              <th>Total Encounters</th>
              <th>Total Billed Revenue</th>
              <th>Payer Coverage</th>
              <th>Patient Out-of-Pocket</th>
              <th>Coverage Rate</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- TAB 3: OPERATIONS -->
  <div id="tab-operations" class="tab-page">
    <div class="chart-grid-2">
      <div class="card">
        <div class="card-title">Hospital Facility Revenue Ranking</div>
        <div class="chart-box"><canvas id="chart-hospitals"></canvas></div>
      </div>
      <div class="card">
        <div class="card-title">Physician Specialty Distribution</div>
        <div class="chart-box"><canvas id="chart-specialties"></canvas></div>
      </div>
    </div>
  </div>

  <!-- TAB 4: CLINICAL -->
  <div id="tab-clinical" class="tab-page">
    <div class="chart-grid-2">
      <div class="card">
        <div class="card-title">Patient Demographics by Gender</div>
        <div class="chart-box"><canvas id="chart-gender"></canvas></div>
      </div>
      <div class="card">
        <div class="card-title">Top Prescribed Medications Summary</div>
        <div class="table-wrapper">
          <table id="table-meds">
            <thead>
              <tr>
                <th>Medication Description</th>
                <th>Prescription Count</th>
                <th>Avg Total Cost</th>
              </tr>
            </thead>
            <tbody></tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <script>
    const dataset = {json_data};
    let activeCharts = {{}};

    function init() {{
      buildDropdowns();
      updateDashboard();

      document.getElementById('filter-hospital').addEventListener('change', updateDashboard);
      document.getElementById('filter-payer').addEventListener('change', updateDashboard);
      document.getElementById('filter-class').addEventListener('change', updateDashboard);
    }}

    function getFilteredData() {{
      const h = document.getElementById('filter-hospital').value;
      const p = document.getElementById('filter-payer').value;
      const c = document.getElementById('filter-class').value;

      return dataset.filter(d => {{
        if (h !== 'ALL' && d.hospital_name !== h) return false;
        if (p !== 'ALL' && d.payor_name !== p) return false;
        if (c !== 'ALL' && d.encounter_class !== c) return false;
        return true;
      }});
    }}

    function buildDropdowns() {{
      const hosps = [...new Set(dataset.map(d => d.hospital_name).filter(Boolean))].sort();
      const payors = [...new Set(dataset.map(d => d.payor_name).filter(Boolean))].sort();
      const classes = [...new Set(dataset.map(d => d.encounter_class).filter(Boolean))].sort();

      const hSel = document.getElementById('filter-hospital');
      hosps.forEach(item => hSel.add(new Option(item, item)));

      const pSel = document.getElementById('filter-payer');
      payors.forEach(item => pSel.add(new Option(item, item)));

      const cSel = document.getElementById('filter-class');
      classes.forEach(item => cSel.add(new Option(item, item)));
    }}

    function resetFilters() {{
      document.getElementById('filter-hospital').value = 'ALL';
      document.getElementById('filter-payer').value = 'ALL';
      document.getElementById('filter-class').value = 'ALL';
      updateDashboard();
    }}

    function showTab(tabId, btn) {{
      document.querySelectorAll('.tab-page').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.tab-item').forEach(el => el.classList.remove('active'));
      document.getElementById(tabId).classList.add('active');
      btn.classList.add('active');
    }}

    function updateDashboard() {{
      const data = getFilteredData();

      const totalCount = data.length;
      const totalRev = data.reduce((acc, d) => acc + parseFloat(d.total_claim_cost || 0), 0);
      const totalCov = data.reduce((acc, d) => acc + parseFloat(d.payer_coverage || 0), 0);
      const totalCopay = data.reduce((acc, d) => acc + parseFloat(d.patient_out_of_pocket_cost || 0), 0);
      const avgStay = totalCount ? (data.reduce((acc, d) => acc + parseFloat(d.length_of_stay_hours || 0), 0) / totalCount).toFixed(1) : 0;
      const covPct = totalRev ? ((totalCov / totalRev) * 100).toFixed(1) : 0;

      document.getElementById('kpi-encounters').innerText = totalCount.toLocaleString();
      document.getElementById('kpi-revenue').innerText = '$' + Math.round(totalRev).toLocaleString();
      document.getElementById('kpi-coverage').innerText = covPct + '%';
      document.getElementById('kpi-copay').innerText = '$' + Math.round(totalCount ? totalCopay / totalCount : 0).toLocaleString();
      document.getElementById('kpi-stay').innerText = avgStay + ' hrs';

      renderMonthly(data);
      renderClass(data);
      renderConditions(data);
      renderCoverage(data);
      renderRaceCopay(data);
      renderPayerTable(data);
      renderHospitals(data);
      renderSpecialties(data);
      renderGender(data);
      renderMedsTable(data);
    }}

    function renderChart(id, type, data, options) {{
      if (activeCharts[id]) activeCharts[id].destroy();
      const ctx = document.getElementById(id).getContext('2d');
      activeCharts[id] = new Chart(ctx, {{ type, data, options }});
    }}

    function renderMonthly(data) {{
      const monthly = {{}};
      data.forEach(d => {{
        if (d.encounter_start_at) {{
          const m = d.encounter_start_at.substring(0, 7);
          monthly[m] = (monthly[m] || 0) + 1;
        }}
      }});
      const labels = Object.keys(monthly).sort();

      renderChart('chart-monthly', 'line', {{
        labels,
        datasets: [{{
          label: 'Encounters',
          data: labels.map(l => monthly[l]),
          borderColor: '#2563eb',
          backgroundColor: 'rgba(37, 99, 235, 0.1)',
          fill: true,
          tension: 0.2
        }}]
      }}, {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }} }}
      }});
    }}

    function renderClass(data) {{
      const counts = {{}};
      data.forEach(d => {{
        const c = d.encounter_class || 'Other';
        counts[c] = (counts[c] || 0) + 1;
      }});

      renderChart('chart-class', 'doughnut', {{
        labels: Object.keys(counts),
        datasets: [{{
          data: Object.values(counts),
          backgroundColor: ['#2563eb', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444']
        }}]
      }}, {{
        responsive: true,
        maintainAspectRatio: false
      }});
    }}

    function renderConditions(data) {{
      const conds = {{}};
      data.forEach(d => {{
        if (d.condition_description) {{
          conds[d.condition_description] = (conds[d.condition_description] || 0) + 1;
        }}
      }});
      const sorted = Object.entries(conds).sort((a,b) => b[1] - a[1]).slice(0, 5);

      renderChart('chart-conditions', 'bar', {{
        labels: sorted.map(s => s[0]),
        datasets: [{{
          label: 'Diagnoses',
          data: sorted.map(s => s[1]),
          backgroundColor: '#3b82f6',
          borderRadius: 4
        }}]
      }}, {{
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }} }}
      }});
    }}

    function renderCoverage(data) {{
      const byClass = {{}};
      data.forEach(d => {{
        const c = d.encounter_class || 'Other';
        if (!byClass[c]) byClass[c] = {{ billed: 0, covered: 0 }};
        byClass[c].billed += parseFloat(d.total_claim_cost || 0);
        byClass[c].covered += parseFloat(d.payer_coverage || 0);
      }});
      const labels = Object.keys(byClass);

      renderChart('chart-coverage', 'bar', {{
        labels,
        datasets: [
          {{ label: 'Billed', data: labels.map(l => byClass[l].billed), backgroundColor: '#2563eb' }},
          {{ label: 'Covered', data: labels.map(l => byClass[l].covered), backgroundColor: '#10b981' }}
        ]
      }}, {{
        responsive: true,
        maintainAspectRatio: false
      }});
    }}

    function renderRaceCopay(data) {{
      const races = {{}};
      data.forEach(d => {{
        const r = d.patient_race || 'Unknown';
        if (!races[r]) races[r] = {{ total: 0, count: 0 }};
        races[r].total += parseFloat(d.patient_out_of_pocket_cost || 0);
        races[r].count += 1;
      }});
      const labels = Object.keys(races);

      renderChart('chart-copay-race', 'bar', {{
        labels,
        datasets: [{{
          label: 'Avg Out-of-Pocket ($)',
          data: labels.map(l => races[l].count ? (races[l].total / races[l].count) : 0),
          backgroundColor: '#ef4444',
          borderRadius: 4
        }}]
      }}, {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }} }}
      }});
    }}

    function renderPayerTable(data) {{
      const payers = {{}};
      data.forEach(d => {{
        const p = d.payor_name || 'Self-Pay';
        if (!payers[p]) payers[p] = {{ count: 0, billed: 0, covered: 0, copay: 0 }};
        payers[p].count += 1;
        payers[p].billed += parseFloat(d.total_claim_cost || 0);
        payers[p].covered += parseFloat(d.payer_coverage || 0);
        payers[p].copay += parseFloat(d.patient_out_of_pocket_cost || 0);
      }});

      const tbody = document.querySelector('#table-payers tbody');
      tbody.innerHTML = '';
      Object.entries(payers).forEach(([name, p]) => {{
        const pct = p.billed ? ((p.covered / p.billed) * 100).toFixed(1) : 0;
        tbody.innerHTML += `<tr>
          <td><strong>${{name}}</strong></td>
          <td>${{p.count}}</td>
          <td>$${{Math.round(p.billed).toLocaleString()}}</td>
          <td>$${{Math.round(p.covered).toLocaleString()}}</td>
          <td>$${{Math.round(p.copay).toLocaleString()}}</td>
          <td>${{pct}}%</td>
        </tr>`;
      }});
    }}

    function renderHospitals(data) {{
      const hosps = {{}};
      data.forEach(d => {{
        const h = d.hospital_name || 'Unknown';
        hosps[h] = (hosps[h] || 0) + parseFloat(d.total_claim_cost || 0);
      }});
      const sorted = Object.entries(hosps).sort((a,b) => b[1] - a[1]);

      renderChart('chart-hospitals', 'bar', {{
        labels: sorted.map(s => s[0]),
        datasets: [{{
          label: 'Total Revenue ($)',
          data: sorted.map(s => s[1]),
          backgroundColor: '#2563eb',
          borderRadius: 4
        }}]
      }}, {{
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }} }}
      }});
    }}

    function renderSpecialties(data) {{
      const specs = {{}};
      data.forEach(d => {{
        const s = d.doctor_specialty || 'General Practice';
        specs[s] = (specs[s] || 0) + 1;
      }});

      renderChart('chart-specialties', 'pie', {{
        labels: Object.keys(specs),
        datasets: [{{
          data: Object.values(specs),
          backgroundColor: ['#2563eb', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4']
        }}]
      }}, {{
        responsive: true,
        maintainAspectRatio: false
      }});
    }}

    function renderGender(data) {{
      const genders = {{}};
      data.forEach(d => {{
        const g = d.patient_gender === 'M' ? 'Male' : (d.patient_gender === 'F' ? 'Female' : 'Other');
        genders[g] = (genders[g] || 0) + 1;
      }});

      renderChart('chart-gender', 'pie', {{
        labels: Object.keys(genders),
        datasets: [{{
          data: Object.values(genders),
          backgroundColor: ['#2563eb', '#ef4444']
        }}]
      }}, {{
        responsive: true,
        maintainAspectRatio: false
      }});
    }}

    function renderMedsTable(data) {{
      const meds = {{}};
      data.forEach(d => {{
        if (d.medication_description) {{
          const m = d.medication_description;
          if (!meds[m]) meds[m] = {{ count: 0, total: 0 }};
          meds[m].count += 1;
          meds[m].total += parseFloat(d.total_claim_cost || 0);
        }}
      }});

      const tbody = document.querySelector('#table-meds tbody');
      tbody.innerHTML = '';
      Object.entries(meds).sort((a,b) => b[1].count - a[1].count).slice(0, 8).forEach(([desc, m]) => {{
        const avg = m.count ? (m.total / m.count).toFixed(2) : 0;
        tbody.innerHTML += `<tr>
          <td><strong>${{desc}}</strong></td>
          <td>${{m.count}}</td>
          <td>$${{avg}}</td>
        </tr>`;
      }});
    }}

    window.onload = init;
  </script>
</body>
</html>
"""

    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ Clean Human-style Dashboard generated: {out_html}")

if __name__ == "__main__":
    build_dashboard()
