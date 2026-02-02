from datetime import datetime
import numpy as np
import pandas as pd

from pipeline.hypothesis import infer_attack_hypothesis


def build_alert(
    df: pd.DataFrame,
    detect_result: dict,
    index: int,
) -> dict:
    """
    Builds a SOC-style alert from ML detection results.
    """

    score = float(detect_result["if_scores"][index])
    threshold = float(detect_result["threshold"])
    is_anomaly = bool(detect_result["is_anomaly"][index])

    severity = (
        "High" if score < threshold * 0.8
        else "Medium" if score < threshold
        else "Low"
    )

    # نحدد الأعمدة الرقمية فقط
    numeric_df = df.select_dtypes(include=[np.number])
    row_numeric = numeric_df.iloc[index]

    # أهم الخصائص المساهمة في الشذوذ
    top_features = (
        row_numeric.abs()
        .sort_values(ascending=False)
        .head(5)
        .index
        .tolist()
    )

    # 🔍 Attack Hypothesis Layer
    hypothesis = infer_attack_hypothesis(top_features, severity)

    alert = {
        "timestamp": datetime.utcnow().isoformat(),
        "source": "network_flow",
        "summary": "Suspicious network behavior detected"
                   if is_anomaly else "Normal traffic pattern",
        "ml": {
            "model": "Isolation Forest",
            "score": score,
            "threshold": threshold,
            "decision": "anomaly" if is_anomaly else "normal",
            "severity": severity,
        },
        "evidence": {
            "top_features": top_features
        },
        "hypothesis": hypothesis
    }

    return alert
