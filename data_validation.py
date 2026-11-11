"""
data_validation.py — 가져온 데이터가 믿을 만한지 검증 (전처리 전에 실행)
---------------------------------------------------------------------------
검사 항목
  1. SQL 결과(행 수) ↔ pandas DataFrame 일치   (데이터 누락 없는지)
  2. 참조 무결성 (orphan 건강검사 = 0)
  3. 결측치 수
  4. 중복 행 수 (BRFSS는 유효 응답으로 유지 → 실패 아님, 보고만)
  5. 임상 변수 유효 범위 (BMI 10~60, diabetes 0~2, 이진 변수 0/1 등)
각 항목을 PASS/FAIL 로 출력하고, 통과 여부를 bool 로 돌려준다.
"""
from data_retrieval import table_counts, count_orphan_exams

# 변수별 허용 범위 (실제 코드북 기준)
RANGES = {
    "diabetes_status": (0, 2), "bmi": (10, 60), "gen_hlth": (1, 5),
    "age": (1, 13), "education": (1, 6), "income": (1, 11),
    "ment_hlth": (0, 30), "phys_hlth": (0, 30),
}
BINARY = ["high_bp", "high_chol", "chol_check", "smoker", "stroke",
          "heart_disease", "phys_activity", "fruits", "veggies",
          "hvy_alcohol", "any_healthcare", "no_doc_cost", "diff_walk", "sex"]


def validate(con, df):
    """검증 리포트를 출력하고 전체 통과 여부(bool)를 반환한다."""
    ok = True
    print("── 데이터 검증 리포트 ──────────────────────────")

    # 1) SQL ↔ DataFrame 행 수 일치
    counts = table_counts(con)
    db_rows = counts["patient"]
    match = (db_rows == len(df))
    ok &= match
    print(f"[{'PASS' if match else 'FAIL'}] 행 수  DB={db_rows:,}  DataFrame={len(df):,}")

    # 2) 참조 무결성
    orphan = count_orphan_exams(con)
    ok &= (orphan == 0)
    print(f"[{'PASS' if orphan == 0 else 'FAIL'}] 참조 무결성  orphan 건강검사 = {orphan}")

    # 3) 결측치
    n_null = int(df.isna().sum().sum())
    ok &= (n_null == 0)
    print(f"[{'PASS' if n_null == 0 else 'FAIL'}] 결측치 = {n_null}건")

    # 4) 중복 (보고만 — 실패로 처리하지 않음)
    n_dup = int(df.duplicated().sum())
    print(f"[INFO] 중복 행 = {n_dup:,}건  (설문 특성상 유효 응답으로 유지)")

    # 5) 임상 변수 유효 범위
    bad = {}
    for col, (lo, hi) in RANGES.items():
        if col in df.columns:
            n = int((~df[col].between(lo, hi)).sum())
            if n:
                bad[col] = n
    for col in BINARY:
        if col in df.columns:
            n = int((~df[col].isin([0, 1])).sum())
            if n:
                bad[col] = n
    ok &= (not bad)
    print(f"[{'PASS' if not bad else 'FAIL'}] 범위 벗어난 값: {bad or '없음'}")

    print("───────────────────────────────────────────────")
    print("검증 결과:", "✅ 모두 통과" if ok else "❌ 문제 발견 — 확인 필요")
    return ok
