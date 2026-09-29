"""
Stage 2 — correlation-based feature selection + model.
1) Correlation of every column with the target.
2) Pick the "relevant columns" (|r| >= 0.15) = highly correlated features.
3) Train logistic regression with (a) ALL features vs (b) SELECTED features,
   and compare — does using only the key columns keep the performance?
Target: diabetes (Diabetes_012 == 2) vs not  (binary classification).
"""
import numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, accuracy_score, roc_auc_score

df = pd.read_csv("diabetes_clean.csv")
df["target"] = (df["Diabetes_012"] == 2).astype(int)
feats_all = [c for c in df.columns if c not in ("Diabetes_012", "target")]

# ---------- 1) correlation with target ----------
corr = df[feats_all + ["target"]].corr()["target"].drop("target")
corr_sorted = corr.reindex(corr.abs().sort_values(ascending=False).index)
print("=== 타깃(당뇨)과의 상관계수 (절댓값 큰 순) ===")
print(corr_sorted.round(3).to_string())

# ---------- 2) select relevant columns ----------
THRESH = 0.15
selected = corr_sorted[corr_sorted.abs() >= THRESH].index.tolist()
print(f"\n=== 선택된 유사(핵심) 열  |r| >= {THRESH}  ({len(selected)}개) ===")
print(", ".join(selected))

# ---------- 3) model: all vs selected ----------
X_all = df[feats_all]; y = df["target"]
Xtr, Xte, ytr, yte = train_test_split(X_all, y, test_size=0.2,
                                      random_state=42, stratify=y)
def run(cols, name):
    sc = StandardScaler().fit(Xtr[cols])
    m = LogisticRegression(max_iter=1000, class_weight="balanced")
    m.fit(sc.transform(Xtr[cols]), ytr)
    p = m.predict(sc.transform(Xte[cols]))
    pr = m.predict_proba(sc.transform(Xte[cols]))[:, 1]
    print(f"\n[{name}]  features={len(cols)}")
    print(f"  accuracy   : {accuracy_score(yte, p):.4f}")
    print(f"  macro-F1   : {f1_score(yte, p, average='macro'):.4f}")
    print(f"  ROC-AUC    : {roc_auc_score(yte, pr):.4f}")

print("\n" + "="*50)
print("모델 비교 — 전체 열 vs 선택된 유사 열")
print("="*50)
run(feats_all, "전체 21개 열")
run(selected,  "선택된 유사 열")
