## SIYAJ: Unsupervised NIDS (Ensemble Learning)
## Overview

# SIYAJ is a Network Intrusion Detection System (NIDS) designed to detect cyber threats using Unsupervised Machine Learning. Unlike traditional systems, SIYAJ doesn't need to be told what an attack looks like; it learns to identify "abnormal" behavior automatically using a collective voting strategy.
-------------------------------

## Dataset & Strategy

# We utilized the CIC-IDS2017 dataset with a strategic split to ensure the system’s effectiveness:

- Training Phase (Monday Data): Models were trained exclusively on Monday’s traffic, which consists only of    Benign (Normal) behavior. This helps the system establish a "Gold Standard" for what is normal.

- Testing Phase (Wednesday Data): We used Wednesday's data, which contains real-world attacks (DoS, Heartbleed, etc.), to evaluate how well the system identifies anomalies.
--------------------------------

## Data Preprocessing:

# Cleaned null and infinite values.

# Dropped the 'Label' column during training to ensure a true unsupervised approach.
-------------------------

## The AI Engine (Algorithms)

# SIYAJ uses three distinct algorithms to analyze network traffic from different mathematical perspectives:

- Isolation Forest: Isolates anomalies by randomly partitioning the data.

- Local Outlier Factor (LOF): Identifies attacks based on how much the data density deviates from its neighbors.

- K-Means Clustering: Groups traffic into clusters to distinguish between normal patterns and outliers.
---------------------------------
## Ensemble Strategy: Majority Voting

# To reduce "False Alarms," we implemented a 2-out-of-3 Majority Voting system:

- Each of the 3 models gives a verdict: 0 (Normal) or 1 (Attack).

- The final system alert is only triggered if at least two models agree that the traffic is malicious.__________________________