import argparse, joblib, pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
from .feature_engineering import FEATURE_COLUMNS

def evaluate(model_path, csv_path):
    model=joblib.load(model_path)
    df=pd.read_csv(csv_path)
    pred=model.predict(df[FEATURE_COLUMNS])
    print(classification_report(df["traffic_level"], pred, zero_division=0))
    print("Confusion matrix:\n", confusion_matrix(df["traffic_level"], pred))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("model_path"); p.add_argument("csv_path")
    a=p.parse_args(); evaluate(a.model_path,a.csv_path)
