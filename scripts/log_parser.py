import pandas as pd

def parse_log(raw_log):
    """
    Convert raw log text into ML features
    """

    raw_log = raw_log.lower()

    features = {
        "Flow Duration": len(raw_log),
        "Total Fwd Packets": raw_log.count("src"),
        "Total Backward Packets": raw_log.count("dst"),
        "SYN Flag Count": raw_log.count("syn"),
        "ACK Flag Count": raw_log.count("ack")
    }

    df = pd.DataFrame([features])

    return df
