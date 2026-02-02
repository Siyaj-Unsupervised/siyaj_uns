from __future__ import annotations
from typing import Dict, List, Tuple


def _infer_attack_and_confidence(top_features: List[str], score: float | None, threshold: float | None) -> Tuple[str, str, List[str]]:
    """
    Returns:
    - predicted_attack_type (hypothesis)
    - confidence (Low/Medium/High)
    - reasons (bullets)
    """
    feats = [f.lower() for f in (top_features or [])]

    has_bytes = any("bytes" in f for f in feats)
    has_packets = any("packets" in f for f in feats)
    has_port = any("port" in f for f in feats)
    has_iat = any("iat" in f for f in feats)

    # Hypothesis rules (simple, explainable)
    if (has_bytes or has_packets) and has_port:
        attack_type = "Possible DoS / Traffic Flooding"
        reasons = [
            "وجود مؤشرات مرتبطة بكثافة المرور (Bytes/s أو Packets/s).",
            "وجود مؤشر مرتبط بالمنافذ (Destination Port) مما يوحي باستهداف خدمة محددة.",
        ]
    elif has_port:
        attack_type = "Possible Scanning / Port-related anomaly"
        reasons = [
            "وجود مؤشر مرتبط بالمنافذ (Destination Port) قد يدل على مسح/استكشاف.",
        ]
    elif has_iat:
        attack_type = "Anomalous Timing Pattern (IAT-related)"
        reasons = [
            "أكثر الخصائص تأثيرًا مرتبطة بزمن التباعد بين الحزم (IAT) مما قد يدل على نمط غير طبيعي/تباطؤ.",
        ]
    else:
        attack_type = "Anomalous Activity"
        reasons = ["الخصائص المؤثرة لا تشير بوضوح لفئة محددة، لكن السلوك خارج نمط الـbaseline."]

    # Confidence logic:
    # 1) Feature evidence strength
    evidence_points = 0
    evidence_points += 1 if (has_bytes or has_packets) else 0
    evidence_points += 1 if has_port else 0
    evidence_points += 1 if has_iat else 0

    # 2) Margin from threshold (if available)
    margin_points = 0
    if score is not None and threshold is not None:
        # anomaly typically when score < threshold in your design
        gap = (threshold - score)
        if gap > 0.02:
            margin_points = 2
            reasons.append(f"فرق واضح بين الدرجة والعتبة (threshold - score = {gap:.4f}).")
        elif gap > 0.005:
            margin_points = 1
            reasons.append(f"فرق متوسط بين الدرجة والعتبة (threshold - score = {gap:.4f}).")
        else:
            reasons.append(f"فرق بسيط بين الدرجة والعتبة (threshold - score = {gap:.4f}).")

    total = evidence_points + margin_points

    if total >= 4:
        confidence = "High"
    elif total >= 2:
        confidence = "Medium"
    else:
        confidence = "Low"

    return attack_type, confidence, reasons


def _playbook(pred_type: str, severity: str) -> Dict[str, List[str]]:
    pred = (pred_type or "").lower()
    sev = (severity or "").lower()

    triage: List[str] = []
    actions: List[str] = []

    if "dos" in pred or "flood" in pred:
        triage = [
            "راجع ارتفاع Packets/s و Bytes/s مقارنة بالـbaseline.",
            "افحص هل السلوك مركز على منفذ/خدمة واحدة (Destination Port).",
            "تحقق من تكرار الحدث خلال آخر 10–30 دقيقة.",
        ]
        actions = [
            "Simulate: Rate-limit / WAF rule (recommended)",
            "Simulate: Escalate severity",
            "Create Incident Report (JSON)",
        ]
    elif "scan" in pred or "port" in pred:
        triage = [
            "افحص تكرار Destination Port وتغيره بزمن قصير.",
            "راجع هل الاتصالات تستهدف منافذ كثيرة بشكل متتابع.",
            "قارن مع سلوك BENIGN المعتاد إن توفر.",
        ]
        actions = [
            "Simulate: Add firewall rule (preview)",
            "Simulate: Escalate severity",
            "Create Incident Report (JSON)",
        ]
    else:
        triage = [
            "راجع الأدلة (top features) لمعرفة سبب الشذوذ.",
            "افحص هل السلوك يتكرر أو يرتبط بخدمة/منفذ محدد.",
            "إن تكرر بشكل كبير، صعّد التنبيه.",
        ]
        actions = [
            "Simulate: Escalate severity",
            "Create Incident Report (JSON)",
        ]

    if sev.lower() == "high":
        triage = ["🚨 (High) " + t for t in triage]
        actions.insert(0, "Simulate: Escalate to Incident")

    return {"triage_steps": triage, "recommended_actions": actions}


def explain_alert(alert: Dict) -> Dict:
    """
    Assistant layer:
    - Builds a readable Arabic explanation from ML outputs (auditable templates)
    - Predicts attack category as a hypothesis (NOT ground truth)
    - Provides confidence + reasons + playbook
    """
    ml = alert.get("ml", {})
    evidence = alert.get("evidence", {})
    top_features = evidence.get("top_features", []) or []

    severity = ml.get("severity", "Low")
    score = ml.get("score", None)
    threshold = ml.get("threshold", None)

    pred_type, confidence, reasons = _infer_attack_and_confidence(top_features, score, threshold)
    playbook = _playbook(pred_type, str(severity))

    explanation = (
        "تم رصد سلوك غير طبيعي في حركة الشبكة بواسطة نموذج كشف الشذوذ (Isolation Forest). "
        f"درجة الشذوذ الحالية = {score:.4f} (العتبة المستخدمة للتنبيه = {threshold:.4f}). "
        f"تم تصنيف الشدة كـ {severity}. "
        f"أكثر المؤشرات تأثيرًا في هذا الحدث: {', '.join(top_features) if top_features else 'غير متوفر'}."
    )

    return {
        "predicted_attack_type": pred_type,
        "confidence": confidence,
        "reasons": reasons,
        "explanation_ar": explanation,
        "triage_steps": playbook["triage_steps"],
        "recommended_actions": playbook["recommended_actions"],
        "disclaimer": "ملاحظة: نوع الهجوم هنا (Predicted) هو فرضية مبنية على heuristics/assistant وليس ground truth من الليبل، والقرار النهائي للمحلل.",
    }
