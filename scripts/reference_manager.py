import pandas as pd
import PyPDF2
import os

class ReferenceManager:
    def __init__(self):
        # تحديد مسارات الملفات التي رفعناها في مجلد docs
        self.mitre_path = 'docs/enterprise-attack.csv'
        self.nca_path = 'docs/ECC-Controls-Arabic.pdf'

    def get_mitre_info(self, attack_name):
        """تبحث عن رقم التكتيك T-ID في ملف MITRE"""
        try:
            df = pd.read_csv(self.mitre_path)
            # البحث عن اسم الهجوم في العمود 'name'
            result = df[df['name'].str.contains(attack_name, case=False, na=False)]
            if not result.empty:
                return {
                    'ID': result.iloc[0]['id'],
                    'Description': result.iloc[0]['description'][:150] + "..."
                }
            return "No MITRE mapping found."
        except Exception as e:
            return f"Error reading MITRE: {e}"

    def get_nca_recommendation(self, attack_type):
        """تقرأ الـ PDF وتعطي توصية بناءً على نوع الهجوم"""
        # ربط بسيط بناءً على محتوى وثيقة الهيئة ECC-2:2024
        mapping = {
            "DoS": "ECC-2-12-1 (أمن الشبكات): يجب حماية حدود الشبكة وتدفق البيانات.",
            "Brute Force": "ECC-2-13-1 (إدارة سجلات الأحداث): يجب مراقبة محاولات الدخول الفاشلة.",
            "Normal": "ECC-1-1-2 (حوكمة الأمن السيبراني): الالتزام بالسياسات العامة."
        }
        return mapping.get(attack_type, "ECC-2-14-1 (إدارة الحوادث): يرجى مراجعة ضوابط الاستجابة.")

# كود تجريبي للتأكد أن كل شيء يعمل
if __name__ == "__main__":
    ref = ReferenceManager()
    print("--- تجربة MITRE ---")
    print(ref.get_mitre_info("Brute Force"))
    print("\n--- تجربة NCA ---")
    print(ref.get_nca_recommendation("DoS"))