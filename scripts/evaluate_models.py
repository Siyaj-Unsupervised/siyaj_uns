import pandas as pd
import joblib
import numpy as np
from sklearn.metrics import classification_report

# 1. تحميل بيانات الاختبار
test_path = 'data/clean/Wednesday-WorkingHours.pcap_ISCX_cleaned.csv'
data_test = pd.read_csv(test_path)

X_test = data_test.drop(['Label'], axis=1)
y_true = [1 if x != 'BENIGN' else 0 for x in data_test['Label']]

# مخزن لحفظ توقعات كل موديل عشان نصوت في الأخير
all_model_predictions = {}

# 2. تقييم كل موديل وحفظ توقعه
models_to_test = {
    "Isolation Forest": "models/if_model.pkl",
    "LOF": "models/lof_model.pkl",
    "K-Means": "models/kmeans_model.pkl"
}

for name, path in models_to_test.items():
    print(f"\n--- 📊 تقييم موديل: {name} ---")
    try:
        model = joblib.load(path)
        preds = model.predict(X_test)
        
        # توحيد النتائج (1 للهجوم، 0 للطبيعي)
        if name == "K-Means":
            y_pred = [1 if x == 1 else 0 for x in preds]
        else:
            y_pred = [1 if x == -1 else 0 for x in preds]
        
        # حفظ التوقع في المخزن
        all_model_predictions[name] = y_pred
        
        print(classification_report(y_true, y_pred))
    except Exception as e:
        print(f"❌ تعذر تقييم {name}: {e}")

# --- 🏆 الجزء الجديد: نظام تصويت الأغلبية (2 من 3) ---
print("\n" + "="*40)
print("🛡️ تقييم نظام سياج الموحد (Ensemble Voting)")
print("="*40)

# تحويل التوقعات لمصفوفة لحساب المجموع
preds_matrix = np.array([
    all_model_predictions["Isolation Forest"],
    all_model_predictions["LOF"],
    all_model_predictions["K-Means"]
])

# إذا كان مجموع الأصوات 2 أو أكثر، القرار النهائي هجوم (1)
final_vote = (np.sum(preds_matrix, axis=0) >= 2).astype(int)

print(classification_report(y_true, final_vote))
print("\n💡 فكرة النظام: لا يتم تأكيد الهجوم إلا بموافقة موديلين على الأقل لتقليل الأخطاء.")