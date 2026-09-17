from pathlib import Path
import argparse, joblib, pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
from .feature_engineering import FEATURE_COLUMNS

def train(csv_path, out_dir="machine_learning/models"):
    df = pd.read_csv(csv_path)
    required = set(FEATURE_COLUMNS + ["traffic_level"])
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    X, y = df[FEATURE_COLUMNS], df["traffic_level"]
    Xtr, Xte, ytr, yte = train_test_split(X,y,test_size=.2,random_state=42,stratify=y)
    models = {
        "random_forest": RandomForestClassifier(n_estimators=200, random_state=42),
        "logistic_regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
    }
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    scores = {}
    for name, model in models.items():
        model.fit(Xtr,ytr)
        pred = model.predict(Xte)
        report = classification_report(yte,pred,output_dict=True,zero_division=0)
        scores[name] = report["weighted avg"]["f1-score"]
        joblib.dump(model, Path(out_dir)/f"{name}.joblib")
        print(name, classification_report(yte,pred,zero_division=0))
    best = max(scores,key=scores.get)
    shutil_src = Path(out_dir)/f"{best}.joblib"
    joblib.dump(joblib.load(shutil_src), Path(out_dir)/"traffic_classifier.joblib")
    print("Selected:", best)

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("csv_path")
    args=p.parse_args()
    train(args.csv_path)
