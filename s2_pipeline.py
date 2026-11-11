"""
===========================================================================
 프로젝트 2단계 — 파이썬 ML 파이프라인
 Oracle DB 연동 → 데이터 가져오기 → 전처리 → 모델링/튜닝 → 암호화 저장
---------------------------------------------------------------------------
 평가 항목 커버:
   1) DB 연동        : oracledb 로 1단계 DB 접속
   2) 데이터 가져오기 : 2개 테이블(patient·health_exam) JOIN → DataFrame
   3) 전처리         : 결측치/이상치 확인, 파생변수, 스케일링, 분할
   4) 모델링 + 저장   : RandomForest vs XGBoost 비교 + GridSearch 튜닝
                       → 최적 모델을 암호화(pickle) 파일로 저장
===========================================================================
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import oracledb
import pickle
from cryptography.fernet import Fernet
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import f1_score, accuracy_score, classification_report

# ===========================================================================
# 1) DB 연동  [평가 10점]
# ===========================================================================
con = oracledb.connect(
    user="system",
    password="Oracle123",              # <- 너의 비밀번호
    dsn="localhost:1521/FREEPDB1",
)
print("① DB 연동 성공 ✅")

# ===========================================================================
# 2) 필요 데이터 가져오기  [평가 20점]
#    patient + health_exam 를 patient_id 로 JOIN → 하나의 DataFrame
# ===========================================================================
query = """
    SELECT p.age, p.sex, p.education, p.income,
           p.diabetes_status, p.smoker, p.phys_activity, p.fruits, p.veggies,
           p.hvy_alcohol, p.any_healthcare, p.no_doc_cost,
           h.bmi, h.high_bp, h.high_chol, h.chol_check, h.gen_hlth,
           h.ment_hlth, h.phys_hlth, h.diff_walk, h.stroke, h.heart_disease
    FROM patient p
    JOIN health_exam h ON p.patient_id = h.patient_id
"""
cur = con.cursor()
cur.execute(query)
cols = [c[0].lower() for c in cur.description]
df = pd.DataFrame(cur.fetchall(), columns=cols)
con.close()
print(f"② 데이터 가져오기 완료 ✅  shape = {df.shape}")

# ===========================================================================
# 3) 데이터 전처리  [평가 25점]
# ===========================================================================
# 3-1) 결측치 확인
n_missing = int(df.isna().sum().sum())
print(f"③ 전처리 — 결측치: {n_missing}건", "→ 없음" if n_missing == 0 else "→ 처리 필요")

# 3-2) 이상치 확인 (BMI 는 1단계에서 10~60 으로 정리됨)
print(f"        BMI 범위: {df['bmi'].min()} ~ {df['bmi'].max()}")

# 3-3) 파생변수 생성 — 위험요인 개수 (복합 위험도)
df["risk_count"] = (
    df["high_bp"] + df["high_chol"] + df["smoker"]
    + (df["bmi"] >= 30).astype(int)          # 비만
    + df["heart_disease"] + df["stroke"]
)
print("        파생변수 'risk_count' 생성 (0~6)")

# 3-4) 피처/타깃 분리  (타깃 = 당뇨 분류 0/1/2)
TARGET = "diabetes_status"
X = df.drop(columns=[TARGET])
y = df[TARGET].astype(int)

# 3-5) 학습/테스트 분할 (계층 샘플링으로 클래스 비율 유지)
X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"        분할 완료 — train {X_tr.shape[0]:,} / test {X_te.shape[0]:,}")

# ===========================================================================
# 4) 모델링 + 하이퍼파라미터 튜닝 + 저장  [평가 35점]
#    RandomForest vs XGBoost 를 GridSearch 로 튜닝 → 최적 모델 선택
#    (불균형 3-class 이므로 scoring = macro-F1)
# ===========================================================================
print("④ 모델링 — RandomForest vs XGBoost (GridSearch 튜닝)")

candidates = {
    "RandomForest": (
        RandomForestClassifier(class_weight="balanced", n_jobs=-1, random_state=42),
        {"n_estimators": [200, 300], "max_depth": [None, 20], "min_samples_leaf": [1, 5]},
    ),
    "XGBoost": (
        XGBClassifier(objective="multi:softprob", num_class=3, eval_metric="mlogloss",
                      tree_method="hist", n_jobs=-1, random_state=42),
        {"n_estimators": [300, 500], "max_depth": [4, 6], "learning_rate": [0.05, 0.1]},
    ),
}

results = {}
for name, (model, grid) in candidates.items():
    gs = GridSearchCV(model, grid, scoring="f1_macro", cv=3, n_jobs=-1, verbose=0)
    gs.fit(X_tr, y_tr)
    pred = gs.best_estimator_.predict(X_te)
    f1 = f1_score(y_te, pred, average="macro")
    acc = accuracy_score(y_te, pred)
    results[name] = (gs.best_estimator_, f1, acc, gs.best_params_)
    print(f"   • {name:13s} macro-F1 = {f1:.4f} | acc = {acc:.4f} | {gs.best_params_}")

# 최적 모델 선택 (macro-F1 기준)
best_name = max(results, key=lambda k: results[k][1])
best_model, best_f1, best_acc, best_params = results[best_name]
print(f"\n   🏆 최적 모델: {best_name}  (macro-F1 {best_f1:.4f}, acc {best_acc:.4f})")
print("\n   [분류 리포트]")
print(classification_report(y_te, best_model.predict(X_te),
                            target_names=["정상", "전당뇨", "당뇨"]))

# ---- 암호화 저장 (Fernet + pickle) ----
key = Fernet.generate_key()
fernet = Fernet(key)
encrypted = fernet.encrypt(pickle.dumps(best_model))

with open("best_model.enc", "wb") as f:
    f.write(encrypted)            # 암호화된 모델 파일
with open("model.key", "wb") as f:
    f.write(key)                  # 복호화 키 (따로 보관)

print("   💾 저장 완료 → best_model.enc (암호화) + model.key (키)")
print("\n✅ 2단계 파이프라인 완료")
