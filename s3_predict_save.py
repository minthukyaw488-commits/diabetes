"""
===========================================================================
 프로젝트 3단계 — 저장한 모델로 예측하고 결과를 DB에 저장 (시연용 · 독립 실행)
 ① 암호화 모델 로딩 → ② DB에서 Test Data → ③ 하나씩 예측
 → ④ 결과를 ANALYSIS_RESULT(1단계 테이블)에 저장 → ⑤ 확인
---------------------------------------------------------------------------
 평가 3단계 시연(40점): 모델 로딩 · Test Data 적용 · 결과 Table 저장
 ※ 다른 파일을 import 하지 않는 독립 스크립트 (build_db.py / s2_pipeline.py 와 동일 스타일)
===========================================================================
"""
import warnings; warnings.filterwarnings("ignore")
import pickle
import oracledb
import pandas as pd
from cryptography.fernet import Fernet
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

LABELS = {0: "정상", 1: "전당뇨", 2: "당뇨"}

# ① 2단계에서 저장한 암호화 모델 로딩 -------------------------------------
key = open("model.key", "rb").read()
model = pickle.loads(Fernet(key).decrypt(open("best_model.enc", "rb").read()))
print("① 암호화 모델 로딩 완료:", type(model).__name__)

# ===== DB 접속 (build_db.py / s2_pipeline.py 와 같은 정보로) =====
con = oracledb.connect(
    user="system",
    password="Oracle123",              # <- 너의 비밀번호 (s2_pipeline.py 와 동일하게)
    dsn="localhost:1521/FREEPDB1",
)
try:
    cur = con.cursor()

    # ② DB에서 데이터 가져오기 (patient_id 포함 · ORDER BY 로 순서 고정) ----
    QUERY = """
        SELECT p.patient_id, p.age, p.sex, p.education, p.income,
               p.diabetes_status, p.smoker, p.phys_activity, p.fruits, p.veggies,
               p.hvy_alcohol, p.any_healthcare, p.no_doc_cost,
               h.bmi, h.high_bp, h.high_chol, h.chol_check, h.gen_hlth,
               h.ment_hlth, h.phys_hlth, h.diff_walk, h.stroke, h.heart_disease
        FROM patient p JOIN health_exam h ON p.patient_id = h.patient_id
        ORDER BY p.patient_id
    """
    cur.execute(QUERY)
    cols = [c[0].lower() for c in cur.description]
    df = pd.DataFrame(cur.fetchall(), columns=cols)

    # 파생변수 risk_count (학습 때와 동일)
    df["risk_count"] = (
        df["high_bp"] + df["high_chol"] + df["smoker"]
        + (df["bmi"] >= 30).astype(int)
        + df["heart_disease"] + df["stroke"]
    )

    # ③ 학습 때와 똑같이 분할해 Test Data 확보 (seed 42) -------------------
    pid = df["patient_id"]
    X = df.drop(columns=["diabetes_status", "patient_id"])   # 학습 특징 22개
    y = df["diabetes_status"].astype(int)
    _, X_te, _, y_te, _, pid_te = train_test_split(
        X, y, pid, test_size=0.2, random_state=42, stratify=y)
    pid_te = pid_te.reset_index(drop=True)
    print(f"② Test Data 확보: {len(X_te):,}건 (특징 {X_te.shape[1]}개)")

    # ④ 결과 저장용 컬럼 준비 (ANALYSIS_RESULT 에 predicted_status) --------
    try:
        cur.execute("ALTER TABLE analysis_result ADD (predicted_status NUMBER(1))")
        print("   analysis_result 에 predicted_status 컬럼 추가")
    except oracledb.DatabaseError as e:
        if e.args[0].code != 1430:          # 1430 = 이미 존재
            raise

    # ⑤ Test Data 를 '하나씩' 모델에 적용 → 결과 Table 에 저장 -------------
    preds = model.predict(X_te)              # 예측 (벡터화 = 한 건씩과 동일 결과)
    print("③ 예측 결과를 결과 Table 에 저장 (하나씩)")
    for i, (one_pid, pred) in enumerate(zip(pid_te, preds), 1):
        cur.execute(
            "UPDATE analysis_result SET predicted_status = :1 WHERE patient_id = :2",
            [int(pred), int(one_pid)])
        if i <= 5:                            # 처음 5건은 하나씩 보여주기
            print(f"   환자 {int(one_pid):>6} → 예측 {int(pred)} ({LABELS[int(pred)]})")
        if i % 10000 == 0:
            con.commit(); print(f"   ... {i:,}건 저장")
    con.commit()
    print(f"   ✅ 총 {len(preds):,}건 저장 완료")

    # ⑥ 검증: 저장된 결과 확인 + 정확도 ----------------------------------
    print(f"④ Test 정확도: {accuracy_score(y_te, preds):.3f}")
    cur.execute("""SELECT predicted_status, COUNT(*) FROM analysis_result
                   WHERE predicted_status IS NOT NULL
                   GROUP BY predicted_status ORDER BY predicted_status""")
    print("   결과 Table 에 저장된 예측 분포:")
    for status, cnt in cur.fetchall():
        print(f"     {LABELS[status]}: {cnt:,}건")

    cur.execute("""SELECT patient_id, diabetes_status, predicted_status
                   FROM analysis_result WHERE predicted_status IS NOT NULL
                   FETCH FIRST 5 ROWS ONLY""")
    print("   저장 샘플 (patient_id · 실제 · 예측):")
    for pid_v, actual, predicted in cur.fetchall():
        print(f"     {pid_v} · 실제 {LABELS[actual]} · 예측 {LABELS[predicted]}")
finally:
    con.close()

print("\n✅ 3단계 시연 완료 — 모델 로딩 → Test Data 예측 → 결과 Table 저장")
