import os
import json
import joblib
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")

FEATS_PATH = os.path.join(MODELS_DIR, "feature_columns.json")
SCALER_PATH = os.path.join(MODELS_DIR, "scaler.pkl")

IF_PATH = os.path.join(MODELS_DIR, "if_model.pkl")
LOF_PATH = os.path.join(MODELS_DIR, "lof_model.pkl")
KMEANS_PATH = os.path.join(MODELS_DIR, "kmeans_model.pkl")


class Detector:
    """
    Runs the unsupervised ML detectors:
    - Isolation Forest: primary anomaly scoring
    - LOF: local validation (optional)
    - KMeans: cluster context (optional)
    """

    def __init__(self):
        self.feature_columns = json.load(open(FEATS_PATH, "r", encoding="utf-8"))
        self.scaler = joblib.load(SCALER_PATH)

        self.if_model = joblib.load(IF_PATH)
        self.lof_model = joblib.load(LOF_PATH)
        self.kmeans_model = joblib.load(KMEANS_PATH)

    def _prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        X = df.drop(columns=["Label"], errors="ignore").copy()

        # ensure all required columns exist
        missing = [c for c in self.feature_columns if c not in X.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing[:10]} (first 10 shown)")

        X = X[self.feature_columns].copy()

        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(X.median(numeric_only=True))

        X_scaled = pd.DataFrame(
            self.scaler.transform(X),
            columns=self.feature_columns,
            index=X.index
        )
        return X_scaled

    def score(self, df: pd.DataFrame, q: float = 0.01) -> dict:
        """
        Returns anomaly info + triage decision.
        q: quantile threshold for alerting (SOC-style). Example 0.01 => top 1% most anomalous.
        """
        X_scaled = self._prepare(df)

        # IF scores (higher=more normal, lower=more anomalous)
        if_scores = self.if_model.decision_function(X_scaled)

        threshold = float(np.quantile(if_scores, q))
        is_anomaly = if_scores <= threshold

        result = {
            "if_scores": if_scores,
            "threshold": threshold,
            "is_anomaly": is_anomaly,
        }

        # LOF (if trained with novelty=True, it supports decision_function)
        # If your LOF was not trained with novelty=True, this may fail -> we'll handle it later if needed
        try:
            lof_scores = self.lof_model.decision_function(X_scaled)
            result["lof_scores"] = lof_scores
        except Exception:
            result["lof_scores"] = None

        # KMeans cluster id (context)
        try:
            clusters = self.kmeans_model.predict(X_scaled)
            result["cluster"] = clusters
        except Exception:
            result["cluster"] = None

        return result
