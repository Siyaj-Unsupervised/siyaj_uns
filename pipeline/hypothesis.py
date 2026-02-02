"""
Attack Hypothesis Layer

This module infers a high-level attack hypothesis based on
behavioral patterns observed in anomaly evidence (top features).

Important notes:
- This is NOT a predictor and does NOT replace ML.
- It provides an interpretable hypothesis for analysts.
- Uncertainty is explicitly handled via the 'Unknown' category.
"""

def infer_attack_hypothesis(top_features, severity):
    """
    Infer attack hypothesis from top contributing features.

    Parameters
    ----------
    top_features : list[str]
        List of feature names contributing most to the anomaly.
    severity : str
        Severity level derived from anomaly score (Low / Medium / High).

    Returns
    -------
    dict
        {
            "type": str,
            "confidence": str,
            "reason": str
        }
    """

    features = set(top_features)

    # --- Reconnaissance / Scanning ---
    recon_indicators = {
        "Destination Port",
        "Flow IAT Mean",
        "Flow IAT Std",
        "Flow IAT Max"
    }

    if features & recon_indicators:
        return {
            "type": "Reconnaissance / Scanning",
            "confidence": "Medium",
            "reason": (
                "Unusual changes in destination ports and inter-arrival times "
                "suggest probing or scanning behavior."
            )
        }

    # --- DoS-like behavior ---
    dos_indicators = {
        "Flow Bytes/s",
        "Flow Packets/s",
        "Fwd Packets/s",
        "Bwd Packets/s"
    }

    if features & dos_indicators:
        return {
            "type": "DoS-like Behavior",
            "confidence": "High" if severity in ["High", "Medium"] else "Low",
            "reason": (
                "High traffic volume or packet rate indicates possible "
                "flooding or denial-of-service behavior."
            )
        }

    # --- Unknown / Unclassified ---
    return {
        "type": "Unknown / Unclassified",
        "confidence": "Low",
        "reason": (
            "The observed behavior does not clearly match known attack patterns "
            "and requires further investigation."
        )
    }