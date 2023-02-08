import pandas as pd
from pathlib import Path

def main():
    df = pd.read_csv("datasets/145_UCR_Anomaly_Lab2Cmac011215EPG1_5000_17210_17260.txt", names=["value"])
    df.index = pd.to_datetime(df.index)
    Path("datasets/prepare").mkdir(parents=True, exist_ok=True)
    df.to_pickle("datasets/prepare/145_UCR_Anomaly_Lab2Cmac011215EPG1_5000_17210_17260.zip", compression="zip")

if __name__ == '__main__':
    main()
