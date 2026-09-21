"""
Find the best algorithm for the BRFSS2021 diabetes dataset (3-class).
Trains 4 models with class-imbalance handling and ranks them by macro-F1.
"""
import time
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    f1_score, balanced_accuracy_score, accuracy_score, classification_report
)
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier

CSV = "/root/.claude/uploads/f8af793c-17b3-5b18-8d87-5a32de0927a6/5a245d99-diabetes_012_health_indicators_BRFSS2021.csv"

# 1. Load
df = pd.read_csv(CSV)
X = df.drop(columns=["Diabetes_012"])
y = df["Diabetes_012"].astype(int)

# 2. Split (stratified so class ratios are preserved)
X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# scaled copy for logistic regression (trees don't need scaling)
scaler = StandardScaler().fit(X_tr)
X_tr_s, X_te_s = scaler.transform(X_tr), scaler.transform(X_te)

# 3. Models — all told to handle imbalance
models = {
    "LogisticRegression": (
        LogisticRegression(max_iter=1000, class_weight="balanced"),
        (X_tr_s, X_te_s),
    ),
    "RandomForest": (
        RandomForestClassifier(
            n_estimators=300, class_weight="balanced",
            n_jobs=-1, random_state=42
        ),
        (X_tr, X_te),
    ),
    "XGBoost": (
        XGBClassifier(
            n_estimators=400, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            objective="multi:softprob", num_class=3,
            eval_metric="mlogloss", n_jobs=-1, random_state=42,
        ),
        (X_tr, X_te),
    ),
    "LightGBM": (
        LGBMClassifier(
            n_estimators=600, learning_rate=0.05, num_leaves=63,
            class_weight="balanced", n_jobs=-1, random_state=42, verbose=-1,
        ),
        (X_tr, X_te),
    ),
}

# 4. Train + evaluate
rows = []
for name, (model, (Xtr, Xte)) in models.items():
    t = time.time()
    model.fit(Xtr, y_tr)
    pred = model.predict(Xte)
    rows.append({
        "model": name,
        "macro_F1": f1_score(y_te, pred, average="macro"),
        "balanced_acc": balanced_accuracy_score(y_te, pred),
        "accuracy": accuracy_score(y_te, pred),
        "sec": round(time.time() - t, 1),
    })
    print(f"\n=== {name} ===")
    print(classification_report(y_te, pred, digits=3))

# 5. Rank
board = pd.DataFrame(rows).sort_values("macro_F1", ascending=False)
print("\n================ LEADERBOARD (best = highest macro_F1) ================")
print(board.to_string(index=False))
print(f"\n>>> BEST ALGORITHM: {board.iloc[0]['model']}")
