import re
import pandas as pd

class LogProcessor:

    def __init__(self):

        self.log_pattern = r"SRC[=:](?P<src_ip>[\d\.]+).*DST[=:](?P<dst_ip>[\d\.]+).*PORT[=:](?P<port>\d+)(.*SIZE[=:](?P<size>\d+))?"

    def extract_features(self, raw_line):

        match = re.search(self.log_pattern, raw_line)

        if not match:
            print("⚠️ Log format not recognized")
            return None
        data = match.groupdict()

        size = int(data['size']) if data['size'] else 1000

        features = {
            'Destination Port': int(data['port']),
            'Total Length of Fwd Packets': size,
            'Flow Duration': 5000,
            'Total Fwd Packets': size // 64
        }

        return pd.DataFrame([features])