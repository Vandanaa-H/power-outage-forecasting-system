#!/usr/bin/env python3
"""
Quick retrain using only sklearn models for better compatibility.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
import joblib
import os

print("🚀 RETRAINING KARNATAKA MODEL WITH PURE SKLEARN")
print("=" * 60)

# Load dataset
print("📊 Loading Karnataka dataset...")
df = pd.read_csv('data/karnataka_power_outage_dataset.csv')
print(f"✓ Loaded {len(df):,} records")

# Prepare features (same as before)
print("🔧 Preparing features...")
# Use existing columns where available
if 'hour_of_day' not in df.columns:
    df['hour_of_day'] = pd.to_datetime(df['timestamp']).dt.hour
if 'day_of_week' not in df.columns:
    df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
if 'month' not in df.columns:
    df['month'] = pd.to_datetime(df['timestamp']).dt.month
if 'season' not in df.columns:
    df['season'] = df['month'].map({12: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 1, 6: 2, 7: 2, 8: 2, 9: 3, 10: 3, 11: 3})
if 'is_monsoon' not in df.columns:
    df['is_monsoon'] = df['month'].isin([6, 7, 8, 9]).astype(int)
if 'is_summer' not in df.columns:
    df['is_summer'] = df['month'].isin([3, 4, 5]).astype(int)

# City encoding
city_map = {city: i for i, city in enumerate(df['city'].unique())}
df['city_encoded'] = df['city'].map(city_map)

# ESCOM zone encoding
escom_map = {escom: i for i, escom in enumerate(df['escom_zone'].unique())}
df['escom_encoded'] = df['escom_zone'].map(escom_map)

# Feature columns
feature_columns = [
    'temperature', 'humidity', 'wind_speed', 'rainfall', 'lightning_strikes', 'storm_alert',
    'load_factor', 'voltage_stability', 'hour_of_day', 'day_of_week', 'month', 'season',
    'historical_outages', 'feeder_health', 'transformer_load', 'population', 'priority_tier',
    'is_monsoon', 'is_summer', 'city_encoded', 'escom_encoded'
]

# Prepare data
X = df[feature_columns].copy()
y = df['outage_occurred'].astype(int)

print(f"✓ Features: {len(feature_columns)}")
print(f"✓ Outage rate: {y.mean():.1%}")

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print(f"✓ Train: {len(X_train):,}, Test: {len(X_test):,}")

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train models
print("\n🌳 Training Random Forest...")
rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=15,
    min_samples_split=10,
    min_samples_leaf=5,
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train_scaled, y_train)

print("⚡ Training Gradient Boosting...")
gb_model = GradientBoostingClassifier(
    n_estimators=100,
    max_depth=8,
    learning_rate=0.1,
    random_state=42
)
gb_model.fit(X_train_scaled, y_train)

print("🎯 Creating Ensemble...")
ensemble_model = VotingClassifier(
    estimators=[
        ('rf', rf_model),
        ('gb', gb_model)
    ],
    voting='soft'
)
ensemble_model.fit(X_train_scaled, y_train)

# Evaluate
print("\n📈 EVALUATION RESULTS:")
rf_pred = rf_model.predict(X_test_scaled)
rf_proba = rf_model.predict_proba(X_test_scaled)[:, 1]
gb_pred = gb_model.predict(X_test_scaled)
gb_proba = gb_model.predict_proba(X_test_scaled)[:, 1]
ensemble_pred = ensemble_model.predict(X_test_scaled)
ensemble_proba = ensemble_model.predict_proba(X_test_scaled)[:, 1]

print(f"🌳 Random Forest: Acc={accuracy_score(y_test, rf_pred):.3f}, AUC={roc_auc_score(y_test, rf_proba):.3f}")
print(f"⚡ Gradient Boost: Acc={accuracy_score(y_test, gb_pred):.3f}, AUC={roc_auc_score(y_test, gb_proba):.3f}")
print(f"🎯 Ensemble: Acc={accuracy_score(y_test, ensemble_pred):.3f}, AUC={roc_auc_score(y_test, ensemble_proba):.3f}")

# Save model package
print("\n💾 Saving model package...")
os.makedirs("models", exist_ok=True)

model_package = {
    'ensemble_model': ensemble_model,
    'scaler': scaler,
    'feature_columns': feature_columns,
    'city_map': city_map,
    'escom_map': escom_map,
    'model_info': {
        'accuracy': accuracy_score(y_test, ensemble_pred),
        'auc': roc_auc_score(y_test, ensemble_proba),
        'features': len(feature_columns),
        'train_samples': len(X_train)
    }
}

model_path = "models/karnataka_sklearn_model.joblib"
joblib.dump(model_package, model_path)

print(f"✅ Model package saved to: {model_path}")
print(f"📦 Size: {os.path.getsize(model_path) / 1024 / 1024:.1f} MB")

# Test loading
print("\n🔬 Testing model loading...")
loaded_package = joblib.load(model_path)
test_pred = loaded_package['ensemble_model'].predict_proba(X_test_scaled[:1])
print(f"✓ Loaded model test: {test_pred[0][1]*100:.1f}% outage risk")

print("\n🎉 PURE SKLEARN MODEL READY!")
print("This model should load without any import issues.")