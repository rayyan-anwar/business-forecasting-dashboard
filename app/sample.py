"""Seeded synthetic sales generator (daily rows for three products) with gaps, duplicates and one promotion spike.

SYNTHETIC DATA ONLY. Author: Rayyan Anwar
"""
from __future__ import annotations

import numpy as np
import pandas as pd

PRODUCTS = {"coffee_beans": (120, 0.04, [0.9, 0.85, 0.9, 1.0, 1.1, 1.3, 1.25]), "tea_samplers": (60, 0.02, [1.0, 1.0, 1.0, 1.0, 1.05, 1.1, 1.0]),
            "mugs": (30, 0.01, [0.8, 0.8, 0.85, 0.9, 1.1, 1.5, 1.4])}


def generate_sales(seed: int = 0, n_days: int = 730, start: str = "2023-01-01") -> pd.DataFrame:
    if not 90 <= n_days <= 3650:
        raise ValueError("n_days must be in [90, 3650]")
    rng = np.random.default_rng(seed)
    dates = pd.date_range(start, periods=n_days, freq="D")
    t = np.arange(n_days)
    rows = []
    for name, (base, growth, week) in PRODUCTS.items():
        yearly = 1 + 0.25 * np.sin(2 * np.pi * (t - 60) / 365.25)
        mean = base * (1 + growth * t / 30) ** 0.5 * yearly * np.array(week)[t % 7]
        units = rng.poisson(mean)
        spike = int(rng.integers(n_days // 3, n_days - 30))
        units[spike] = int(units[spike] * 5)  # promotion / data-entry spike
        keep = rng.random(n_days) > 0.02  # about 2% of days have no rows at all
        for d, u, k in zip(dates, units, keep):
            if k:
                rows.append((d.strftime("%Y-%m-%d"), name, int(u)))
    df = pd.DataFrame(rows, columns=["date", "series", "value"])
    dup = df.sample(frac=0.01, random_state=seed)  # some transactions arrive as split rows on the same day
    return pd.concat([df, dup], ignore_index=True).sample(frac=1.0, random_state=seed).reset_index(drop=True)
