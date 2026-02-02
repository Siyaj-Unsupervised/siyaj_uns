import os
import sys
import json
import io
from datetime import datetime

import pandas as pd
import streamlit as st


def build_incident_payload(alert, hypo, llm_out=None):
    return {
        "created_at": datetime.utcnow().isoformat(),
        "alert": alert,
        "assistant": {
            "hypothesis": hypo,
            "chat": llm_out or {}
        }
    }

# ------------------------------------------------------------------
# Ensure project root on PYTHONPATH
# ------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from pipeline.detect import Detector
from pipeline.alerts import build_alert
from pipeline.llm_assistant import explain_alert

# Actions (optional safety)
try:
    from pipeline.actions import create_incident_report
except Exception:
    create_incident_report = None

# Hypothesis layer (optional)
try:
    from pipeline.hypothesis import infer_attack_hypothesis
except Exception:
    infer_attack_hypothesis = None

# OpenAI (optional)
OPENAI_AVAILABLE = True
try:
    from openai import OpenAI
except Exception:
    OPENAI_AVAILABLE = False


# ------------------------------------------------------------------
# Page config (browser title)
# ------------------------------------------------------------------
PAGE_TITLE = "سياج – بصيرة الأمن السيبراني الوطني | Siyaj: National Cyber Defense with AI Insight"

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon="🛡️",
    layout="wide",
)

# ------------------------------------------------------------------
# Global CSS (background + fonts + professional UI)
# ------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"]  {
  font-family: 'Tajawal', 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif !important;
}

/* App background (main page) */
div[data-testid="stAppViewContainer"] {
  background: #334a85;
}

/* Make inner blocks readable */
.block-container {
  padding-top: 0.8rem;
  padding-bottom: 2rem;
}

/* Default text color on blue background */
p, li, span, label, div {
  color: rgba(255,255,255,0.88);
}

/* Default headings on blue background */
h1, h2, h3 {
  letter-spacing: 0.2px;
  color: rgba(255,255,255,0.96) !important;
}

/* ====== WHITE TOP HEADER AREA (like split page) ======
   This styles the FIRST container (top area) to look like a white header.
   It usually works because your header content is the first block in the app.
*/
div[data-testid="stVerticalBlock"]:first-child {
  background: rgba(255,255,255,0.98);
  border-radius: 18px;
  padding: 18px 18px 10px 18px;
  box-shadow: 0 10px 28px rgba(0,0,0,0.18);
  border: 1px solid rgba(0,0,0,0.06);
}

/* Title colors inside the top header */
div[data-testid="stVerticalBlock"]:first-child h1,
div[data-testid="stVerticalBlock"]:first-child h2,
div[data-testid="stVerticalBlock"]:first-child h3 {
  color: #1f3a8a !important;   /* Blue title */
}

/* Text inside top header becomes dark */
div[data-testid="stVerticalBlock"]:first-child p,
div[data-testid="stVerticalBlock"]:first-child li,
div[data-testid="stVerticalBlock"]:first-child span,
div[data-testid="stVerticalBlock"]:first-child div,
div[data-testid="stVerticalBlock"]:first-child label,
div[data-testid="stVerticalBlock"]:first-child .stCaption {
  color: rgba(15,23,42,0.88) !important; /* dark slate */
}

/* Make the horizontal divider look subtle */
hr {
  border: none;
  height: 1px;
  background: rgba(255,255,255,0.18);
  margin: 18px 0;
}

/* Cards feel for metrics */
div[data-testid="metric-container"]{
  border: 1px solid rgba(255,255,255,0.14);
  padding: 14px;
  border-radius: 16px;
  background: rgba(0,0,0,0.18);
}

/* Dataframe container */
div[data-testid="stDataFrame"] {
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.14);
}

/* Buttons */
.stButton>button {
  border-radius: 14px;
  padding: 0.6rem 1rem;
  border: 1px solid rgba(255,255,255,0.20);
  background: rgba(0,0,0,0.20);
  color: rgba(255,255,255,0.92);
}
.stButton>button:hover {
  border: 1px solid rgba(255,255,255,0.35);
  background: rgba(0,0,0,0.28);
}

/* Sidebar style */
section[data-testid="stSidebar"] {
  background: rgba(0,0,0,0.18);
  border-right: 1px solid rgba(255,255,255,0.10);
}

/* Hide Streamlit header */
header { visibility: hidden; height: 0px; }

/* Alert boxes */
div[data-testid="stAlert"] {
  border-radius: 14px;
}
</style>
""",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# Header with logo (bigger + neat)
# ------------------------------------------------------------------
logo_path = os.path.join(BASE_DIR, "app", "assets", "siyaj_logo.png")

left, right = st.columns([0.78, 0.22], vertical_alignment="center")

with left:
    st.markdown("## سياج – بصيرة الأمن السيبراني الوطني")
    st.markdown("### Siyaj: National Cyber Defense with AI Insight")
    st.caption(
        "نظام كشف شذوذ يساعد محلل الأمن على الفهم، التقييم، واتخاذ القرار "
        "(Human-in-the-loop — بدون أتمتة خطرة)."
    )

with right:
    if os.path.exists(logo_path):
        st.image(logo_path, width=280)  # كبرناه
    else:
        st.caption("ضع الشعار هنا: app/assets/siyaj_logo.png")

st.markdown("---")

# ------------------------------------------------------------------
# Sidebar – Settings
# ------------------------------------------------------------------
st.sidebar.header("⚙️ إعدادات الكشف")

q = st.sidebar.slider(
    "نسبة التنبيهات (Top % Anomalies)",
    min_value=0.001,
    max_value=0.05,
    value=0.01,
    step=0.001,
)

sample_size = st.sidebar.selectbox(
    "حجم العينة (لتسريع العرض)",
    [20000, 50000, 100000, 200000, "ALL"],
    index=1,
)

max_alerts = st.sidebar.slider(
    "عدد التنبيهات المعروضة",
    min_value=50,
    max_value=300,
    value=150,
    step=50,
)

st.sidebar.markdown("---")

enable_ai = st.sidebar.checkbox(
    "تفعيل Chat AI (اختياري)",
    value=True,
    help="إذا توفر مفتاح + رصيد يطلع شرح ذكي. إذا لا، يرجع لشرح آمن بدون ما يخرب النظام."
)

model_name = st.sidebar.text_input("Model", value="gpt-4o-mini")



# ------------------------------------------------------------------
# Data + Detector
# ------------------------------------------------------------------
DATA_PATH = os.path.join(BASE_DIR, "data", "clean", "Wednesday-WorkingHours.pcap_ISCX_cleaned.csv")

@st.cache_data(show_spinner=False)
def load_data(n):
    df_ = pd.read_csv(DATA_PATH)
    if n != "ALL":
        df_ = df_.sample(n=int(n), random_state=42).reset_index(drop=True)
    return df_

@st.cache_resource(show_spinner=False)
def load_detector():
    return Detector()

if not os.path.exists(DATA_PATH):
    st.error(f"❌ Data file not found: {DATA_PATH}")
    st.stop()

df = load_data(sample_size)
detector = load_detector()

with st.spinner("Running anomaly detection..."):
    result = detector.score(df, q=q)

anomaly_idx = result["is_anomaly"].nonzero()[0]
total_alerts = len(anomaly_idx)

# ------------------------------------------------------------------
# Dashboard
# ------------------------------------------------------------------
st.markdown("### 📊 لوحة المؤشرات")
m1, m2, m3 = st.columns(3)
m1.metric("عدد السجلات", f"{len(df):,}")
m2.metric("عدد التنبيهات", f"{total_alerts:,}")
m3.metric("Threshold (q)", f"{q:.3f}")

st.markdown("---")

# ------------------------------------------------------------------
# Alerts list
# ------------------------------------------------------------------
st.subheader("🚨 التنبيهات المكتشفة")

if total_alerts == 0:
    st.info("لا يوجد تنبيهات عند هذه الإعدادات.")
    st.stop()

rows = []
threshold_val = float(result["threshold"])

for i in anomaly_idx[:max_alerts]:
    score = float(result["if_scores"][i])
    sev = "High" if score < threshold_val * 0.8 else "Medium" if score < threshold_val else "Low"
    rows.append({"alert_id": int(i), "score": round(score, 4), "severity": sev})

alerts_df = pd.DataFrame(rows).sort_values("score").reset_index(drop=True)

selected_id = st.selectbox(
    "اختر تنبيه",
    alerts_df["alert_id"].tolist(),
    format_func=lambda x: f"Alert #{x}",
)

st.dataframe(alerts_df, use_container_width=True, hide_index=True)

# ------------------------------------------------------------------
# Build alert + assistant baseline
# ------------------------------------------------------------------
alert = build_alert(df, result, int(selected_id))
assist = explain_alert(alert)

# ------------------------------------------------------------------
# Hypothesis (robust normalization)
# ------------------------------------------------------------------
def _normalize_hypothesis_output(out):
    """
    Supports:
    - dict: {"label":..., "confidence":..., "why":...}
    - tuple/list: (label, confidence, why?) or (label, confidence)
    - str: label
    """
    if out is None:
        return {"label": "Unknown", "confidence": "Low", "why": "لا يوجد سياق كافٍ لاستنتاج نوع الهجوم."}

    if isinstance(out, dict):
        return {
            "label": out.get("label", out.get("attack", out.get("type", "Unknown"))),
            "confidence": out.get("confidence", "Low"),
            "why": out.get("why", out.get("reason", "تم الاستدلال بناءً على الخصائص الأكثر تأثيرًا.")),
        }

    if isinstance(out, (tuple, list)):
        if len(out) == 0:
            return {"label": "Unknown", "confidence": "Low", "why": "لا يوجد سياق كافٍ لاستنتاج نوع الهجوم."}
        if len(out) == 1:
            return {"label": str(out[0]), "confidence": "Low", "why": "تم الاستدلال بناءً على الخصائص الأكثر تأثيرًا."}
        if len(out) == 2:
            return {"label": str(out[0]), "confidence": str(out[1]), "why": "تم الاستدلال بناءً على الخصائص الأكثر تأثيرًا."}
        return {"label": str(out[0]), "confidence": str(out[1]), "why": str(out[2])}

    if isinstance(out, str):
        return {"label": out, "confidence": "Low", "why": "تم الاستدلال بناءً على الخصائص الأكثر تأثيرًا."}

    return {"label": "Unknown", "confidence": "Low", "why": "ناتج غير متوقع من طبقة الاستدلال."}


def safe_hypothesis(alert_obj):
    top_features = alert_obj.get("evidence", {}).get("top_features", [])
    severity = alert_obj.get("ml", {}).get("severity", "Low")

    # Basic safety
    if not isinstance(top_features, list):
        top_features = list(top_features) if top_features else []

    # If no hypothesis function, fallback to assistant guess
    if infer_attack_hypothesis is None:
        return {
            "label": assist.get("predicted_attack_type", "Unknown"),
            "confidence": assist.get("confidence", "Low"),
            "why": "لا يوجد منطق Hypothesis مخصص — تم استخدام تقدير المساعد."
        }

    try:
        out = infer_attack_hypothesis(top_features, severity)
        hypo_obj = _normalize_hypothesis_output(out)

        # If label still unknown, give a clearer why
        if str(hypo_obj.get("label", "")).strip().lower() in ("unknown", "n/a", ""):
            hypo_obj["why"] = "الخصائص الحالية لا تطابق نمطًا واضحًا لهجوم معروف — تحتاج سياق أكثر (IP/Ports/Counts/Time-window)."

        return hypo_obj

    except Exception:
        return {
            "label": assist.get("predicted_attack_type", "Unknown"),
            "confidence": assist.get("confidence", "Low"),
            "why": "تعذر تشغيل منطق Hypothesis — تم استخدام تقدير المساعد."
        }

hypo = safe_hypothesis(alert)



# ------------------------------------------------------------------
# Main banner (clean)
# ------------------------------------------------------------------
st.error(
    f"🚨 Suspicious Activity Detected\n\n"
    f"**Hypothesis:** {hypo['label']}  \n"
    f"**Confidence:** {hypo['confidence']}  \n"
    f"**Severity:** {alert['ml']['severity']}"
)

st.success(f"✅ Why this hypothesis?\n\n{hypo['why']}")

st.markdown("### 🔎 Evidence (Top Features)")
st.write(", ".join(alert["evidence"]["top_features"]))

st.markdown("---")

# ------------------------------------------------------------------
# Tabs (NO Developer / NO Related Text / NO Evaluation)
# ------------------------------------------------------------------
tab1, tab2 = st.tabs(["🧠 Analyst Assistant", "🛠️ Actions"])

# ================= ASSISTANT =================
with tab1:
    st.markdown("### 🧠 الشرح والتحليل")

    def rules_explain():
        st.write(
            f"تم رصد سلوك غير طبيعي باستخدام نموذج كشف الشذوذ (Unsupervised). "
            f"الفرضية الحالية: **{hypo['label']}** (ثقة: {hypo['confidence']})."
        )
        st.markdown("**خطوات Triage مقترحة:**")
        steps = assist.get("triage_steps", []) or [
            "راجع الخصائص (Top Features) لمعرفة سبب الشذوذ.",
            "تحقق هل يتكرر الحدث خلال نافذة زمنية قصيرة.",
            "قارن مع baseline أو BENIGN إن توفر.",
            "إذا تكرر كثيرًا: صعّد التنبيه وابدأ إجراءات احترازية."
        ]
        for s in steps:
            st.write(f"- {s}")

    if enable_ai:
        try:
            api_key = os.getenv("OPENAI_API_KEY", "").strip()
            if not api_key or not OPENAI_AVAILABLE:
                raise RuntimeError("Chat AI غير متاح (لا يوجد مفتاح أو مكتبة).")

            client = OpenAI(api_key=api_key)

            prompt = f"""
أنت مساعد محلل SOC.
اكتب شرحًا عربيًا مهنيًا ومختصرًا للتنبيه.
المطلوب:
1) ماذا يعني هذا التنبيه؟
2) لماذا هذه الفرضية؟ (بدون ادعاء يقيني)
3) خطوات triage عملية (3-6 نقاط)
4) إذا كانت الفرضية Unknown قل إن السياق غير كافٍ وحدد ما البيانات الناقصة.

Alert ML:
{json.dumps(alert.get("ml", {}), ensure_ascii=False)}

Hypothesis:
{json.dumps(hypo, ensure_ascii=False)}

Evidence (Top Features):
{json.dumps(alert.get("evidence", {}), ensure_ascii=False)}
"""

            resp = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.25,
            )

            st.caption("Source: Chat AI")
            st.write(resp.choices[0].message.content)

        except Exception:
            # IMPORTANT: do not break app if quota/429 happens
            st.caption("Chat AI غير متاح الآن — تم استخدام الشرح الآمن (Rules fallback).")
            rules_explain()
    else:
        rules_explain()

    st.caption("⚠️ القرار النهائي بيد المحلل — سياج نظام مساعد فقط.")

# ================= ACTIONS =================
with tab2:
    st.markdown("### 🛠️ إجراءات مقترحة (محاكاة)")

    col1, col2 = st.columns(2)

    with col1:
     if st.button("📄 إنشاء Incident Report"):
        out_dir = os.path.join(BASE_DIR, "data", "actions")
        os.makedirs(out_dir, exist_ok=True)
        payload = build_incident_payload(alert, hypo, llm_out if "llm_out" in globals() else None)
        filename = f"incident_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        path = os.path.join(out_dir, filename)

        # 1) حفظ داخل المشروع
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        st.success(f"✅ تم حفظ التقرير داخل المشروع: {path}")


        # 3) Download للجهاز
        json_bytes = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        st.download_button(
            label="⬇️ Download Incident Report (JSON)",
            data=json_bytes,
            file_name=filename,
            mime="application/json"
        )

    with col2:
        if st.button("🧱 Firewall Rule (Preview)"):
            st.code(
                f"""# Firewall Preview (Template)
# Hypothesis: {hypo['label']} | Confidence: {hypo['confidence']}
action: rate_limit
target: destination_port
window: 60s
limit: 1000 req/min
notes: review with SOC analyst before applying
""",
                language="yaml",
            )