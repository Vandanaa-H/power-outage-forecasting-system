"""
Quick accuracy check on a sampled subset of the Karnataka dataset.
Reports Accuracy and ROC-AUC using a lightweight GradientBoosting model.
Non-invasive: does not change any project files or models.
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
from sklearn.ensemble import GradientBoostingClassifier


FEATURES: List[str] = [
    'temperature', 'humidity', 'wind_speed', 'rainfall',
    'lightning_strikes', 'storm_alert', 'load_factor', 'voltage_stability',
    'hour_of_day', 'day_of_week', 'month', 'season',
    'historical_outages', 'transformer_load', 'feeder_health',
    'population', 'priority_tier', 'is_monsoon', 'is_summer'
]


def load_sampled_dataframe(csv_path: Path, sample_rows: int = 100_000) -> pd.DataFrame:
    total_rows = 0
    chunks = []
    for chunk in pd.read_csv(csv_path, chunksize=50_000, low_memory=False):
        chunks.append(chunk)
        total_rows += len(chunk)
        if sum(len(c) for c in chunks) >= sample_rows:
            break
    df = pd.concat(chunks, ignore_index=True)
    return df


def main():
    data_path = Path("data/karnataka_power_outage_dataset.csv")
    if not data_path.exists():
        print(f"[ERROR] Dataset not found: {data_path}")
        return 1

    print("[INFO] Loading sampled data (~up to 100k rows)...")
    df = load_sampled_dataframe(data_path, sample_rows=100_000)
    print(f"[OK] Loaded {len(df):,} rows for quick evaluation")

    # Minimal preprocessing
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    # Encode categorical city/escom minimally using factorize
    if 'city' in df.columns:
        df['city_encoded'] = pd.factorize(df['city'])[0]
    else:
        df['city_encoded'] = 0
    if 'escom_zone' in df.columns:
        df['escom_encoded'] = pd.factorize(df['escom_zone'])[0]
    else:
        df['escom_encoded'] = 0

    local_features = FEATURES + ['city_encoded', 'escom_encoded']
    available = [c for c in local_features if c in df.columns]
    missing = set(local_features) - set(available)
    if missing:
        print(f"[WARN] Missing expected features: {sorted(list(missing))}")

    # Target
    if 'outage_occurred' not in df.columns:
        print("[ERROR] 'outage_occurred' target not found.")
        return 2
    y = df['outage_occurred'].astype(int)

    X = df[available].fillna(0)

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Scale
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    # Model
    clf = GradientBoostingClassifier(
        n_estimators=150, learning_rate=0.08, max_depth=3, random_state=42
    )
    clf.fit(X_train_s, y_train)

    # Evaluate
    y_pred = clf.predict(X_test_s)
    y_proba = clf.predict_proba(X_test_s)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    try:
        auc = roc_auc_score(y_test, y_proba)
    except Exception:
        auc = float('nan')

    print("\n[QUICK ACCURACY]")
    print(f"  Accuracy: {acc:.3f}")
    print(f"  ROC-AUC:  {auc:.3f}")
    print("\n[CLASSIFICATION REPORT]")
    print(classification_report(y_test, y_pred, digits=3))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
