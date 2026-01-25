import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor # تصحيح: شلنا المسافة اللي كانت بين الكلمتين
from sklearn.cluster import KMeans
import os

# التأكد من وجود مجلد الموديلات عشان ما يطلع Error
if not os.path.exists('models'):
    os.makedirs('models')

# 1.تحميل البيانات 
data = pd.read_csv('data/clean/Monday-WorkingHours.pcap_ISCX_cleaned.csv')

# 2. تجهيز الموديلات
if_model = IsolationForest(contamination=0.01, random_state=42)
lof_model = LocalOutlierFactor(n_neighbors=20, novelty=True) # تأكدي من novelty=True عشان نقدر نستخدمه للتوقع لاحقاً
kmeans_model = KMeans(n_clusters=2, random_state=42)

# 3. التدريب
print("⏳ جاري تدريب الموديلات الثلاثة (هذا قد يستغرق دقيقة)...")
if_model.fit(data)
lof_model.fit(data) # الـ LOF هنا بيحفظ نمط البيانات الطبيعية
kmeans_model.fit(data)

# 4. حفظ الموديلات
joblib.dump(if_model, 'models/if_model.pkl')
joblib.dump(lof_model, 'models/lof_model.pkl')
joblib.dump(kmeans_model, 'models/kmeans_model.pkl')

print("✅ تم تدريب وحفظ جميع الموديلات بنجاح في مجلد models/")