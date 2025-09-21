"""
Quick Karnataka Model Training - Simplified Version
Creates a basic ensemble model for immediate testing
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score
import joblib
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

print("QUICK KARNATAKA MODEL TRAINING")
print("=" * 50)

# Create models directory
Path("models").mkdir(exist_ok=True)

# Load Karnataka dataset
print("Loading Karnataka dataset...")
data_file = "data/karnataka_power_outage_dataset.csv"

if not os.path.exists(data_file):
    print(f"Dataset not found: {data_file}")
    print("Run: python data/karnataka_data_loader.py")
    exit(1)

df = pd.read_csv(data_file)
print(f"Loaded dataset: {len(df):,} records")
print(f"Outage rate: {df['outage_occurred'].mean():.2%}")

# Prepare features
print("\nPreparing features...")

# Encode categorical variables
le_city = LabelEncoder()
df['city_encoded'] = le_city.fit_transform(df['city'])

le_zone = LabelEncoder()
df['zone_encoded'] = le_zone.fit_transform(df['escom_zone'])

# Extract time features
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)

# Select features for training
feature_columns = [
    'temperature', 'humidity', 'wind_speed', 'rainfall',
    'lightning_strikes', 'storm_alert', 'load_factor', 'voltage_stability',
    'city_encoded', 'zone_encoded', 'hour_of_day', 'day_of_week', 
    'month', 'is_weekend', 'population', 'historical_outages',
    'transformer_load', 'feeder_health', 'is_monsoon', 'is_summer'
]

# Prepare data
X = df[feature_columns].fillna(0)
y = df['outage_occurred']

print(f"Features: {len(feature_columns)} columns")
print(f"Samples: {len(X):,} records")

# Split data
print("\n🔄 Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Training set: {len(X_train):,} samples")
print(f"Test set: {len(X_test):,} samples")

# Scale features
print("\n📏 Scaling features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train ensemble models
print("\n🤖 Training ensemble models...")

# Random Forest
print("🌳 Training Random Forest...")
rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train_scaled, y_train)

# Gradient Boosting
print("Training Gradient Boosting...")
gb_model = GradientBoostingClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42
)
gb_model.fit(X_train_scaled, y_train)

# Create ensemble predictor
class KarnatakaEnsembleModel:
    def __init__(self, rf_model, gb_model, scaler, feature_columns):
        self.rf_model = rf_model
        self.gb_model = gb_model
        self.scaler = scaler
        self.feature_columns = feature_columns
        self.le_city = le_city
        self.le_zone = le_zone
    
    def predict_proba(self, X):
        """Predict outage probabilities."""
        if isinstance(X, list):
            X = np.array(X).reshape(1, -1)
        
        X_scaled = self.scaler.transform(X)
        
        # Get predictions from both models
        rf_proba = self.rf_model.predict_proba(X_scaled)
        gb_proba = self.gb_model.predict_proba(X_scaled)
        
        # Ensemble average
        ensemble_proba = (rf_proba + gb_proba) / 2
        return ensemble_proba
    
    def predict(self, X):
        """Predict outage (binary)."""
        proba = self.predict_proba(X)
        return (proba[:, 1] > 0.5).astype(int)

# Create ensemble
ensemble_model = KarnatakaEnsembleModel(rf_model, gb_model, scaler, feature_columns)

# Evaluate models
print("\nEVALUATING MODELS...")

# Test predictions
rf_pred = rf_model.predict(X_test_scaled)
gb_pred = gb_model.predict(X_test_scaled)
ensemble_pred = ensemble_model.predict(X_test_scaled)

rf_proba = rf_model.predict_proba(X_test_scaled)[:, 1]
gb_proba = gb_model.predict_proba(X_test_scaled)[:, 1]
ensemble_proba = ensemble_model.predict_proba(X_test_scaled)[:, 1]

print("🌳 Random Forest Results:")
print(f"   Accuracy: {accuracy_score(y_test, rf_pred):.3f}")
print(f"   ROC-AUC: {roc_auc_score(y_test, rf_proba):.3f}")

print("Gradient Boosting Results:")
print(f"   Accuracy: {accuracy_score(y_test, gb_pred):.3f}")
print(f"   ROC-AUC: {roc_auc_score(y_test, gb_proba):.3f}")

print("Ensemble Results:")
print(f"   Accuracy: {accuracy_score(y_test, ensemble_pred):.3f}")
print(f"   ROC-AUC: {roc_auc_score(y_test, ensemble_proba):.3f}")

# Feature importance
print("\nTOP FEATURES:")
feature_importance = rf_model.feature_importances_
for i, importance in enumerate(feature_importance):
    if importance > 0.05:  # Show important features
        print(f"   {feature_columns[i]}: {importance:.3f}")

# Save model
print("\n💾 Saving model...")
model_path = "models/karnataka_outage_model.joblib"
joblib.dump(ensemble_model, model_path)

print(f"Model saved to: {model_path}")
print(f"Model size: {os.path.getsize(model_path) / 1024 / 1024:.1f} MB")

# Test prediction example
print("\n🔮 TESTING PREDICTION...")
sample_data = X_test.iloc[0:1].values
prediction = ensemble_model.predict_proba(sample_data)
print(f"Sample prediction: {prediction[0][1]:.3f} outage probability")

print("\nKARNATAKA MODEL TRAINING COMPLETE!")
print("Ready for real-time predictions with weather API integration!")
