from scripts.ensemble import siyaj_predict
import pandas as pd

def main():
    print("🚀 جاري تشغيل نظام سياج الموحد...")

    test_data = pd.read_csv(
        'data/clean/Wednesday-WorkingHours.pcap_ISCX_cleaned.csv'
    ).head(20)

    X = test_data.drop(['Label'], axis=1) if 'Label' in test_data.columns else test_data

    predictions = siyaj_predict(X)

    test_data['Siyaj_Decision'] = predictions
    print(test_data[['Siyaj_Decision']])

if __name__ == "__main__":
    main()
