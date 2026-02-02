import re
import pandas as pd
import numpy as np

class LogProcessor:
    def __init__(self, expected_features):
        self.expected_features = expected_features
        # نمط مرن لاستخراج البيانات من النص غير المنظم
        self.patterns = {
            'Destination Port': r"PORT:(\d+)",
            'Flow Duration': r"DUR:(\d+)",
            'Total Fwd Packets': r"FWD:(\d+)",
            'Total Backward Packets': r"BACK:(\d+)"
        }

    def extract_features(self, raw_text):
        # إنشاء سطر مليء بالأصفار لكل الـ 78 ميزة
        data = {feat: [0] for feat in self.expected_features}
        df = pd.DataFrame(data)

        # استخراج القيم المتاحة من النص ووضعها في مكانها الصحيح
        for feature, pattern in self.patterns.items():
            match = re.search(pattern, raw_text)
            if match and feature in self.expected_features:
                df[feature] = int(match.group(1))
        
        return df