from adtk.detector import GeneralizedESDTestAD
from adtk.visualization import plot
import pandas as pd
from pathlib import Path
import numpy as np
def main():
    df = pd.read_pickle("datasets/prepare/145_UCR_Anomaly_Lab2Cmac011215EPG1_5000_17210_17260.pkl")
    esd_ad = GeneralizedESDTestAD(alpha=0.3)
    anomalies = esd_ad.fit_detect(df["value"])
    Path("results").mkdir(parents=True, exist_ok=True)
    plot(df["value"], anomaly=anomalies, ts_linewidth=1, ts_markersize=3, anomaly_markersize=5, anomaly_color='red',
         anomaly_tag="marker")
    anomalies.to_csv("results/145_UCR_Anomaly_Lab2Cmac011215EPG1_5000_17210_17260.csv", index=False)


if __name__ == '__main__':
    main()