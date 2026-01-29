import re
import pandas as pd

class LogProcessor:
    def __init__(self):
        # النمط لاستخراج البيانات من السجلات الخام (النقطة D)
        # هذا النمط يبحث عن الـ IP والمنفذ وحجم البيانات من سطر نصي
        self.log_pattern = r"SRC:(?P<src_ip>[\d\.]+) DST:(?P<dst_ip>[\d\.]+) PORT:(?P<port>\d+) SIZE:(?P<size>\d+)"

    def extract_features(self, raw_line):
        """تحويل النص الخام إلى أرقام يفهمها الموديل (النقطة B)"""
        match = re.search(self.log_pattern, raw_line)
        if match:
            data = match.groupdict()
            # استخراج الميزات الأساسية برمجياً وتحويلها لجدول
            features = {
                'Destination Port': int(data['port']),
                'Total Length of Fwd Packets': int(data['size']),
                'Flow Duration': 5000,
                'Total Fwd Packets': int(data['size']) // 64
            }
            return pd.DataFrame([features])
        return None

if __name__ == "__main__":
    processor = LogProcessor()
    # تجربة سطر خام (Raw Log) للتأكد من نجاح العملية
    sample_log = "2026-01-29 20:30:00 ALERT SRC:192.168.1.100 DST:10.0.0.5 PORT:80 SIZE:1500"
    
    print("--- Testing Log Processor ---")
    df = processor.extract_features(sample_log)
    if df is not None:
        print("✅ Successfully Extracted Features:")
        print(df)
