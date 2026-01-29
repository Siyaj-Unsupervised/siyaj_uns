from scripts.ensemble import siyaj_predict
import pandas as pd
from scripts.log_parser import parse_log
from analyst_bot import SecurityAnalyst
from scripts.reference_manager import ReferenceManager
from scripts.log_processor import LogProcessor


#def main():
    #print("🚀 جاري تشغيل نظام سياج الموحد...")

    #test_data = pd.read_csv(
       # 'data/clean/Wednesday-WorkingHours.pcap_ISCX_cleaned.csv'
   # ).head(20)

   ## X = test_data.drop(['Label'], axis=1) if 'Label' in test_data.columns else test_data

   # predictions = siyaj_predict(X)

   # test_data['Siyaj_Decision'] = predictions
  #  print(test_data[['Siyaj_Decision']])
def run_soc():

    print("\n🛡️ SIYAJ SOC ENGINE STARTED\n")

    raw_log = """
    ALERT TCP SYN FLOOD detected
    SRC=185.12.10.4 DST=192.168.1.10 PORT=80
    """

    print("📥 Incoming Log:")
    print(raw_log)

    # --------- PRE ML ---------
    processor = LogProcessor()

    X = processor.extract_features(raw_log)
    if X is None:
        print("❌ Log dropped. Unable to extract features.")
        return


    # --------- ML ENGINE ---------
    decision, confidence = siyaj_predict(X)

    if decision[0] == 1:

        print("Confidence:", confidence[0], "%")

        confidence = 92

        # --------- POST ML ---------
        analyst = SecurityAnalyst()
        ref = ReferenceManager()

        explanation = analyst.explain_attack("DoS", confidence)

        mitre = ref.get_mitre_info("Denial of Service")
        recommendation = ref.get_nca_recommendation("DoS")

        print("\n==============================")
        print("🧠 AI ANALYST REPORT")
        print("==============================")
        print(explanation)

        print("\n==============================")
        print("📌 MITRE ATT&CK MAPPING")
        print("==============================")
        print(mitre)

        print("\n==============================")
        print("🇸🇦 NCA RESPONSE GUIDELINES")
        print("==============================")
        print(recommendation)

    else:
        print("\n✅ NORMAL TRAFFIC")


if __name__ == "__main__":
    run_soc()
   # main()
