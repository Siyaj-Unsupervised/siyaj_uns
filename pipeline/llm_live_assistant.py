import os
import json
from typing import Any, Dict, List

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def _build_prompt(alert: Dict[str, Any], assist_hint: Dict[str, Any], related_texts: List[Dict[str, Any]]) -> str:
    top_feats = alert.get("evidence", {}).get("top_features", [])
    ml = alert.get("ml", {})
    hyp = assist_hint.get("predicted_attack_type", "Unknown")
    conf = assist_hint.get("confidence", "Low")
    reasons = assist_hint.get("reasons", [])

    # small curated snippets (keep short)
    snippets = []
    for t in (related_texts or [])[:3]:
        snippets.append({
            "file": t.get("file"),
            "category": t.get("category"),
            "match_score": t.get("match_score"),
            "snippet": (t.get("snippet") or "")[:500],
        })

    payload = {
        "alert": {
            "summary": alert.get("summary"),
            "score": ml.get("score"),
            "threshold": ml.get("threshold"),
            "severity": ml.get("severity"),
            "decision": ml.get("decision"),
            "top_features": top_feats,
        },
        "hypothesis_hint": {
            "predicted_attack_type": hyp,
            "confidence": conf,
            "reasons": reasons,
        },
        "related_text_intel": snippets,
        "requirements": {
            "language": "Arabic",
            "tone": "SOC analyst assistant",
            "rule": "If uncertain, say Unknown/needs more context (do not hallucinate).",
            "format": "Return ONLY valid JSON.",
        }
    }

    return json.dumps(payload, ensure_ascii=False)


def generate_soc_assistant(alert: Dict[str, Any], assist_hint: Dict[str, Any], related_texts: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Calls an LLM to produce SOC-style explanation + triage + response guidance.
    Returns a dict (JSON).
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "status": "no_api_key",
            "explanation_ar": "لا يوجد OPENAI_API_KEY في البيئة. سيتم استخدام المساعد المحلي فقط.",
            "attack_overview_ar": "",
            "triage_steps": [],
            "recommended_actions": [],
            "confidence": "Low",
            "attack_type": assist_hint.get("predicted_attack_type", "Unknown"),
        }

    client = OpenAI()

    system = (
        "You are a cybersecurity SOC analyst assistant. "
        "You DO NOT invent facts. "
        "You only use given evidence. "
        "If the attack type is uncertain, say it's Unknown and what extra evidence is needed. "
        "Return ONLY JSON with the specified schema."
    )

    user = _build_prompt(alert, assist_hint, related_texts or [])

    # Using Chat Completions (stable + simple)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.3,
    )

    text = resp.choices[0].message.content.strip()

    # try parse JSON
    try:
        data = json.loads(text)
        return data
    except Exception:
        # fallback if model returned extra text
        return {
            "status": "parse_error",
            "raw": text,
            "explanation_ar": "فشل تحويل الرد إلى JSON. راجعي raw.",
            "attack_overview_ar": "",
            "triage_steps": [],
            "recommended_actions": [],
            "confidence": "Low",
            "attack_type": assist_hint.get("predicted_attack_type", "Unknown"),
        }
