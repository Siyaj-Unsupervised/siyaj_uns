import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

# 1. تحميل بيانات الاثنين (Unsupervised Learning)
print("Reading Monday's normal data...")
df = pd.read_csv('data/clean/Monday-WorkingHours.pcap_ISCX_cleaned.csv')

# 2. تنظيف البيانات (نختار الخصائص الفنية فقط)
# نتخلص من الأعمدة غير الفنية مثل الـ IP والوقت
# سنفترض أن أول 7 أعمدة هي أعمدة تعريفية (Identification)
X_train = df.iloc[:, 7:] 

# تنظيف البيانات من القيم اللانهائية أو المفقودة
X_train = X_train.replace([float('inf'), float('-inf')], 0).fillna(0)

# 3. بناء الموديل (Anomaly Detector)
# contamination=0.01 تعني أننا نتوقع وجود 1% شذوذ حتى في البيانات الطبيعية
model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)

# 4. التدريب (هنا الموديل يتعلم السلوك الطبيعي فقط)
print("Training the Anomaly Detector (Unsupervised)...")
model.fit(X_train)

# 5. حفظ الموديل
joblib.dump(model, 'scripts/siyaj_anomaly_detector.pkl')
print("Success! The Anomaly Detector is ready.")