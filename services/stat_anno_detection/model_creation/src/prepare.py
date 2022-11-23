import pandas as pd


def main():
    df = pd.read_csv("datasets/145_UCR_Anomaly_Lab2Cmac011215EPG1_5000_17210_17260.txt", names=["value"])
    df.index = pd.to_datetime(df.index)
    df.to_pickle("datasets/145_UCR_Anomaly_Lab2Cmac011215EPG1_5000_17210_17260.pkl")

if __name__ == '__main__':
    main()
