# System Card

Author: Rayyan Anwar

**System:** automated univariate forecasting for business time series with backtest-based model selection, uncertainty bands and a data-quality report.

**Intended use:** planning support where a human reviews the forecast, the warnings and the assumptions. **Not for:** automated purchasing, pricing, staffing or financial reporting without independent validation on your own data; short or intermittent demand series; one-off events.

**Data and privacy:** uploads are processed in memory and not stored; do not upload data you are not allowed to process. Sample data is synthetic.

**Known failure modes:** structural breaks, promotions and holidays are not modelled; short histories make backtests and intervals unreliable (the app warns); backtest gains are optimistic; zero-heavy series are poorly forecast; forecasts can go negative; model choice can flip between uploads; additive seasonality only; no hierarchical reconciliation or external regressors.
