"""
===========================================================================
 create_tables_final.sql 의 파이썬 버전
 (SQL Developer의 수동 CSV Import 없이, 파이썬에서 전부 수행)
---------------------------------------------------------------------------
 최종 설계 (3 테이블, patient_id 공유 PK · 1:1)
   PATIENT          환자 · 진단 · 생활습관 통합   PK = patient_id
   HEALTH_EXAM      건강검사                      PK = FK = patient_id
   ANALYSIS_RESULT  분석결과(환자별 위험등급)     PK = FK = patient_id
 수행: 1) 기존 정리 → 2) 테이블 생성 → 3) CSV 적재(파이썬) → 4) 분석결과 → 5) 검증
===========================================================================
"""
import csv
import oracledb
from db_connection import get_connection   # 환경변수에서 접속 정보 로드

# ===== DB 접속 (.env 의 DB_PASSWORD 사용 — 코드에 비밀번호 없음) =====
con = get_connection()
cur = con.cursor()
print("connected\n")


def run(sql, ok=()):
    try:
        cur.execute(sql)
    except oracledb.DatabaseError as e:
        code = e.args[0].code
        if code in ok:
            print(f"   skip ORA-{code:05d}")
            return
        raise


# ---------------------------------------------------------------------------
# 1) 기존 테이블 / 시퀀스 정리 (없으면 건너뜀 → 여러 번 실행 안전)
# ---------------------------------------------------------------------------
print("1) 기존 테이블·시퀀스 정리")
for t in ("ANALYSIS_RESULT", "HEALTH_EXAM", "LIFESTYLE", "DIAGNOSIS", "PATIENT", "STG_DIABETES"):
    run(f"DROP TABLE {t} CASCADE CONSTRAINTS PURGE", ok=(942,))
for s in ("SEQ_RESULT", "SEQ_EXAM", "SEQ_LIFESTYLE", "SEQ_DIAG"):
    run(f"DROP SEQUENCE {s}", ok=(2289,))

# ---------------------------------------------------------------------------
# 2) 테이블 생성 (최종 ER 구조)
# ---------------------------------------------------------------------------
print("2) 테이블 생성 (patient / health_exam / analysis_result)")
run("""CREATE TABLE patient (
        patient_id       NUMBER(10) NOT NULL,
        age              NUMBER(2)  NOT NULL,
        sex              NUMBER(1)  NOT NULL,
        education        NUMBER(1),
        income           NUMBER(2),
        diabetes_status  NUMBER(1)  NOT NULL,
        smoker           NUMBER(1),
        phys_activity    NUMBER(1),
        fruits           NUMBER(1),
        veggies          NUMBER(1),
        hvy_alcohol      NUMBER(1),
        any_healthcare   NUMBER(1),
        no_doc_cost      NUMBER(1),
        CONSTRAINT pk_patient        PRIMARY KEY (patient_id),
        CONSTRAINT ck_patient_age    CHECK (age BETWEEN 1 AND 13),
        CONSTRAINT ck_patient_sex    CHECK (sex IN (0, 1)),
        CONSTRAINT ck_patient_edu    CHECK (education BETWEEN 1 AND 6),
        CONSTRAINT ck_patient_income CHECK (income BETWEEN 1 AND 11),
        CONSTRAINT ck_patient_diab   CHECK (diabetes_status IN (0, 1, 2))
     )""")
run("""CREATE TABLE health_exam (
        patient_id     NUMBER(10) NOT NULL,
        bmi            NUMBER(3),
        high_bp        NUMBER(1),
        high_chol      NUMBER(1),
        chol_check     NUMBER(1),
        gen_hlth       NUMBER(1),
        ment_hlth      NUMBER(2),
        phys_hlth      NUMBER(2),
        diff_walk      NUMBER(1),
        stroke         NUMBER(1),
        heart_disease  NUMBER(1),
        CONSTRAINT pk_health_exam   PRIMARY KEY (patient_id),
        CONSTRAINT fk_exam_patient  FOREIGN KEY (patient_id) REFERENCES patient (patient_id),
        CONSTRAINT ck_exam_bmi      CHECK (bmi BETWEEN 10 AND 60),
        CONSTRAINT ck_exam_genhlth  CHECK (gen_hlth BETWEEN 1 AND 5),
        CONSTRAINT ck_exam_menthlth CHECK (ment_hlth BETWEEN 0 AND 30),
        CONSTRAINT ck_exam_physhlth CHECK (phys_hlth BETWEEN 0 AND 30)
     )""")
run("""CREATE TABLE analysis_result (
        patient_id     NUMBER(10)    NOT NULL,
        analysis_name  VARCHAR2(100) NOT NULL,
        category       VARCHAR2(100),
        metric_value   NUMBER(12,4),
        created_at     DATE DEFAULT SYSDATE,
        CONSTRAINT pk_analysis_result PRIMARY KEY (patient_id),
        CONSTRAINT fk_result_patient  FOREIGN KEY (patient_id) REFERENCES patient (patient_id)
     )""")

# ---------------------------------------------------------------------------
# 3) CSV 적재 (파이썬 내장 csv 모듈 — pandas/numpy 불필요) · patient_id 1,2,3...
# ---------------------------------------------------------------------------
print("3) diabetes_clean.csv 적재")
with open("diabetes_clean.csv", newline="") as f:
    records = list(csv.DictReader(f))
print(f"   읽은 행: {len(records):,}")

PAT_SRC = ["Age", "Sex", "Education", "Income", "Diabetes_012", "Smoker",
           "PhysActivity", "Fruits", "Veggies", "HvyAlcoholConsump",
           "AnyHealthcare", "NoDocbcCost"]
HX_SRC = ["BMI", "HighBP", "HighChol", "CholCheck", "GenHlth", "MentHlth",
          "PhysHlth", "DiffWalk", "Stroke", "HeartDiseaseorAttack"]

patient_rows, exam_rows = [], []
for pid, r in enumerate(records, start=1):
    patient_rows.append((pid, *(int(float(r[c])) for c in PAT_SRC)))
    exam_rows.append((pid, *(int(float(r[c])) for c in HX_SRC)))

def bulk_insert(table, cols_sql, rows, chunk=50000):
    n = cols_sql.count(",") + 1
    sql = f"INSERT INTO {table} ({cols_sql}) VALUES ({','.join(':'+str(i+1) for i in range(n))})"
    for i in range(0, len(rows), chunk):
        cur.executemany(sql, rows[i:i+chunk])
    con.commit()
    print(f"   {table}: {len(rows):,} rows")

bulk_insert("patient",
    "patient_id, age, sex, education, income, diabetes_status, "
    "smoker, phys_activity, fruits, veggies, hvy_alcohol, any_healthcare, no_doc_cost",
    patient_rows)
bulk_insert("health_exam",
    "patient_id, bmi, high_bp, high_chol, chol_check, gen_hlth, "
    "ment_hlth, phys_hlth, diff_walk, stroke, heart_disease",
    exam_rows)

# ---------------------------------------------------------------------------
# 4) ANALYSIS_RESULT — 환자별 위험요인 개수 (고혈압+고콜레스테롤+비만+건강나쁨, 0~4)
# ---------------------------------------------------------------------------
print("4) analysis_result 생성 (위험요인 개수)")
run("""INSERT INTO analysis_result (patient_id, analysis_name, category, metric_value)
       SELECT h.patient_id, '위험요인 개수',
              CASE WHEN cnt >= 3 THEN '고위험'
                   WHEN cnt = 2  THEN '중위험'
                   ELSE '저위험' END,
              cnt
       FROM (
           SELECT patient_id,
                  NVL(high_bp, 0) + NVL(high_chol, 0)
                + CASE WHEN bmi >= 30     THEN 1 ELSE 0 END
                + CASE WHEN gen_hlth >= 4 THEN 1 ELSE 0 END AS cnt
           FROM   health_exam
       ) h""")
con.commit()

# ---------------------------------------------------------------------------
# 5) 검증
# ---------------------------------------------------------------------------
print("\n=== row counts (3 테이블 모두 236,378) ===")
for t in ("patient", "health_exam", "analysis_result"):
    print(f"   {t:16s}: {cur.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]:,}")

print("\n=== 1:1 확인 (짝 없는 환자 = 0) ===")
n = cur.execute("""SELECT COUNT(*) FROM patient p
                   WHERE NOT EXISTS (SELECT 1 FROM health_exam h WHERE h.patient_id = p.patient_id)
                """).fetchone()[0]
print(f"   건강검사 없는 환자: {n}")

print("\n=== 위험등급별 당뇨 비율 (3-테이블 조인) ===")
cur.execute("""SELECT a.category, COUNT(*) AS patients,
                      ROUND(AVG(CASE WHEN p.diabetes_status=2 THEN 1 ELSE 0 END)*100, 1) AS diabetes_rate
               FROM patient p
               JOIN health_exam     h ON h.patient_id = p.patient_id
               JOIN analysis_result a ON a.patient_id = p.patient_id
               GROUP BY a.category ORDER BY diabetes_rate""")
for r in cur.fetchall():
    print(f"   {r[0]:6s}  {r[1]:>8,}명   당뇨 {r[2]}%")

con.close()
print("\n완료 — 최종 3-테이블 설계로 DB 구축 + 데이터 적재 완료")
