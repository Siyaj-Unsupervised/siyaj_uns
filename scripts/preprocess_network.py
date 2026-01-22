import pandas as pd
import numpy as np
import sys
import os

def clean_data(file_path):
    if not os.path.exists(file_path):
        print(f"خطأ: الملف {file_path} غير موجود!")
        return

    print(f"--- جاري تنظيف: {file_path} ---")
    # قراءة البيانات
    df = pd.read_csv(file_path)
    
    # تنظيف العناوين
    df.columns = df.columns.str.strip()
    
    # معالجة القيم اللانهائية والمفقودة
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)
    
    # فصل الليبل والبيانات الرقمية
    if 'Label' in df.columns:
        labels = df['Label']
        df_numeric = df.select_dtypes(include=[np.number])
        df_final = pd.concat([df_numeric, labels], axis=1)
    else:
        df_final = df.select_dtypes(include=[np.number])
    
    # حفظ الملف الجديد
    output_path = file_path.replace(".csv", "_cleaned.csv")
    df_final.to_csv(output_path, index=False)
    print(f"تم بنجاح! الملف النظيف موجود هنا: {output_path}")

if __name__ == "__main__":
    # إذا كتبتِ مسار في التيرمينال بيأخذه، إذا ما كتبتِ بينظف الاثنين تلقائيًا
    target_file = sys.argv[1] if len(sys.argv) > 1 else 'data/Monday-WorkingHours.pcap_ISCX.csv'
    clean_data(target_file)