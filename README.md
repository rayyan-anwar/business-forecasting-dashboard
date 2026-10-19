# 📈 Business Forecasting Dashboard

<div align="center">

  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0F172A,35:1D4ED8,70:0891B2,100:14B8A6&height=240&section=header&text=Business%20Forecasting&fontSize=40&fontColor=FFFFFF&animation=fadeIn&fontAlignY=35&desc=Time%20Series%20Analysis%20%7C%20Predictive%20Insights%20%7C%20Smarter%20Planning&descSize=13&descAlignY=58" width="100%" alt="Animated Business Forecasting Dashboard banner" />

  <h3>Turn Historical Data into Forecasts You Can Evaluate</h3>

  **Created by Rayyan Anwar**

  *AI/ML Engineer · Researcher · Technology Manager · Software Developer*

  <p>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
    <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas" />
    <img src="https://img.shields.io/badge/Time_Series-0F766E?style=for-the-badge" alt="Time series forecasting" />
  </p>

  <p>
    <img src="https://img.shields.io/badge/Tests-18%20Passed-success?style=flat-square" alt="18 tests reported passing" />
    <img src="https://img.shields.io/badge/Forecasting-Backtested-blue?style=flat-square" alt="Backtested forecasting" />
    <img src="https://img.shields.io/badge/Data-Not%20Stored-0891B2?style=flat-square" alt="Data not stored" />
    <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="MIT License" />
  </p>

  <a href="https://github.com/rayyan-anwar">GitHub Profile</a> ·
  <a href="https://github.com/rayyan-anwar?tab=repositories">Explore Projects</a>

</div>

---

## 🚀 Overview

The **Business Forecasting Dashboard** is a time-series analysis application that transforms historical sales or demand data into forecasts, uncertainty intervals, and practical analytical reports.

Upload a CSV file, select a forecasting horizon, and receive a series-by-series analysis containing data-quality diagnostics, automatic frequency detection, backtested model selection, trend and seasonality views, outlier flags, and downloadable reports.

The application is designed to make forecasting more transparent by explaining the assumptions behind its predictions and warning users when data quality or model limitations could affect the results.

> [!IMPORTANT]
> **Forecasts are estimates, not commitments.** The system extrapolates historical patterns. Promotions, price changes, holidays, stock-outs, and other external drivers are not modelled. Evaluation results are based on synthetic data.

## ✨ Key Features

<table>
  <tr>
    <td width="50%">
      <h3>📂 CSV Data Upload</h3>
      Import historical sales or demand data with date, value, and an optional series identifier.
    </td>
    <td width="50%">
      <h3>🧹 Data Quality Analysis</h3>
      Identify invalid rows, missing periods, irregular observations, and aggregation requirements.
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>🧠 Automatic Model Selection</h3>
      Compare seven candidate forecasting models using rolling-origin backtesting and MASE.
    </td>
    <td width="50%">
      <h3>📊 Forecasts with Uncertainty</h3>
      Generate future estimates with per-horizon conformal-style uncertainty bands.
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>🔍 Trend & Seasonality</h3>
      Explore historical patterns, decomposition, and flagged outliers.
    </td>
    <td width="50%">
      <h3>📥 Downloadable Reports</h3>
      Export forecasts as CSV, analytical reports as Markdown, and results as JSON.
    </td>
  </tr>
</table>

## 📈 Evaluation Results

The following figures come from the committed synthetic-data evaluation, covering 60 held-out forecasts.

<details open>
<summary><strong>Reported benchmark results</strong></summary>

| Metric | Reported result |
|---|---:|
| Average held-out error versus seasonal naive | 6% lower |
| Forecasts outperforming seasonal naive | 63% |
| Coverage of nominal 80% uncertainty intervals | 85% of held-out days |
| Model choice within 5% of hindsight-best performance | 53% of cases |
| Average in-app backtest improvement | Approximately 21% |

</details>

### How to interpret these results

- **Held-out performance:** The selected forecasting approach reduced average held-out error by approximately 6% compared with the seasonal-naive benchmark in the reported evaluation.
- **Forecast consistency:** The selected approach outperformed the baseline in 63% of evaluated forecasts, so improvement was not universal.
- **Uncertainty intervals:** The reported 85% coverage exceeded the nominal 80% level. Coverage alone does not establish that intervals are appropriately calibrated across every horizon or series.
- **Model selection:** The chosen model was within 5% of the hindsight-best model in 53% of cases.
- **Backtest optimism:** The approximately 21% in-app backtest improvement was optimistic. The application labels this limitation rather than presenting the backtest gain as expected real-world performance.

These figures are specific to the synthetic evaluation. They are not guarantees of accuracy on your business data.

For methodology and caveats, see [Evaluation Documentation](docs/EVALUATION.md) and [`results/RESULTS.md`](results/RESULTS.md).

## 🔬 Forecasting Workflow

<div align="center">

  <img src="https://img.shields.io/badge/01-Upload%20Historical%20Data-0F766E?style=for-the-badge" alt="Step 1: Upload historical data" />
  <br />
  <img src="https://img.shields.io/badge/02-Validate%20%26%20Prepare-155E75?style=for-the-badge" alt="Step 2: Validate and prepare data" />
  <br />
  <img src="https://img.shields.io/badge/03-Backtest%20Candidate%20Models-1D4ED8?style=for-the-badge" alt="Step 3: Backtest models" />
  <br />
  <img src="https://img.shields.io/badge/04-Forecast%20with%20Intervals-6D28D9?style=for-the-badge" alt="Step 4: Forecast with intervals" />
  <br />
  <img src="https://img.shields.io/badge/05-Review%20%26%20Export-0F766E?style=for-the-badge" alt="Step 5: Review and export" />

</div>

1. **Upload:** Provide a CSV containing historical observations.
2. **Validate:** Count dropped rows and inspect data-quality issues.
3. **Prepare:** Infer the observation frequency and handle missing periods according to the selected policies.
4. **Evaluate:** Compare candidate models using rolling-origin validation and Mean Absolute Scaled Error (MASE).
5. **Forecast:** Generate predictions for the requested horizon with uncertainty bands.
6. **Interpret:** Review trends, seasonality, outlier flags, assumptions, and warnings.
7. **Export:** Download the forecast and accompanying analysis.

## 📄 Input Data Format

Your CSV should contain a `date` column, a numeric `value` column, and optionally a `series` column.

```csv
date,value,series
2026-01-01,1250,Product_A
2026-01-02,1320,Product_A
2026-01-03,1180,Product_A
2026-01-01,840,Product_B
2026-01-02,910,Product_B
2026-01-03,875,Product_B
```

| Column | Required? | Description |
|---|---|---|
| `date` | Yes | Observation date |
| `value` | Yes | Numeric sales or demand value |
| `series` | No | Identifier for separate products, stores, or demand series |

Without a `series` column, the application treats the observations as a single series.

Use consistent dates and meaningful numeric values. The application applies its configured validation, frequency inference, gap-filling, and aggregation policies to the submitted data.

## 🧠 Forecasting Capabilities

| Capability | Purpose |
|---|---|
| Seven candidate models | Compare supported forecasting approaches |
| Rolling-origin backtesting | Evaluate forecasts across historical cutoffs |
| MASE-based selection | Compare model errors against a scaled benchmark |
| Uncertainty bands | Communicate forecast uncertainty by horizon |
| Frequency inference | Identify an appropriate observation interval |
| Gap handling | Apply configured policies to missing periods |
| Outlier detection | Flag observations requiring investigation |
| Decomposition | Inspect supported trend and seasonal patterns |
| Assumptions and warnings | Explain important interpretation limits |

The model-selection procedure chooses among implemented candidates. It does not guarantee that the selected model will outperform every alternative on future observations.

## 🏗️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core forecasting and data-processing logic |
| Pandas | Time-series data manipulation |
| NumPy | Numerical calculations |
| FastAPI | HTTP API |
| HTML, CSS, JavaScript | Browser dashboard and SVG charts |
| pytest / unittest | Automated testing |
| CSV, Markdown, JSON | Data and report exports |

Confirm the precise dependencies against `requirements-dev.txt` and the source files in the repository.

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or a compatible version supported by the project dependencies.
- Git.
- A terminal or command prompt.

### 1. Clone the repository

```bash
git clone https://github.com/rayyan-anwar/business-forecasting-dashboard.git
cd business-forecasting-dashboard
```

If your actual repository name differs, replace the example URL and directory accordingly.

### 2. Create a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

### 4. Run the tests

```bash
python -m pytest -q
```

The committed test report records 18 passing tests. Two API tests were not executed in the original authoring sandbox, so verify the current results in your own environment.

### 5. Launch the dashboard

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8020
```

Open these URLs:

| Resource | URL |
|---|---|
| Browser dashboard | http://127.0.0.1:8020 |
| Interactive API documentation | http://127.0.0.1:8020/docs |
| Health check | http://127.0.0.1:8020/health |
| Application information | http://127.0.0.1:8020/api/info |

Select **Use sample sales data** in the dashboard to explore the application without preparing your own dataset.

## 🔌 API Examples

### Retrieve synthetic sample data

```bash
curl -s http://127.0.0.1:8020/api/sample -o sales.csv
```

### Analyze the sample data

```bash
curl -s "http://127.0.0.1:8020/api/analyze?horizon=14" \
  -H "Content-Type: text/csv" \
  --data-binary @sales.csv
```

The analysis endpoint accepts a CSV request body and supports documented query parameters for frequency, forecast horizon, aggregation, missing-value handling, interval level, and seasonality.

Consult `/docs` for the exact accepted values and request behavior.

## 📥 Export Options

| Format | Intended use |
|---|---|
| CSV | Forecast values for spreadsheets and further analysis |
| Markdown | Readable reports containing analytical findings and caveats |
| JSON | Structured results for downstream tools and integrations |

CSV exports include formula-injection protection. The project is designed not to persist uploaded data, but deployment operators should independently verify logging, proxy, and infrastructure behavior before handling confidential business information.

## 🧪 Testing & Verification

| Verification item | Reported status |
|---|---|
| Core tests | 18 executed and passing |
| Data validation and missing-period handling | Implemented and tested |
| Forecasting model selection | Implemented and tested |
| Uncertainty bands and exports | Implemented and tested |
| API tests | Written but not executed in the original authoring sandbox |
| Docker build | Not verified |
| Ruff linting | Not run |
| Browser JavaScript | Syntax-checked; full browser behavior not verified |

The committed tests also cover dropped-row accounting and a previously fixed issue involving a season length of zero.

## ⚠️ Known Limitations

- Evaluation relies on synthetic data.
- Backtest gains were optimistic relative to held-out results.
- Uncertainty intervals are approximate and based on limited backtesting origins.
- Promotions, pricing, holidays, stock-outs, and other external drivers are not modelled.
- Sparse and intermittent demand may be poorly served.
- Hierarchical and multivariate forecasting are not implemented.
- Forecasts are sensitive to data quality and historical regime changes.
- The application does not implement authentication.

**Before operational use:** Evaluate the application on representative historical business data, compare it with simple baselines, inspect interval coverage, and validate results with domain experts.

## 🛣️ Future Roadmap

Potential extensions, not currently implemented:

- [ ] Holiday and calendar regressors.
- [ ] Promotion and pricing features.
- [ ] Hierarchical forecasts across products and stores.
- [ ] Multivariate forecasting models.
- [ ] Probabilistic forecasting methods.
- [ ] Improved support for intermittent demand.
- [ ] Authentication and access controls.
- [ ] Expanded browser end-to-end tests.
- [ ] Docker build verification and deployment automation.

## 📚 Documentation

| Document | Description |
|---|---|
| [Architecture](docs/ARCHITECTURE.md) | System components and design |
| [Evaluation](docs/EVALUATION.md) | Experimental methodology, results, and caveats |
| [Model Card](docs/MODEL_CARD.md) | Intended use and limitations |
| [Deployment](docs/DEPLOYMENT.md) | Deployment instructions |
| [Results](results/RESULTS.md) | Committed benchmark results |

## 👨‍💻 About the Author

<div align="center">

  <h3>Rayyan Anwar</h3>

  **AI/ML Engineer · Researcher · Technology Manager · Software Developer**

  Building practical data-driven tools at the intersection of machine learning, predictive analytics, scientific research, and software engineering.

  <a href="https://github.com/rayyan-anwar">
    <img src="https://img.shields.io/badge/GitHub-rayyan--anwar-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub Profile" />
  </a>

  <p>
    <a href="https://github.com/rayyan-anwar?tab=repositories">Explore My Repositories</a>
  </p>

</div>

## 📄 License

Released under the **MIT License**.

Copyright © Rayyan Anwar. See [`LICENSE`](LICENSE) for details.

---

<div align="center">

  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:14B8A6,45:0891B2,100:0F172A&height=120&section=footer" width="100%" alt="Decorative animated forecasting footer" />

  **Forecast responsibly. Understand uncertainty. Make better-informed decisions.**

  <sub>Historical patterns are evidence, not promises.</sub>

</div>
