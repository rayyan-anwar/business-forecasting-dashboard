# Evaluation

Author: Rayyan Anwar

`python scripts/evaluate.py` writes `results/RESULTS.md`. Real company data was unavailable, so truth comes from a seeded sales generator (three products, weekly and yearly seasonality, growth, gaps, split rows, one spike each).

## Committed run (20 seeds x 3 products = 60 forecasts; train 730 days, forecast the next 28)
| Measure | Value |
|---|---:|
| Held-out MAE vs seasonal naive (mean / median ratio) | 0.94 / 0.93 |
| Forecasts better than seasonal naive | 63% |
| 80% interval coverage on held-out days | 0.85 |
| Selection regret vs the hindsight-best candidate | 10.9% on average; chosen model within 5% of best in 53% of cases |
| Backtest gain the app reports vs reference | 20.9% on average |
| Injected bad rows (50 dates, 40 values) | reported exactly; 32 empty periods filled, matching an independent count |
| 20 series x 730 days end to end | 10 s on one core |

## Findings
- Automatic selection gives a modest real gain: held-out error is about **6% below** seasonal naive on average, and the pipeline beats it in roughly 6 of 10 forecasts.
- **The backtest overstates that gain** (20.9% claimed vs about 6% realised), a winner's-curse effect from picking the best of seven models on six origins. The UI and report therefore label the gain as optimistic.
- Holt-Winters was chosen for most series (41 of 60), consistent with the planted seasonal structure; simple exponential smoothing was chosen when weekly patterns were weak.
- Intervals covered 85% of held-out days against an 80% target: slightly conservative on this synthetic data.

## Caveats
Smooth synthetic data; no promotions, price changes, stock-outs or holidays; held-out days within a series are correlated, so coverage has wide uncertainty; the selection regret and optimism figures depend on the candidate set. Nothing here predicts accuracy on real business data.
