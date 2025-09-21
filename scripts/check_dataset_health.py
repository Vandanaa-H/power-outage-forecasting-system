"""
Lightweight dataset health check for data/karnataka_power_outage_dataset.csv.
Reads in chunks to avoid memory issues and prints key stats.
"""

import os
import pandas as pd
from pathlib import Path


def main():
    data_path = Path("data/karnataka_power_outage_dataset.csv")
    if not data_path.exists():
        print(f"[ERROR] Dataset not found: {data_path}")
        print("Run: python data/karnataka_data_loader.py")
        return 1

    print(f"[INFO] Scanning dataset: {data_path}")

    chunksize = 200_000
    total_rows = 0
    outage_count = 0
    min_ts = None
    max_ts = None
    cities = set()
    null_counts = None

    for chunk in pd.read_csv(data_path, chunksize=chunksize, parse_dates=["timestamp"], low_memory=False):
        total_rows += len(chunk)
        outage_count += chunk.get("outage_occurred", pd.Series([0]*len(chunk))).sum()
        cities.update(chunk.get("city", pd.Series(dtype=str)).dropna().unique())

        ts_min = chunk["timestamp"].min() if "timestamp" in chunk.columns else None
        ts_max = chunk["timestamp"].max() if "timestamp" in chunk.columns else None
        if ts_min is not None:
            min_ts = ts_min if min_ts is None else min(min_ts, ts_min)
        if ts_max is not None:
            max_ts = ts_max if max_ts is None else max(max_ts, ts_max)

        # Initialize null_counts on first chunk
        if null_counts is None:
            null_counts = chunk.isna().sum()
        else:
            null_counts += chunk.isna().sum()

    outage_rate = (outage_count / total_rows) if total_rows else 0.0

    print("\n[SUMMARY]")
    print(f"  Rows: {total_rows:,}")
    if min_ts and max_ts:
        print(f"  Date range: {min_ts} → {max_ts}")
    print(f"  Cities: {len(cities)} => {sorted(list(cities))[:10]}{' ...' if len(cities) > 10 else ''}")
    print(f"  Outage rate: {outage_rate:.2%}")

    # Show top nullable columns
    if null_counts is not None:
        top_nulls = null_counts.sort_values(ascending=False).head(10)
        print("\n[NULL COUNTS - TOP 10]")
        for col, cnt in top_nulls.items():
            print(f"  {col}: {int(cnt):,}")

    # Quick schema expectation check
    expected = {
        "timestamp", "city", "latitude", "longitude", "escom_zone", "priority_tier",
        "temperature", "humidity", "wind_speed", "rainfall", "lightning_strikes", "storm_alert",
        "load_factor", "voltage_stability", "historical_outages", "maintenance_status", "feeder_health",
        "transformer_load", "hour_of_day", "day_of_week", "month", "season", "outage_occurred"
    }
    # Read header only to check columns
    header_cols = pd.read_csv(data_path, nrows=0).columns
    missing = expected.difference(set(header_cols))
    if missing:
        print("\n[WARNING] Missing expected columns:")
        for col in sorted(missing):
            print(f"  - {col}")
    else:
        print("\n[OK] Expected schema present.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
