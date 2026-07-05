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
  <title>Synthea Healthcare Executive Analytics Dashboard</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@500;600;700&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {{
      --bg-main: #0f172a;
      --bg-card: #1e293b;
      --bg-card-hover: #334155;
      --accent-blue: #38bdf8;
      --accent-indigo: #818cf8;
      --accent-emerald: #34d399;
      --accent-rose: #f43f5e;
      --accent-amber: #fbbf24;
      --text-primary: #f8fafc;
      --text-secondary: #94a3b8;
      --border-color: rgba(255, 255, 255, 0.08);
      --font-heading: 'Outfit', sans-serif;
      --font-body: 'Inter', sans-serif;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      background-color: var(--bg-main);
      color: var(--text-primary);
      font-family: var(--font-body);
      min-height: 100vh;
      padding: 24px;
      line-height: 1.5;
    }}

    header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--border-color);
      flex-wrap: wrap;
      gap: 16px;
    }}

    .header-title h1 {{
      font-family: var(--font-heading);
      font-size: 26px;
      font-weight: 700;
      letter-spacing: -0.5px;
      background: linear-gradient(135deg, #38bdf8, #818cf8);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}

    .header-title p {{
      font-size: 13px;
      color: var(--text-secondary);
      margin-top: 2px;
    }}

    .filters {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }}

    .filter-group {{
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}

    .filter-group label {{
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-secondary);
      font-weight: 600;
    }}

    select {{
      background-color: var(--bg-card);
      color: var(--text-primary);
      border: 1px solid var(--border-color);
      padding: 8px 12px;
      border-radius: 8px;
      font-size: 13px;
      font-family: var(--font-body);
      outline: none;
      cursor: pointer;
      transition: border-color 0.2s;
    }}

    select:hover {{
      border-color: var(--accent-blue);
    }}

    .btn-reset {{
      background: rgba(244, 63, 94, 0.15);
      color: var(--accent-rose);
      border: 1px solid rgba(244, 63, 94, 0.3);
      padding: 8px 16px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      align-self: flex-end;
      transition: all 0.2s;
    }}

    .btn-reset:hover {{
      background: rgba(244, 63, 94, 0.25);
    }}

    /* KPI CARDS */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}

    .kpi-card {{
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 18px 20px;
      position: relative;
      overflow: hidden;
      transition: transform 0.2s, border-color 0.2s;
    }}

    .kpi-card:hover {{
      transform: translateY(-2px);
      border-color: rgba(255, 255, 255, 0.2);
    }}

    .kpi-card::before {{
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 4px;
      height: 100%;
      background: var(--card-accent, var(--accent-blue));
    }}

    .kpi-title {{
      font-size: 12px;
      font-weight: 600;
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    .kpi-value {{
      font-family: var(--font-heading);
      font-size: 24px;
      font-weight: 700;
      margin-top: 6px;
      color: var(--text-primary);
    }}

    .kpi-subtext {{
      font-size: 11px;
      color: var(--accent-emerald);
      margin-top: 4px;
      display: flex;
      align-items: center;
      gap: 4px;
    }}

    /* TABS */
    .nav-tabs {{
      display: flex;
      gap: 8px;
      border-bottom: 1px solid var(--border-color);
      margin-bottom: 24px;
    }}

    .tab-btn {{
      background: none;
      border: none;
      color: var(--text-secondary);
      padding: 12px 20px;
      font-size: 14px;
      font-weight: 600;
      font-family: var(--font-body);
      cursor: pointer;
      border-bottom: 2px solid transparent;
      transition: all 0.2s;
    }}

    .tab-btn:hover {{
      color: var(--text-primary);
    }}

    .tab-btn.active {{
      color: var(--accent-blue);
      border-bottom-color: var(--accent-blue);
    }}

    .tab-content {{
      display: none;
    }}

    .tab-content.active {{
      display: block;
    }}

    /* DASHBOARD GRID */
    .grid-2 {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
      gap: 20px;
      margin-bottom: 20px;
    }}

    .grid-3 {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 20px;
      margin-bottom: 20px;
    }}

    .chart-card {{
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 20px;
      display: flex;
      flex-direction: column;
    }}

    .chart-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }}

    .chart-header h3 {{
      font-family: var(--font-heading);
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
    }}

    .chart-container {{
      position: relative;
      flex-grow: 1;
      min-height: 260px;
    }}

    /* TABLE */
    .table-container {{
      overflow-x: auto;
      margin-top: 10px;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
      text-align: left;
    }}

    th {{
      background-color: rgba(255, 255, 255, 0.04);
      color: var(--text-secondary);
      font-weight: 600;
      padding: 12px 14px;
      border-bottom: 1px solid var(--border-color);
      text-transform: uppercase;
      font-size: 11px;
      letter-spacing: 0.5px;
    }}

    td {{
      padding: 12px 14px;
      border-bottom: 1px solid var(--border-color);
      color: var(--text-primary);
    }}

    tr:hover td {{
      background-color: rgba(255, 255, 255, 0.02);
    }}

    .badge {{
      display: inline-block;
      padding: 3px 8px;
      border-radius: 12px;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
    }}

    .badge-emergency {{ background: rgba(244, 63, 94, 0.2); color: #f43f5e; }}
    .badge-inpatient {{ background: rgba(251, 191, 36, 0.2); color: #fbbf24; }}
    .badge-wellness {{ background: rgba(52, 211, 153, 0.2); color: #34d399; }}
    .badge-ambulatory {{ background: rgba(56, 189, 248, 0.2); color: #38bdf8; }}

    footer {{
      margin-top: 40px;
      padding-top: 16px;
      border-top: 1px solid var(--border-color);
      text-align: center;
      font-size: 12px;
      color: var(--text-secondary);
    }}

    @media (max-width: 768px) {{
      .grid-2, .grid-3 {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>

  <header>
    <div class="header-title">
      <h1>Synthea Healthcare Executive Analytics</h1>
      <p>Medallion Data Pipeline (S3 → Snowflake → dbt 3NF + SCD2 → Star Schema OBT)</p>
    </div>
    <div class="filters">
      <div class="filter-group">
        <label>Hospital Facility</label>
        <select id="filter-hospital">
          <option value="ALL">All Hospitals</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Insurance Payer</label>
        <select id="filter-payer">
          <option value="ALL">All Payers</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Encounter Class</label>
        <select id="filter-class">
          <option value="ALL">All Classes</option>
        </select>
      </div>
      <button class="btn-reset" onclick="resetFilters()">Reset</button>
    </div>
  </header>

  <!-- KPI CARDS -->
  <div class="kpi-grid">
    <div class="kpi-card" style="--card-accent: var(--accent-blue);">
      <div class="kpi-title">Total Encounters</div>
      <div class="kpi-value" id="kpi-encounters">0</div>
      <div class="kpi-subtext">▲ 100% Verified in DW</div>
    </div>
    <div class="kpi-card" style="--card-accent: var(--accent-emerald);">
      <div class="kpi-title">Billed Claims Revenue</div>
      <div class="kpi-value" id="kpi-revenue">$0</div>
      <div class="kpi-subtext">▲ Total Billed Cost</div>
    </div>
    <div class="kpi-card" style="--card-accent: var(--accent-indigo);">
      <div class="kpi-title">Payer Coverage Rate</div>
      <div class="kpi-value" id="kpi-coverage">0%</div>
      <div class="kpi-subtext">Insurance Reimbursed</div>
    </div>
    <div class="kpi-card" style="--card-accent: var(--accent-rose);">
      <div class="kpi-title">Avg Out-of-Pocket</div>
      <div class="kpi-value" id="kpi-copay">$0</div>
      <div class="kpi-subtext">Patient Responsibility</div>
    </div>
    <div class="kpi-card" style="--card-accent: var(--accent-amber);">
      <div class="kpi-title">Avg Stay Duration</div>
      <div class="kpi-value" id="kpi-stay">0 hrs</div>
      <div class="kpi-subtext">Length of Stay</div>
    </div>
  </div>

  <!-- NAVIGATION TABS -->
  <div class="nav-tabs">
    <button class="tab-btn active" onclick="switchTab('tab-overview', this)">Executive Command Center</button>
    <button class="tab-btn" onclick="switchTab('tab-financials', this)">Financial & Payer Analytics</button>
    <button class="tab-btn" onclick="switchTab('tab-operations', this)">Hospital & Physician Performance</button>
    <button class="tab-btn" onclick="switchTab('tab-clinical', this)">Clinical & Demographics</button>
  </div>

  <!-- TAB 1: EXECUTIVE COMMAND CENTER -->
  <div id="tab-overview" class="tab-content active">
    <div class="grid-2">
      <div class="chart-card">
        <div class="chart-header">
          <h3>Monthly Encounter & Revenue Trend</h3>
        </div>
        <div class="chart-container">
          <canvas id="chart-monthly-trend"></canvas>
        </div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <h3>Encounter Class Distribution</h3>
        </div>
        <div class="chart-container">
          <canvas id="chart-encounter-class"></canvas>
        </div>
      </div>
    </div>
    <div class="chart-card">
      <div class="chart-header">
        <h3>Top Diagnosed Medical Conditions</h3>
      </div>
      <div class="chart-container" style="min-height: 220px;">
        <canvas id="chart-top-conditions"></canvas>
      </div>
    </div>
  </div>

  <!-- TAB 2: FINANCIAL & PAYER ANALYTICS -->
  <div id="tab-financials" class="tab-content">
    <div class="grid-2">
      <div class="chart-card">
        <div class="chart-header">
          <h3>Billed Cost vs Insurance Coverage by Visit Class</h3>
        </div>
        <div class="chart-container">
          <canvas id="chart-cost-vs-coverage"></canvas>
        </div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <h3>Patient Financial Responsibility by Race</h3>
        </div>
        <div class="chart-container">
          <canvas id="chart-race-copay"></canvas>
        </div>
      </div>
    </div>
    <div class="chart-card">
      <div class="chart-header">
        <h3>Insurance Payer Financial Performance Matrix</h3>
      </div>
      <div class="table-container">
        <table id="table-payer-matrix">
          <thead>
            <tr>
              <th>Payer Name</th>
              <th>Total Encounters</th>
              <th>Billed Revenue</th>
              <th>Payer Payout</th>
              <th>Patient Copay</th>
              <th>Coverage Rate</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- TAB 3: HOSPITAL & PHYSICIAN PERFORMANCE -->
  <div id="tab-operations" class="tab-content">
    <div class="grid-2">
      <div class="chart-card">
        <div class="chart-header">
          <h3>Hospital Facility Revenue Ranking</h3>
        </div>
        <div class="chart-container">
          <canvas id="chart-hospital-revenue"></canvas>
        </div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <h3>Physician Specialty Workload Distribution</h3>
        </div>
        <div class="chart-container">
          <canvas id="chart-specialty-dist"></canvas>
        </div>
      </div>
    </div>
  </div>

  <!-- TAB 4: CLINICAL & DEMOGRAPHICS -->
  <div id="tab-clinical" class="tab-content">
    <div class="grid-2">
      <div class="chart-card">
        <div class="chart-header">
          <h3>Patient Demographics by Gender & Race</h3>
        </div>
        <div class="chart-container">
          <canvas id="chart-demographics"></canvas>
        </div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <h3>Top Prescribed Medications Summary</h3>
        </div>
        <div class="table-container">
          <table id="table-medications">
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

  <footer>
    Synthea Healthcare Data Pipeline • AWS S3 Ingestion • Snowflake DW • dbt 3NF + SCD Type 2 Snapshots • Star Schema Power BI Export
  </footer>

  <script>
    const rawData = {json_data};
    let charts = {{}};

    function init() {{
      populateFilters();
      renderDashboard();

      document.getElementById('filter-hospital').addEventListener('change', renderDashboard);
      document.getElementById('filter-payer').addEventListener('change', renderDashboard);
      document.getElementById('filter-class').addEventListener('change', renderDashboard);
    }}

    function getFilteredData() {{
      const hosp = document.getElementById('filter-hospital').value;
      const pay = document.getElementById('filter-payer').value;
      const cls = document.getElementById('filter-class').value;

      return rawData.filter(d => {{
        if (hosp !== 'ALL' && d.hospital_name !== hosp) return false;
        if (pay !== 'ALL' && d.payor_name !== pay) return false;
        if (cls !== 'ALL' && d.encounter_class !== cls) return false;
        return true;
      }});
    }}

    function populateFilters() {{
      const hospitals = [...new Set(rawData.map(d => d.hospital_name).filter(Boolean))].sort();
      const payors = [...new Set(rawData.map(d => d.payor_name).filter(Boolean))].sort();
      const classes = [...new Set(rawData.map(d => d.encounter_class).filter(Boolean))].sort();

      const hSelect = document.getElementById('filter-hospital');
      hospitals.forEach(h => hSelect.add(new Option(h, h)));

      const pSelect = document.getElementById('filter-payer');
      payors.forEach(p => pSelect.add(new Option(p, p)));

      const cSelect = document.getElementById('filter-class');
      classes.forEach(c => cSelect.add(new Option(c, c)));
    }}

    function resetFilters() {{
      document.getElementById('filter-hospital').value = 'ALL';
      document.getElementById('filter-payer').value = 'ALL';
      document.getElementById('filter-class').value = 'ALL';
      renderDashboard();
    }}

    function switchTab(tabId, btn) {{
      document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(tb => tb.classList.remove('active'));
      document.getElementById(tabId).classList.add('active');
      btn.classList.add('active');
    }}

    function renderDashboard() {{
      const data = getFilteredData();

      // KPIs
      const totalEncounters = data.length;
      const totalRevenue = data.reduce((sum, d) => sum + parseFloat(d.total_claim_cost || 0), 0);
      const totalCoverage = data.reduce((sum, d) => sum + parseFloat(d.payer_coverage || 0), 0);
      const totalCopay = data.reduce((sum, d) => sum + parseFloat(d.patient_out_of_pocket_cost || 0), 0);
      const avgStay = totalEncounters ? (data.reduce((sum, d) => sum + parseFloat(d.length_of_stay_hours || 0), 0) / totalEncounters).toFixed(1) : 0;
      const covRate = totalRevenue ? ((totalCoverage / totalRevenue) * 100).toFixed(1) : 0;

      document.getElementById('kpi-encounters').innerText = totalEncounters.toLocaleString();
      document.getElementById('kpi-revenue').innerText = '$' + Math.round(totalRevenue).toLocaleString();
      document.getElementById('kpi-coverage').innerText = covRate + '%';
      document.getElementById('kpi-copay').innerText = '$' + Math.round(totalEncounters ? totalCopay / totalEncounters : 0).toLocaleString();
      document.getElementById('kpi-stay').innerText = avgStay + ' hrs';

      renderMonthlyTrend(data);
      renderEncounterClass(data);
      renderTopConditions(data);
      renderCostVsCoverage(data);
      renderRaceCopay(data);
      renderPayerMatrix(data);
      renderHospitalRevenue(data);
      renderSpecialtyDist(data);
      renderDemographics(data);
      renderMedicationsTable(data);
    }}

    function createOrUpdateChart(chartId, type, data, options) {{
      if (charts[chartId]) charts[chartId].destroy();
      const ctx = document.getElementById(chartId).getContext('2d');
      charts[chartId] = new Chart(ctx, {{ type, data, options }});
    }}

    function renderMonthlyTrend(data) {{
      const monthly = {{}};
      data.forEach(d => {{
        if (d.encounter_start_at) {{
          const month = d.encounter_start_at.substring(0, 7);
          monthly[month] = (monthly[month] || 0) + 1;
        }}
      }});
      const labels = Object.keys(monthly).sort();
      const values = labels.map(l => monthly[l]);

      createOrUpdateChart('chart-monthly-trend', 'line', {{
        labels,
        datasets: [{{
          label: 'Encounters',
          data: values,
          borderColor: '#38bdf8',
          backgroundColor: 'rgba(56, 189, 248, 0.1)',
          fill: true,
          tension: 0.3
        }}]
      }}, {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
          x: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#94a3b8' }} }},
          y: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#94a3b8' }} }}
        }}
      }});
    }}

    function renderEncounterClass(data) {{
      const counts = {{}};
      data.forEach(d => {{
        const cls = d.encounter_class || 'Other';
        counts[cls] = (counts[cls] || 0) + 1;
      }});

      createOrUpdateChart('chart-encounter-class', 'doughnut', {{
        labels: Object.keys(counts),
        datasets: [{{
          data: Object.values(counts),
          backgroundColor: ['#38bdf8', '#818cf8', '#34d399', '#fbbf24', '#f43f5e']
        }}]
      }}, {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{ legend: {{ position: 'right', labels: {{ color: '#f8fafc' }} }} }}
      }});
    }}

    function renderTopConditions(data) {{
      const conds = {{}};
      data.forEach(d => {{
        if (d.condition_description) {{
          conds[d.condition_description] = (conds[d.condition_description] || 0) + 1;
        }}
      }});
      const sorted = Object.entries(conds).sort((a,b) => b[1] - a[1]).slice(0, 5);

      createOrUpdateChart('chart-top-conditions', 'bar', {{
        labels: sorted.map(s => s[0]),
        datasets: [{{
          label: 'Diagnoses Count',
          data: sorted.map(s => s[1]),
          backgroundColor: '#818cf8',
          borderRadius: 6
        }}]
      }}, {{
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
          x: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#94a3b8' }} }},
          y: {{ grid: {{ display: false }}, ticks: {{ color: '#f8fafc' }} }}
        }}
      }});
    }}

    function renderCostVsCoverage(data) {{
      const byClass = {{}};
      data.forEach(d => {{
        const cls = d.encounter_class || 'Other';
        if (!byClass[cls]) byClass[cls] = {{ billed: 0, covered: 0 }};
        byClass[cls].billed += parseFloat(d.total_claim_cost || 0);
        byClass[cls].covered += parseFloat(d.payer_coverage || 0);
      }});

      const labels = Object.keys(byClass);
      createOrUpdateChart('chart-cost-vs-coverage', 'bar', {{
        labels,
        datasets: [
          {{ label: 'Total Billed', data: labels.map(l => byClass[l].billed), backgroundColor: '#38bdf8', borderRadius: 4 }},
          {{ label: 'Payer Covered', data: labels.map(l => byClass[l].covered), backgroundColor: '#34d399', borderRadius: 4 }}
        ]
      }}, {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{ legend: {{ labels: {{ color: '#f8fafc' }} }} }},
        scales: {{
          x: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#94a3b8' }} }},
          y: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#94a3b8' }} }}
        }}
      }});
    }}

    function renderRaceCopay(data) {{
      const raceMap = {{}};
      data.forEach(d => {{
        const r = d.patient_race || 'Unknown';
        if (!raceMap[r]) raceMap[r] = {{ copay: 0, count: 0 }};
        raceMap[r].copay += parseFloat(d.patient_out_of_pocket_cost || 0);
        raceMap[r].count += 1;
      }});

      const labels = Object.keys(raceMap);
      const avgs = labels.map(l => raceMap[l].count ? (raceMap[l].copay / raceMap[l].count) : 0);

      createOrUpdateChart('chart-race-copay', 'bar', {{
        labels,
        datasets: [{{
          label: 'Avg Out-of-Pocket ($)',
          data: avgs,
          backgroundColor: '#f43f5e',
          borderRadius: 6
        }}]
      }}, {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
          x: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#94a3b8' }} }},
          y: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#94a3b8' }} }}
        }}
      }});
    }}

    function renderPayerMatrix(data) {{
      const payers = {{}};
      data.forEach(d => {{
        const p = d.payor_name || 'Uninsured / Self-Pay';
        if (!payers[p]) payers[p] = {{ count: 0, billed: 0, covered: 0, copay: 0 }};
        payers[p].count += 1;
        payers[p].billed += parseFloat(d.total_claim_cost || 0);
        payers[p].covered += parseFloat(d.payer_coverage || 0);
        payers[p].copay += parseFloat(d.patient_out_of_pocket_cost || 0);
      }});

      const tbody = document.querySelector('#table-payer-matrix tbody');
      tbody.innerHTML = '';
      Object.entries(payers).forEach(([name, p]) => {{
        const covRate = p.billed ? ((p.covered / p.billed) * 100).toFixed(1) : 0;
        const row = `<tr>
          <td><strong>${{name}}</strong></td>
          <td>${{p.count}}</td>
          <td>$${{Math.round(p.billed).toLocaleString()}}</td>
          <td>$${{Math.round(p.covered).toLocaleString()}}</td>
          <td>$${{Math.round(p.copay).toLocaleString()}}</td>
          <td><span class="badge badge-wellness">${{covRate}}%</span></td>
        </tr>`;
        tbody.innerHTML += row;
      }});
    }}

    function renderHospitalRevenue(data) {{
      const hosps = {{}};
      data.forEach(d => {{
        const h = d.hospital_name || 'Unknown Facility';
        hosps[h] = (hosps[h] || 0) + parseFloat(d.total_claim_cost || 0);
      }});
      const sorted = Object.entries(hosps).sort((a,b) => b[1] - a[1]);

      createOrUpdateChart('chart-hospital-revenue', 'bar', {{
        labels: sorted.map(s => s[0]),
        datasets: [{{
          label: 'Total Revenue ($)',
          data: sorted.map(s => s[1]),
          backgroundColor: '#38bdf8',
          borderRadius: 6
        }}]
      }}, {{
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
          x: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#94a3b8' }} }},
          y: {{ grid: {{ display: false }}, ticks: {{ color: '#f8fafc' }} }}
        }}
      }});
    }}

    function renderSpecialtyDist(data) {{
      const specs = {{}};
      data.forEach(d => {{
        const s = d.doctor_specialty || 'General Practice';
        specs[s] = (specs[s] || 0) + 1;
      }});

      createOrUpdateChart('chart-specialty-dist', 'doughnut', {{
        labels: Object.keys(specs),
        datasets: [{{
          data: Object.values(specs),
          backgroundColor: ['#818cf8', '#38bdf8', '#fbbf24', '#34d399', '#f43f5e', '#a855f7']
        }}]
      }}, {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{ legend: {{ position: 'right', labels: {{ color: '#f8fafc' }} }} }}
      }});
    }}

    function renderDemographics(data) {{
      const genders = {{}};
      data.forEach(d => {{
        const g = d.patient_gender === 'M' ? 'Male' : (d.patient_gender === 'F' ? 'Female' : 'Other');
        genders[g] = (genders[g] || 0) + 1;
      }});

      createOrUpdateChart('chart-demographics', 'pie', {{
        labels: Object.keys(genders),
        datasets: [{{
          data: Object.values(genders),
          backgroundColor: ['#38bdf8', '#f43f5e']
        }}]
      }}, {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{ legend: {{ position: 'right', labels: {{ color: '#f8fafc' }} }} }}
      }});
    }}

    function renderMedicationsTable(data) {{
      const meds = {{}};
      data.forEach(d => {{
        if (d.medication_description) {{
          const m = d.medication_description;
          if (!meds[m]) meds[m] = {{ count: 0, total: 0 }};
          meds[m].count += 1;
          meds[m].total += parseFloat(d.total_claim_cost || 0);
        }}
      }});

      const tbody = document.querySelector('#table-medications tbody');
      tbody.innerHTML = '';
      Object.entries(meds).sort((a,b) => b[1].count - a[1].count).slice(0, 8).forEach(([desc, m]) => {{
        const avgCost = m.count ? (m.total / m.count).toFixed(2) : 0;
        const row = `<tr>
          <td><strong>${{desc}}</strong></td>
          <td>${{m.count}}</td>
          <td>$${{avgCost}}</td>
        </tr>`;
        tbody.innerHTML += row;
      }});
    }}

    window.onload = init;
  </script>
</body>
</html>
"""

    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ Dashboard generated successfully: {out_html}")

if __name__ == "__main__":
    build_dashboard()
