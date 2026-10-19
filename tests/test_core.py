"""Tests: validation, regularisation, outliers, model selection, intervals, warnings, exports and API.

Author: Rayyan Anwar
"""
import json
import unittest

import numpy as np
import pandas as pd

from app.business import (InputError, analyse_series, analyse_table, decompose, flag_outliers, forecast_csv, infer_freq,
                          load_table, regularise, report_markdown)
from app.sample import generate_sales


def csv(*rows):
    return "\n".join(("date,value",) + rows)


def seasonal_series(n=300, seed=0, noise=2.0, m=7):
    t = np.arange(n)
    w = np.array([0, -8, -6, -4, 2, 14, 20.0])
    y = 100 + 0.1 * t + w[t % 7] + np.random.default_rng(seed).normal(0, noise, n)
    return pd.Series(y, index=pd.date_range("2024-01-01", periods=n, freq="D"))


class TestLoad(unittest.TestCase):
    def test_valid_and_defaults(self):
        df, rep = load_table(csv("2025-01-01,5", "2025-01-02,7"))
        self.assertEqual(list(df["series"]), ["total", "total"])
        self.assertEqual((rep["rows_kept"], rep["series"], rep["date_range"]), (2, 1, ["2025-01-01", "2025-01-02"]))

    def test_bad_rows_counted_and_failures_raise(self):
        df, rep = load_table(csv("2025-01-01,5", "garbage,3", "2025-01-03,abc", "2025-01-04,inf", "Jan 5 2025,9"))
        self.assertEqual(rep["dropped"], {"invalid_date": 1, "invalid_value": 2})
        self.assertEqual(rep["rows_kept"], 2)
        for bad in ("", "  ", "a,b\n1,2", "date,value", "date,value\nx,y", "date\n2025-01-01"):
            with self.assertRaises(InputError, msg=repr(bad)):
                load_table(bad)

    def test_bom_series_column_and_negatives(self):
        df, rep = load_table("\ufeffdate,value,series\n2025-01-01,-3,A\n2025-01-02,4,B")
        self.assertEqual(rep["series"], 2)
        self.assertEqual(rep["negative_values"], 1)


class TestFrequencyAndRegularise(unittest.TestCase):
    def test_infer_freq(self):
        mk = lambda freq: pd.Series(pd.date_range("2024-01-01", periods=30, freq=freq))
        self.assertEqual(infer_freq(mk("D")), "D")
        self.assertEqual(infer_freq(mk("W-MON")), "W")
        self.assertEqual(infer_freq(mk("MS")), "M")
        with self.assertRaises(InputError):
            infer_freq(mk("100D"))
        with self.assertRaises(InputError):
            infer_freq(pd.Series(pd.to_datetime(["2024-01-01", "2024-01-02"])))

    def make(self):
        return pd.DataFrame({"date": pd.to_datetime(["2025-01-01", "2025-01-01", "2025-01-02", "2025-01-05"]),
                             "series": "s", "value": [10.0, 5.0, 4.0, 8.0]})

    def test_sum_aggregation_and_fill_policies(self):
        s, rep = regularise(self.make(), "D", "sum", "zero")
        self.assertEqual(s.tolist(), [15.0, 4.0, 0.0, 0.0, 8.0])
        self.assertEqual((rep["periods_without_data_filled"], rep["periods_with_multiple_rows_aggregated"]), (2, 1))
        np.testing.assert_allclose(regularise(self.make(), "D", "sum", "interpolate")[0].to_numpy(), [15.0, 4.0, 16 / 3, 20 / 3, 8.0])
        self.assertEqual(regularise(self.make(), "D", "sum", "ffill")[0].tolist(), [15.0, 4.0, 4.0, 4.0, 8.0])
        self.assertEqual(regularise(self.make(), "D", "mean", "zero")[0].tolist()[0], 7.5)

    def test_monthly_and_invalid_options(self):
        df = pd.DataFrame({"date": pd.to_datetime(["2025-01-15", "2025-01-20", "2025-03-02"]), "series": "s", "value": [1.0, 2.0, 5.0]})
        s, _ = regularise(df, "M", "sum", "zero")
        self.assertEqual(s.tolist(), [3.0, 0.0, 5.0])
        for kw in ({"freq": "Y"}, {"agg": "max"}, {"missing": "drop"}):
            with self.assertRaises(InputError):
                regularise(df, **{"freq": "D", **kw})


class TestAnalysis(unittest.TestCase):
    def test_outliers_flagged_not_removed(self):
        y = seasonal_series(120)
        y.iloc[60] += 400
        flagged = flag_outliers(y, 7)
        self.assertEqual([o["date"] for o in flagged], [str(y.index[60].date())])
        self.assertEqual(flag_outliers(y.iloc[:10], 7), [])
        self.assertEqual(flag_outliers(pd.Series(np.full(50, 3.0), index=pd.date_range("2024-01-01", periods=50)), 7), [])

    def test_decompose_recovers_weekly_profile(self):
        t = np.arange(140)
        w = np.array([0, -8, -6, -4, 2, 14, 20.0])
        d = decompose(100 + w[t % 7], 7)
        self.assertAlmostEqual(d["seasonal_profile"][6] - d["seasonal_profile"][1], 28, delta=1.5)
        self.assertIsNone(decompose(np.arange(30.0), 1)["seasonal_profile"])

    def test_selects_seasonal_model_and_forecasts_close_to_truth(self):
        y = seasonal_series(300, seed=1)
        full = seasonal_series(314, seed=1)
        r = analyse_series(y, "D", 14)
        self.assertIn(r["model"], ("holt_winters", "ridge_lags", "seasonal_naive"))
        self.assertGreater(r["backtest"]["improvement_over_reference_pct"], -1)
        mae = np.abs(np.array(r["forecast"]["values"]) - full.values[300:]).mean()
        self.assertLess(mae, 6.0)
        f = r["forecast"]
        self.assertTrue(all(lo <= v <= hi for lo, v, hi in zip(f["lower"], f["values"], f["upper"])))
        self.assertEqual(f["dates"][0], str((y.index[-1] + pd.Timedelta(days=1)).date()))
        json.dumps(r)

    def test_chosen_model_has_lowest_backtest_mase(self):
        r = analyse_series(seasonal_series(300, seed=2), "D", 14)
        self.assertEqual(r["model"], min(r["backtest"]["by_model"], key=lambda k: r["backtest"]["by_model"][k]["mase"]))

    def test_warnings(self):
        monthly = pd.Series(np.arange(24.0) + 10, index=pd.date_range("2023-01-01", periods=24, freq="MS"))
        w = " ".join(analyse_series(monthly, "M", 6)["warnings"])
        self.assertIn("two full seasons", w)
        sparse = seasonal_series(200)
        sparse[np.random.default_rng(0).random(200) < 0.5] = 0.0
        self.assertIn("zero", " ".join(analyse_series(sparse, "D", 7)["warnings"]))

    def test_validation_errors(self):
        y = seasonal_series(100)
        for kw in ({"h": 0}, {"h": 61}, {"level": 0.3}, {"level": 0.99}, {"m": 0}):
            with self.assertRaises(InputError, msg=str(kw)):
                analyse_series(y, "D", **{"h": 7, **kw})
        with self.assertRaises(InputError):
            analyse_series(y.iloc[:20], "D", 7)
        with self.assertRaises(InputError):
            analyse_series(y.iloc[:35], "D", 30)


class TestTableAndExports(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        df, rep = load_table(generate_sales(0, 400).to_csv(index=False))
        cls.res = analyse_table(df, rep, horizon=14)

    def test_all_series_forecast_with_preparation_report(self):
        self.assertEqual(set(self.res["series"]), {"coffee_beans", "mugs", "tea_samplers"})
        p = self.res["series"]["mugs"]["preparation"]
        self.assertGreater(p["periods_without_data_filled"], 0)
        self.assertGreater(p["periods_with_multiple_rows_aggregated"], 0)
        self.assertEqual(self.res["frequency"], "daily")

    def test_spike_is_flagged(self):
        self.assertTrue(any(self.res["series"][k]["outliers"] for k in self.res["series"]))

    def test_csv_and_report(self):
        text = forecast_csv(self.res)
        self.assertEqual(text.splitlines()[0], "series,date,forecast,lower,upper")
        self.assertEqual(len(text.splitlines()), 1 + 3 * 14)
        md = report_markdown(self.res)
        for part in ("# Forecast report", "Assumptions:", "Chosen model"):
            self.assertIn(part, md)

    def test_csv_injection_and_quotes_in_series_names(self):
        res = {"series": {'=HYPERLINK("x")': {"forecast": {"dates": ["2025-01-01"], "values": [1.0], "lower": [0.5], "upper": [1.5]}}}}
        line = forecast_csv(res).splitlines()[1]
        self.assertTrue(line.startswith("\"'="))
        self.assertIn('""x""', line)

    def test_errors_for_short_series_and_series_limit(self):
        rows = [f"2025-01-{d:02d},{d},long" for d in range(1, 29)] + ["2025-01-01,1,tiny", "2025-01-02,2,tiny"]
        long_csv = "date,value,series\n" + "\n".join(rows)
        df, rep = load_table(long_csv)
        r = analyse_table(df, rep, freq="D", horizon=3)
        self.assertEqual(set(r["series"]), {"long"})
        self.assertIn("tiny", r["errors"])
        many = pd.DataFrame({"date": pd.to_datetime(["2025-01-01"] * 21), "series": [f"s{i}" for i in range(21)], "value": 1.0})
        with self.assertRaises(InputError):
            analyse_table(many, {}, freq="D")
        with self.assertRaises(InputError):
            analyse_table(df[df["series"] == "tiny"], rep, freq="D", horizon=3)


class TestSample(unittest.TestCase):
    def test_generator_deterministic_with_quirks(self):
        a, b = generate_sales(1, 200), generate_sales(1, 200)
        pd.testing.assert_frame_equal(a, b)
        self.assertGreater(a.duplicated(["date", "series"]).sum(), 0)
        self.assertLess(len(a), 3 * 200 * 1.02)
        with self.assertRaises(ValueError):
            generate_sales(0, 10)


try:
    import fastapi  # noqa: F401
    import httpx  # noqa: F401
    HAVE_API = True
except ImportError:
    HAVE_API = False


@unittest.skipUnless(HAVE_API, "fastapi/httpx not installed - API tests are skipped, not passed")
class TestApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from fastapi.testclient import TestClient
        from app.main import app
        cls.c = TestClient(app)

    def test_sample_roundtrip(self):
        self.assertEqual(self.c.get("/health").json()["author"], "Rayyan Anwar")
        self.assertIn("Rayyan Anwar", self.c.get("/").text)
        text = self.c.get("/api/sample", params={"n_days": 400}).text
        r = self.c.post("/api/analyze", params={"horizon": 7}, content=text, headers={"content-type": "text/csv"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()["series"]), 3)
        self.assertIn("forecast_csv", r.json())

    def test_errors(self):
        post = lambda content, **p: self.c.post("/api/analyze", params=p, content=content, headers={"content-type": "text/csv"})
        self.assertEqual(post(b"a,b\n1,2").status_code, 422)
        self.assertEqual(post(b"\xff\xfe").status_code, 422)
        self.assertEqual(post(b"x" * 5_000_001).status_code, 413)
        self.assertEqual(post(b"date,value\n2025-01-01,1", horizon=500).status_code, 422)
        self.assertEqual(post(b"date,value\n2025-01-01,1", freq="Q").status_code, 422)


if __name__ == "__main__":
    unittest.main()
