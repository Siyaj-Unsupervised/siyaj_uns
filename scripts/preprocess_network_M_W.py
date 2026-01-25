import pandas as pd
import numpy as np
import os

# تحديد مسار المشروع تلقائياً
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_ROW_DIR = os.path.join(BASE_DIR, 'data', 'row')
DATA_CLEAN_DIR = os.path.join(BASE_DIR, 'data', 'clean')


def clean_data(filename):

    file_path = os.path.join(DATA_ROW_DIR, filename)

    if not os.path.exists(file_path):
        print(f"❌ الملف غير موجود: {file_path}")
        return

    print(f"\n--- جاري تنظيف: {filename} ---")

    df = pd.read_csv(file_path)

    # تنظيف الأعمدة
    df.columns = df.columns.str.strip()

    # إزالة القيم الغير صالحة
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)

    # فصل الليبل
    if 'Label' in df.columns:
        labels = df['Label']
        numeric = df.select_dtypes(include=[np.number])
        df_final = pd.concat([numeric, labels], axis=1)
    else:
        df_final = df.select_dtypes(include=[np.number])

    # إنشاء مجلد clean إذا غير موجود (بدون التأثير على الموجود)
    os.makedirs(DATA_CLEAN_DIR, exist_ok=True)

    output_name = filename.replace('.csv', '_cleaned.csv')
    output_path = os.path.join(DATA_CLEAN_DIR, output_name)

    df_final.to_csv(output_path, index=False)

    print(f"✅ تم الحفظ: {output_path}")


if __name__ == "__main__":

    files = [
        'Monday-WorkingHours.pcap_ISCX.csv',
        'Wednesday-workingHours.pcap_ISCX.csv'
    ]

    for f in files:
        clean_data(f)
