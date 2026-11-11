"""
data_retrieval.py — SQL로 분석용 데이터를 가져오는 로직만 분리
---------------------------------------------------------------------------
  * MODELING_QUERY : 모델링에 필요한 전체 변수를 1:1 조인으로 수집
  * fetch_modeling_data() : 쿼리 실행 → pandas DataFrame
  * table_counts()        : 각 테이블 행 수 (검증용)
커서는 with 블록으로 열고 자동으로 닫습니다 (자원 정리).
"""
import pandas as pd

# 환자(인구·진단·생활습관) + 건강검사 를 patient_id 로 1:1 조인
# → 분석/모델링에 필요한 22개 변수를 한 번에 확보
MODELING_QUERY = """
    SELECT p.age, p.sex, p.education, p.income,
           p.diabetes_status, p.smoker, p.phys_activity, p.fruits, p.veggies,
           p.hvy_alcohol, p.any_healthcare, p.no_doc_cost,
           h.bmi, h.high_bp, h.high_chol, h.chol_check, h.gen_hlth,
           h.ment_hlth, h.phys_hlth, h.diff_walk, h.stroke, h.heart_disease
    FROM patient p
    JOIN health_exam h ON p.patient_id = h.patient_id
"""


def fetch_modeling_data(con):
    """MODELING_QUERY 를 실행해 DataFrame 으로 반환한다."""
    with con.cursor() as cur:
        cur.execute(MODELING_QUERY)
        cols = [c[0].lower() for c in cur.description]
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)


def table_counts(con, tables=("patient", "health_exam", "analysis_result")):
    """각 테이블의 행 수를 dict 로 반환한다 (검증용)."""
    counts = {}
    with con.cursor() as cur:
        for t in tables:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            counts[t] = cur.fetchone()[0]
    return counts


def count_orphan_exams(con):
    """건강검사에 있지만 환자에 없는 레코드 수 (참조 무결성 검사). 0이어야 정상."""
    with con.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) FROM health_exam h
            WHERE NOT EXISTS (SELECT 1 FROM patient p WHERE p.patient_id = h.patient_id)
        """)
        return cur.fetchone()[0]
