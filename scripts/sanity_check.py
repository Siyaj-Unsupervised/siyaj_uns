import os
import json
import joblib
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CLEAN_DIR = os.path.join(BASE_DIR, "data", "clean")
MODELS_DIR = os.path.join(BASE_DIR, "models")

WEDNESDAY_CLEAN = os.path.join(CLEAN_DIR, "Wednesday-WorkingHours.pcap_ISCX_cleaned.csv")

FEATS_PATH = os.path.join(MODELS_DIR, "feature_columns.json")
SCALER_PATH = os.path.join(MODELS_DIR, "scaler.pkl")
IF_MODEL_PATH = os.path.join(MODELS_DIR, "if_model.pkl")


def main():
    for p in [WEDNESDAY_CLEAN, FEATS_PATH, SCALER_PATH, IF_MODEL_PATH]:
        if not os.path.exists(p):
            raise FileNotFoundError(f"❌ File not found: {p}")

    feature_columns = json.load(open(FEATS_PATH, "r", encoding="utf-8"))
    scaler = joblib.load(SCALER_PATH)
    if_model = joblib.load(IF_MODEL_PATH)

    df = pd.read_csv(WEDNESDAY_CLEAN)

    labels = None
    if "Label" in df.columns:
        labels = df["Label"].astype(str).str.strip()

    X = df.drop(columns=["Label"], errors="ignore")

    missing = [c for c in feature_columns if c not in X.columns]
    if missing:
        raise ValueError(f"❌ Missing columns in Wednesday data: {missing[:10]} (first 10 shown)")

    X = X[feature_columns].copy()

    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median(numeric_only=True))

    # Scaling -> keep as DataFrame (to preserve feature names)
    X_scaled = pd.DataFrame(
        scaler.transform(X),
        columns=feature_columns,
        index=X.index
    )

    # IsolationForest score: higher = more normal, lower = more anomalous
    scores = if_model.decision_function(X_scaled)

    # Instead of predict(), use a threshold (SOC-style triage)
    # Example: flag the most anomalous 1% as alerts
    q = 0.01
    threshold = np.quantile(scores, q)
    is_anomaly = scores <= threshold

    print("✅ Sanity check passed!")
    print(f"Rows: {len(X)} | Features: {X.shape[1]}")
    print(f"Scores: min={scores.min():.4f}, max={scores.max():.4f}, mean={scores.mean():.4f}")
    print(f"Threshold (q={q}): {threshold:.4f}")
    print(f"Flagged anomalies (top {int(q*100)}%): {is_anomaly.sum()}")

    if labels is not None:
        print("\nLabel distribution (top):")
        print(labels.value_counts().head(10))

        # Quick view: how many flagged are actually attacks (not BENIGN)
        flagged_labels = labels[is_anomaly]
        attack_rate = (flagged_labels != "BENIGN").mean() if len(flagged_labels) > 0 else 0.0
        print(f"\nAmong flagged anomalies: attack ratio = {attack_rate:.3f}")
        print("Flagged labels (top):")
        print(flagged_labels.value_counts().head(10))


if __name__ == "__main__":
    main()

