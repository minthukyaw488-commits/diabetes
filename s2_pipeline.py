"""
===========================================================================
 프로젝트 2단계 — 파이썬 ML 파이프라인 (메인 오케스트레이터)
 DB 연동 → 데이터 가져오기 → 검증 → 전처리 → 모델링/튜닝 → 암호화 저장
---------------------------------------------------------------------------
 이 스크립트는 '흐름'만 담당하고, 실제 로직은 모듈로 분리되어 있습니다:
   db_connection.py   연결(환경변수·오류처리)
   data_retrieval.py  SQL 데이터 수집
   data_validation.py 데이터 검증
   preprocessing.py   파생변수·분할
 평가 항목: ① DB연동(10) ② 데이터(20) ③ 전처리(25) ④ 분석/모델링·저장(35)
===========================================================================
"""
import warnings; warnings.filterwarnings("ignore")
import pickle
from cryptography.fernet import Fernet
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import f1_score, accuracy_score, classification_report

from db_connection import get_connection
from data_retrieval import fetch_modeling_data
from data_validation import validate
from preprocessing import add_derived_features, split_data

# ===========================================================================
# ① DB 연동 + ② 데이터 가져오기 + 검증   [평가 10 + 20점]
#    연결은 try/finally 로 '반드시' 닫는다 (오류가 나도 자원 정리).
# ===========================================================================
con = get_connection()
print("① DB 연동 성공 ✅")
try:
    df = fetch_modeling_data(con)
    print(f"② 데이터 가져오기 완료 ✅  shape = {df.shape}")
    passed = validate(con, df)          # 전처리 '전에' 데이터 신뢰성 확인
    if not passed:
        raise SystemExit("검증 실패 — 데이터를 확인한 뒤 다시 실행하세요.")
finally:
    con.close()                         # 연결은 더 쓰지 않으므로 바로 닫음

# ===========================================================================
# ③ 데이터 전처리   [평가 25점]
#    (결측치·범위는 위 검증에서 확인됨 / 여기선 파생변수·분할)
# ===========================================================================
df = add_derived_features(df)           # risk_count (누수 없는 row-wise 변환)
X_tr, X_te, y_tr, y_te = split_data(df) # stratified 분할
print(f"③ 전처리 — risk_count 생성 · 분할 train {len(X_tr):,} / test {len(X_te):,}")

# ===========================================================================
# ④ 모델링 + 튜닝 + 암호화 저장   [평가 35점]
#    불균형 3-class 이므로 scoring = macro-F1
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
    gs = GridSearchCV(model, grid, scoring="f1_macro", cv=3, n_jobs=-1)
    gs.fit(X_tr, y_tr)
    pred = gs.best_estimator_.predict(X_te)
    results[name] = (gs.best_estimator_,
                     f1_score(y_te, pred, average="macro"),
                     accuracy_score(y_te, pred), gs.best_params_)
    print(f"   • {name:13s} macro-F1 = {results[name][1]:.4f} | "
          f"acc = {results[name][2]:.4f} | {results[name][3]}")

best_name = max(results, key=lambda k: results[k][1])
best_model, best_f1, best_acc, _ = results[best_name]
print(f"\n   🏆 최적 모델: {best_name}  (macro-F1 {best_f1:.4f}, acc {best_acc:.4f})")
print("\n   [분류 리포트]")
print(classification_report(y_te, best_model.predict(X_te),
                            target_names=["정상", "전당뇨", "당뇨"]))

# 암호화 저장 (Fernet + pickle)
key = Fernet.generate_key()
with open("best_model.enc", "wb") as f:
    f.write(Fernet(key).encrypt(pickle.dumps(best_model)))
with open("model.key", "wb") as f:
    f.write(key)
print("   💾 저장 완료 → best_model.enc (암호화) + model.key (키)")
print("\n✅ 2단계 파이프라인 완료")
