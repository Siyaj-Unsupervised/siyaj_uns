"""
make_artifacts.py

فايدة هذا الملف:
----------------
هذا السكربت مسؤول عن تثبيت شكل البيانات (Preprocessing)
اللي تتوقعه نماذج الكشف عن الشذوذ في مشروع سياج.

ليش نحتاجه؟
------------
في نظام كشف اختراقات حقيقي، لازم أي بيانات جديدة تدخل للنظام
تتعالج بنفس الطريقة اللي تعالجت فيها بيانات التدريب.
هذا الملف يضمن هالشي عن طريق:

- تحديد الأعمدة الرقمية (Features) المستخدمة فعليًا في التدريب
- تدريب الـScaler على بيانات طبيعية فقط (Monday - Benign)
- حفظ الـScaler وقائمة الأعمدة لاستخدامها لاحقًا في التنبؤ وواجهة المستخدم

وش ينتج؟
--------
- scaler.pkl
  يستخدم لتوحيد القيم بنفس توزيع بيانات التدريب

- feature_columns.json
  يحدد ترتيب وأسماء الأعمدة اللي تتوقعها النماذج

ملاحظات:
---------
- هذا الملف لا يدرّب النماذج نفسها
- يستخدم فقط لضمان الاتساق بين التدريب والتشغيل (Inference)
- ضروري لتشغيل النظام وواجهة Streamlit بشكل صحيح
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# مسار المشروع الأساسي
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# المسارات
CLEAN_DIR = os.path.join(BASE_DIR, "data", "clean")
MODELS_DIR = os.path.join(BASE_DIR, "models")

MONDAY_CLEAN = os.path.join(
    CLEAN_DIR, "Monday-WorkingHours.pcap_ISCX_cleaned.csv"
)

SCALER_PATH = os.path.join(MODELS_DIR, "scaler.pkl")
FEATS_PATH = os.path.join(MODELS_DIR, "feature_columns.json")


def main():
    # تأكد من وجود ملف Monday المنظف
    if not os.path.exists(MONDAY_CLEAN):
        raise FileNotFoundError(
            f"❌ Monday cleaned file not found: {MONDAY_CLEAN}"
        )

    os.makedirs(MODELS_DIR, exist_ok=True)

    # قراءة البيانات
    df = pd.read_csv(MONDAY_CLEAN)

    # Unsupervised: لا نستخدم الليبل
    if "Label" in df.columns:
        df = df.drop(columns=["Label"])

    # نحتفظ فقط بالأعمدة الرقمية
    X = df.select_dtypes(include=[np.number]).copy()

    # تنظيف بسيط وآمن
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median(numeric_only=True))

    # حفظ أسماء الأعمدة (الترتيب مهم)
    feature_columns = list(X.columns)

    # تدريب الـScaler على بيانات طبيعية فقط
    scaler = StandardScaler()
    scaler.fit(X)
 

    # حفظ الـartifacts
    joblib.dump(scaler, SCALER_PATH)

    with open(FEATS_PATH, "w", encoding="utf-8") as f:
        json.dump(feature_columns, f, ensure_ascii=False, indent=2)

    # طباعة تأكيد
    print("✅ Artifacts saved successfully:")
    print(f"- {SCALER_PATH}")
    print(f"- {FEATS_PATH}")


if __name__ == "__main__":
    main()
