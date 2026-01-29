 # SIYAJ: Unsupervised NIDS (Ensemble Learning)
### Overview

*SIYAJ (سياج): An Unsupervised Anomaly-based NIDS, specifically designed to detect Zero-day Attacks by analyzing behavioral deviations from normal network patterns, eliminating the need for pre-labeled attack data.*

-------------------------------

### Dataset & Strategy

**We utilized the CIC-IDS2017 dataset with a strategic split to ensure the system’s effectiveness:**

- Training Phase (Monday Data): Models were trained exclusively on Monday’s traffic, which consists only of    Benign (Normal) behavior. This helps the system establish a "Gold Standard" for what is normal.

- Testing Phase (Wednesday Data): We used Wednesday's data, which contains real-world attacks (DoS, etc.), to evaluate how well the system identifies anomalies.
--------------------------------

### Data Preprocessing:

- Cleaned null and infinite values.

- Dropped the 'Label' column during training to ensure a true unsupervised approach.
-------------------------

### The AI Engine (Algorithms)

**SIYAJ uses three distinct algorithms to analyze network traffic from different mathematical perspectives:**

- Isolation Forest: Isolates anomalies by randomly partitioning the data.

- Local Outlier Factor (LOF): Identifies attacks based on how much the data density deviates from its neighbors.

- K-Means Clustering: Groups traffic into clusters to distinguish between normal patterns and outliers.
---------------------------------
### Ensemble Strategy: Majority Voting

**To reduce "False Alarms," we implemented a 2-out-of-3 Majority Voting system:**

- Each of the 3 models gives a verdict: 0 (Normal) or 1 (Attack).

- The final system alert is only triggered if at least two models agree that the traffic is malicious.

-------------------------------
## Intelligent Analysis Layer (LLM Integration)

**To bridge the gap between technical detection and human-readable reports, SIYAJ now includes an AI-Powered Security Analyst:**

- Explainable AI (XAI): We integrated a Generative AI model (DistilGPT2) via the Hugging Face framework to provide natural language explanations for every detected alert.

- Automated Triage: Instead of showing raw alerts, the system generates a concise report explaining the threat's nature (e.g., DoS, Brute Force) and its potential impact on the infrastructure.

- Mitigation Strategy: For every detection, the AI analyst suggests immediate technical fixes (Response), helping security teams act faster without manual research.

- Human-in-the-loop: The LLM acts as a digital assistant, summarizing complex network patterns into actionable insights for the security analyst.
----------------------------------

## 📌 Reference
This project was inspired by the Kaggle notebook “CICIDS2017 - ML Models Comparison: Unsupervised”, which applies unsupervised learning to the CICIDS2017 dataset for network anomaly detection.  
View it here: https://www.kaggle.com/code/ericanacletoribeiro/cicids2017-ml-models-comparison-unsupervised

------------------------------
