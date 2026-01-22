import pandas as pd
import numpy as np

def clean_data(file_path):
    print(f"--- جاري تنظيف: {file_path} ---")
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)
    
    # اختيار الأعمدة الرقمية فقط للنموذج
    df_numeric = df.select_dtypes(include=[np.number])
    
    output_path = file_path.replace(".csv", "_cleaned.csv")
    df_numeric.to_csv(output_path, index=False)
    print(f"تم الحفظ في: {output_path}")

if __name__ == "__main__":
    clean_data('data/Monday-WorkingHours.pcap_ISCX.csv')
