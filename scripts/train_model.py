import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.cluster import KMeans
import os

# التأكد من وجود مجلد الموديلات
if not os.path.exists('models'):
    os.makedirs('models')

# 1. تحميل البيانات 
data = pd.read_csv('data/clean/Monday-WorkingHours.pcap_ISCX_cleaned.csv')

# --- الخطوة السحرية: حذف عمود الكلمات (Label) ---
# الموديلات تحتاج أرقام فقط للتدريب
if 'Label' in data.columns:
    X = data.drop(['Label'], axis=1)
    print("🗑️ تم حذف عمود Label لتهيئة البيانات للتدريب.")
else:
    X = data

# 2. تجهيز الموديلات
if_model = IsolationForest(contamination=0.01, random_state=42)
lof_model = LocalOutlierFactor(n_neighbors=20, novelty=True) 
kmeans_model = KMeans(n_clusters=2, random_state=42)

# 3. التدريب (نستخدم X اللي بدون كلمات)
print("⏳ جاري تدريب الموديلات الثلاثة (هذا قد يستغرق دقيقة)...")
if_model.fit(X)
lof_model.fit(X) 
kmeans_model.fit(X)

# 4. حفظ الموديلات
joblib.dump(if_model, 'models/if_model.pkl')
joblib.dump(lof_model, 'models/lof_model.pkl')
joblib.dump(kmeans_model, 'models/kmeans_model.pkl')

print("✅ تم تدريب وحفظ جميع الموديلات بنجاح في مجلد models/")