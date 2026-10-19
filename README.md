# Business Forecasting Dashboard

**Author: Rayyan Anwar** — AI/ML Engineer | Researcher | Technology Manager | Software Developer

Upload sales or demand history (CSV with `date`, `value`, optional `series`) and get, for each series: a data-quality report, automatic frequency detection, a backtested model choice, a forecast with an **uncertainty band**, outlier flags, a trend/seasonality view, plain-language **assumptions and warnings**, and downloads (forecast CSV, Markdown report, JSON). Nothing is stored.

> Forecasts extrapolate past patterns; they are not commitments. Promotions, price changes, holidays and stock-outs are not modelled. Evaluation here uses synthetic data only.

## Implemented vs optional
| Feature | Status |
|---|---|
| Validation with dropped-row counts, frequency inference, gap filling and aggregation policies | Implemented, tested |
| 7 candidate models, rolling-origin selection by MASE, per-horizon conformal-style bands | Implemented, tested |
| Outlier flags, decomposition, warnings, assumptions, CSV/Markdown/JSON exports (formula-injection safe) | Implemented, tested |
| FastAPI service + browser dashboard with SVG charts | Implemented; API tests written but **not executed in the authoring sandbox** |
| External regressors, holidays, hierarchies, multi-variate and probabilistic models, authentication | Not implemented |

## Results (committed run, 60 held-out forecasts, `results/RESULTS.md`)
Held-out error averaged **6% below** seasonal naive (better in 63% of forecasts); 80% intervals covered 85% of held-out days; the model choice was within 5% of the hindsight best in 53% of cases. The in-app backtest gain (about 21% on average) was optimistic, so the UI labels it as such. Injected bad rows and empty periods were counted exactly. See [docs/EVALUATION.md](docs/EVALUATION.md).

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -q
uvicorn app.main:app --port 8020       # http://127.0.0.1:8020 -> "Use sample sales data"
```
`curl -s localhost:8020/api/sample > sales.csv && curl -s "localhost:8020/api/analyze?horizon=14" -H 'content-type: text/csv' --data-binary @sales.csv | head -c 500`

Endpoints: `GET /health`, `/api/info`, `/api/sample`; `POST /api/analyze` (CSV body; query: freq, horizon, agg, missing, level, season); docs at `/docs`.

## Documentation
[Architecture](docs/ARCHITECTURE.md) · [Evaluation](docs/EVALUATION.md) · [System card](docs/MODEL_CARD.md) · [Deployment](docs/DEPLOYMENT.md)

## Testing status
18 tests executed and passing (`python -m unittest`); 2 API tests skipped in the authoring sandbox (FastAPI/httpx unavailable). Tests caught and I fixed a real bug (a season length of 0 was silently ignored). Docker not built; Ruff not run; UI JavaScript syntax-checked only.

## Known limitations
Synthetic evaluation; optimistic backtest gains; approximate intervals with few origins; no external drivers; sparse/intermittent series poorly served; no authentication.

## GitHub repository metadata
- **Description:** Upload business history and get backtested forecasts with uncertainty bands, data-quality reports and explicit assumptions.
- **Topics:** `forecasting`, `demand-forecasting`, `time-series`, `dashboard`, `backtesting`, `pandas`, `fastapi`, `python`

## License
MIT © Rayyan Anwar. See [LICENSE](LICENSE).
