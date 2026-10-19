"""Validate, regularise and forecast business time series with automatic model selection by rolling-origin backtest.

Everything the forecast assumes is returned alongside it. Author: Rayyan Anwar
"""
from __future__ import annotations

import io
import math

import numpy as np
import pandas as pd

from .evaluation import conformal_quantiles, mase_scale, metrics, origins, rolling_forecasts
from .models import FORECASTERS, ModelUnavailable

MAX_ROWS, MAX_SERIES = 300_000, 20
FREQS = {"D": ("daily", 7, "D"), "W": ("weekly", 52, "W-SUN"), "M": ("monthly", 12, "MS")}
CANDIDATES = ("naive", "seasonal_naive", "drift", "ses", "holt", "holt_winters", "ridge_lags")
SIMPLICITY = {m: i for i, m in enumerate(CANDIDATES)}


class InputError(ValueError):
    """Invalid data or parameters."""


def load_table(source) -> tuple[pd.DataFrame, dict]:
    """CSV text or DataFrame with columns date, value and optional series. Bad rows are dropped and counted."""
    if isinstance(source, pd.DataFrame):
        df = source.copy()
    else:
        if not isinstance(source, str) or not source.strip():
            raise InputError("CSV is empty")
        try:
            df = pd.read_csv(io.StringIO(source.lstrip("\ufeff")))
        except (pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
            raise InputError(f"could not parse CSV: {exc}") from None
    df.columns = [str(c).strip().lower() for c in df.columns]
    missing = [c for c in ("date", "value") if c not in df.columns]
    if missing:
        raise InputError(f"missing required columns: {missing} (need date, value; optional series)")
    if len(df) > MAX_ROWS:
        raise InputError(f"too many rows ({len(df)}); limit is {MAX_ROWS}")
    n_in = len(df)
    ts = pd.to_datetime(df["date"], errors="coerce", format="mixed")
    val = pd.to_numeric(df["value"], errors="coerce")
    bad_date = ts.isna()
    bad_val = ~np.isfinite(val) & ~bad_date
    keep = ~(bad_date | bad_val)
    out = pd.DataFrame({"date": ts[keep].dt.tz_localize(None) if ts.dt.tz is not None else ts[keep],
                        "series": df["series"].astype(str)[keep] if "series" in df.columns else "total",
                        "value": val[keep].astype(float)}).reset_index(drop=True)
    if out.empty:
        raise InputError("no valid rows after validation")
    return out, {"rows_in": n_in, "rows_kept": int(len(out)), "dropped": {"invalid_date": int(bad_date.sum()), "invalid_value": int(bad_val.sum())},
                 "series": int(out["series"].nunique()), "date_range": [str(out["date"].min().date()), str(out["date"].max().date())],
                 "negative_values": int((out["value"] < 0).sum())}


def infer_freq(dates: pd.Series) -> str:
    d = np.sort(dates.dt.normalize().unique())
    if len(d) < 3:
        raise InputError("need at least 3 distinct dates")
    gap = float(np.median(np.diff(d).astype("timedelta64[D]").astype(float)))
    if gap <= 1.5:
        return "D"
    if 5 <= gap <= 9:
        return "W"
    if 25 <= gap <= 35:
        return "M"
    raise InputError(f"could not infer a daily, weekly or monthly frequency (median gap {gap:.0f} days); set freq explicitly")


def regularise(df: pd.DataFrame, freq: str, agg: str = "sum", missing: str = "zero") -> tuple[pd.Series, dict]:
    if freq not in FREQS:
        raise InputError(f"freq must be one of {list(FREQS)}")
    if agg not in ("sum", "mean"):
        raise InputError("agg must be 'sum' or 'mean'")
    if missing not in ("zero", "interpolate", "ffill"):
        raise InputError("missing must be 'zero', 'interpolate' or 'ffill'")
    s = df.set_index("date")["value"].sort_index()
    rule = FREQS[freq][2]
    grouped = s.resample(rule)
    agg_s = grouped.sum(min_count=1) if agg == "sum" else grouped.mean()
    n_missing = int(agg_s.isna().sum())
    if missing == "zero":
        agg_s = agg_s.fillna(0.0)
    elif missing == "interpolate":
        agg_s = agg_s.interpolate(limit_direction="both")
    else:
        agg_s = agg_s.ffill().bfill()
    rows_per_period = grouped.size()
    return agg_s, {"periods": int(len(agg_s)), "periods_without_data_filled": n_missing, "fill_policy": missing,
                   "periods_with_multiple_rows_aggregated": int((rows_per_period > 1).sum()), "aggregation": agg}


def flag_outliers(y: pd.Series, m: int, z: float = 4.0) -> list[dict]:
    """Periods far from a rolling median (robust z on the residual); flagged, never removed."""
    if len(y) < 14:
        return []
    k = max(5, m if m > 1 else 5) | 1
    resid = y - y.rolling(k, center=True, min_periods=3).median()
    mad = float(np.median(np.abs(resid - resid.median())))
    scale = 1.4826 * mad if mad > 0 else float(resid.std())
    if scale == 0 or not math.isfinite(scale):
        return []
    zs = (resid - resid.median()) / scale
    return [{"date": str(d.date()), "value": float(y[d]), "robust_z": float(zs[d])} for d in zs.index[np.abs(zs) > z]][:20]


def decompose(y: np.ndarray, m: int) -> dict:
    """Simple descriptive decomposition: centred moving-average trend and a mean seasonal profile."""
    k = m if m > 1 else min(7, max(3, len(y) // 10))
    trend = pd.Series(y).rolling(k, center=True, min_periods=1).mean().to_numpy()
    prof = None
    if m > 1 and len(y) >= 2 * m:
        d = y - trend
        prof = [float(np.mean(d[i::m])) for i in range(m)]
    return {"trend": trend.round(4).tolist(), "seasonal_profile": prof, "trend_window": k}


def analyse_series(y: pd.Series, freq: str, h: int, level: float = 0.8, m: int | None = None) -> dict:
    if not 1 <= h <= 60:
        raise InputError("horizon must be in [1, 60]")
    if not 0.5 <= level <= 0.95:
        raise InputError("level must be in [0.5, 0.95]")
    m = FREQS[freq][1] if m is None else m
    if not 1 <= m <= 366:
        raise InputError("season must be in [1, 366]")
    vals = y.to_numpy(float)
    n = len(vals)
    warnings = []
    if n < max(24, h + 12):
        raise InputError(f"only {n} periods: need at least {max(24, h + 12)} for this horizon")
    min_train = max(2 * m + 2, 20, n // 2)
    try:
        orgs = origins(n, h, 6, min_train)
    except ValueError:
        orgs = origins(n, h, 4, max(12, n // 2)) if n - h >= max(12, n // 2) else []
        warnings.append("History is short for backtesting at this horizon; accuracy estimates are rough.")
    if not orgs:
        raise InputError("not enough history to backtest this horizon; shorten the horizon or provide more data")
    if n < 2 * m + 2 and m > 1:
        warnings.append(f"Fewer than two full seasons of history (season length {m}): Holt-Winters and lag models are unavailable; "
                        "only seasonal-naive can capture seasonality.")
    scale = mase_scale(vals[:orgs[0]], m)
    cv, errs, fcs = {}, {}, {}
    for name in CANDIDATES:
        try:
            f, a = rolling_forecasts(vals, m, h, orgs, name)
        except (ModelUnavailable, ValueError):
            continue
        cv[name] = metrics(f, a, scale)
        errs[name] = a - f
    if not cv:
        raise InputError("no model could be fitted on this series")
    best = min(cv, key=lambda k: (round(cv[k]["mase"], 6), SIMPLICITY[k]))
    ref = "seasonal_naive" if "seasonal_naive" in cv and m > 1 else "naive"
    fc = FORECASTERS[best](vals, h, m)
    q = conformal_quantiles(np.abs(errs[best]), level)
    last = y.index[-1]
    off = pd.tseries.frequencies.to_offset(FREQS[freq][2])
    future = pd.date_range(last + off, periods=h, freq=FREQS[freq][2])
    zero_share = float((vals == 0).mean())
    if zero_share > 0.3:
        warnings.append(f"{zero_share:.0%} of periods are zero: intermittent demand is poorly served by these models.")
    if ref in cv and cv[best]["mase"] > 0.97 * cv[ref]["mase"]:
        warnings.append("No meaningful backtest improvement (under 3%) over the seasonal-naive/naive reference; a simple rule may be as good.")
    if len(orgs) < 5:
        warnings.append("Few backtest origins: prediction intervals are approximate.")
    if (fc < 0).any() and (vals >= 0).all():
        warnings.append("Some forecasts are negative although history is non-negative; consider flooring at zero.")
    gain = 100 * (1 - cv[best]["mase"] / cv[ref]["mase"]) if ref in cv and cv[ref]["mase"] > 0 else 0.0
    return {
        "frequency": FREQS[freq][0], "season_length": m, "horizon": h, "periods": n, "model": best, "reference_model": ref,
        "backtest": {"origins": len(orgs), "by_model": {k: {"mase": v["mase"], "mae": v["mae"], "rmse": v["rmse"]} for k, v in cv.items()},
                     "improvement_over_reference_pct": float(gain)},
        "history": {"dates": [str(d.date()) for d in y.index], "values": vals.round(4).tolist()},
        "forecast": {"dates": [str(d.date()) for d in future], "values": fc.round(4).tolist(), "lower": (fc - q).round(4).tolist(),
                     "upper": (fc + q).round(4).tolist(), "level": level},
        "decomposition": decompose(vals, m), "outliers": flag_outliers(y, m), "warnings": warnings,
        "assumptions": [f"Model chosen by lowest MASE over {len(orgs)} rolling backtest origins (ties go to the simpler model).",
                        "The future behaves like the recent past: no promotions, price changes, holidays or supply limits are modelled.",
                        f"Intervals use past absolute errors of the chosen model per horizon ({level:.0%} target); with few origins they are approximate.",
                        f"Seasonality is additive with period {m}.", "Outliers are flagged but kept in the data.",
                        "The backtest gain is an optimistic estimate: picking the best of several models on the same backtest overstates its true advantage."]}


def analyse_table(df: pd.DataFrame, validation: dict, freq: str | None = None, horizon: int = 12, agg: str = "sum",
                  missing: str = "zero", level: float = 0.8, season: int | None = None) -> dict:
    freq = freq or infer_freq(df["date"])
    names = sorted(df["series"].unique())
    if len(names) > MAX_SERIES:
        raise InputError(f"too many series ({len(names)}); limit is {MAX_SERIES}")
    results, errors = {}, {}
    for name in names:
        try:
            y, prep = regularise(df[df["series"] == name], freq, agg, missing)
            results[name] = {**analyse_series(y, freq, horizon, level, season), "preparation": prep}
        except InputError as exc:
            errors[name] = str(exc)
    if not results:
        raise InputError("no series could be forecast: " + "; ".join(f"{k}: {v}" for k, v in errors.items()))
    return {"validation": validation, "frequency": FREQS[freq][0], "series": results, "errors": errors}


def forecast_csv(res: dict) -> str:
    def safe(v):
        return "'" + v if isinstance(v, str) and v[:1] in "=+-@\t\r" else v
    lines = ["series,date,forecast,lower,upper"]
    for name, r in res["series"].items():
        f = r["forecast"]
        for d, v, lo, hi in zip(f["dates"], f["values"], f["lower"], f["upper"]):
            lines.append(f'"{str(safe(name)).replace(chr(34), chr(34) * 2)}",{d},{v},{lo},{hi}')
    return "\n".join(lines) + "\n"


def report_markdown(res: dict) -> str:
    L = ["# Forecast report", "", "Generated by Business Forecasting Dashboard (Rayyan Anwar).", "",
         f"- Frequency: {res['frequency']}; series: {len(res['series'])}; rows kept {res['validation']['rows_kept']} of {res['validation']['rows_in']}"]
    for name, r in res["series"].items():
        b = r["backtest"]
        L += ["", f"## {name}", "", f"- Chosen model: **{r['model']}** (reference: {r['reference_model']}); backtest origins: {b['origins']}",
              f"- Backtest MASE of chosen model: {b['by_model'][r['model']]['mase']:.2f} (improvement over reference: {b['improvement_over_reference_pct']:.0f}%)",
              f"- Next {r['horizon']} periods: first {r['forecast']['values'][0]:.1f} ({r['forecast']['lower'][0]:.1f} to {r['forecast']['upper'][0]:.1f}), "
              f"last {r['forecast']['values'][-1]:.1f} ({r['forecast']['lower'][-1]:.1f} to {r['forecast']['upper'][-1]:.1f})"]
        L += [f"- Warning: {w}" for w in r["warnings"]]
        L += ["", "Assumptions:"] + [f"- {a}" for a in r["assumptions"]]
    return "\n".join(L) + "\n"
