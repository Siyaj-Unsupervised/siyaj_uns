import joblib
import pandas as pd
import numpy as np

# تحميل الموديلات
if_model = joblib.load('models/if_model.pkl')
lof_model = joblib.load('models/lof_model.pkl')
km_model = joblib.load('models/kmeans_model.pkl')


def siyaj_predict(data):
    data = pd.DataFrame(data, columns=lof_model.feature_names_in_)

    if not isinstance(data, pd.DataFrame):
        raise ValueError("المدخل يجب أن يكون DataFrame")

    p_if = if_model.predict(data)
    p_lof = lof_model.predict(data)
    p_km = km_model.predict(data)

    res_if = np.where(p_if == -1, 1, 0)
    res_lof = np.where(p_lof == -1, 1, 0)

    counts = np.bincount(p_km)
    attack_cluster = np.argmin(counts)
    res_km = np.where(p_km == attack_cluster, 1, 0)

    total_votes = res_if + res_lof + res_km
    final_decision = (total_votes >= 2).astype(int)

    return final_decision


if __name__ == "__main__":
    print("✅ محرك سياج الموحد (Ensemble Engine) جاهز!")
