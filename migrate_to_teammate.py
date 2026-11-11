"""
Migrate DB to the teammate's design (PDF/ER report):
  - 3 tables: PATIENT (환자+진단+생활습관 통합), HEALTH_EXAM, ANALYSIS_RESULT
  - 1:1 shared key: patient_id = PK in PATIENT, PK+FK in HEALTH_EXAM
  - lifestyle + diagnosis are MERGED into PATIENT, then dropped

From the current 01c design (4 tables: surrogate PK + UNIQUE).
SAFE: lifestyle/diagnosis values are copied into PATIENT before those tables
are dropped, so no data is lost. Run on the machine hosting Oracle Free.
"""
import oracledb

# ===== fill in your DB info =====
con = oracledb.connect(
    user="system",
    password="Oracle123",              # <- 너의 비밀번호
    dsn="localhost:1521/FREEPDB1",
)
cur = con.cursor()
print("connected\n")


def run(sql, ok=()):
    """Execute one statement; ignore the ORA codes listed in `ok`."""
    try:
        cur.execute(sql)
    except oracledb.DatabaseError as e:
        code = e.args[0].code
        if code in ok:
            print(f"   skip ORA-{code:05d}")
            return
        raise


# ---------------------------------------------------------------------------
# STEP 1 — add 생활습관 + 진단 columns to PATIENT
# ---------------------------------------------------------------------------
print("STEP 1 — PATIENT에 생활습관·진단 컬럼 추가")
run("""ALTER TABLE patient ADD (
        diabetes_status NUMBER(1),
        smoker          NUMBER(1),
        phys_activity   NUMBER(1),
        fruits          NUMBER(1),
        veggies         NUMBER(1),
        hvy_alcohol     NUMBER(1),
        any_healthcare  NUMBER(1),
        no_doc_cost     NUMBER(1)
     )""", ok=(1430,))                       # 1430 = column already exists

# ---------------------------------------------------------------------------
# STEP 2 — copy values from DIAGNOSIS + LIFESTYLE into PATIENT (1:1 join)
# ---------------------------------------------------------------------------
print("STEP 2 — diagnosis·lifestyle 값을 PATIENT로 이전")
run("""MERGE INTO patient p USING (
        SELECT p0.patient_id,
               d.diabetes_status,
               l.smoker, l.phys_activity, l.fruits, l.veggies,
               l.hvy_alcohol, l.any_healthcare, l.no_doc_cost
        FROM   patient p0
        JOIN   diagnosis d ON p0.patient_id = d.patient_id
        JOIN   lifestyle l ON p0.patient_id = l.patient_id
     ) s ON (p.patient_id = s.patient_id)
     WHEN MATCHED THEN UPDATE SET
        p.diabetes_status = s.diabetes_status,
        p.smoker          = s.smoker,
        p.phys_activity   = s.phys_activity,
        p.fruits          = s.fruits,
        p.veggies         = s.veggies,
        p.hvy_alcohol     = s.hvy_alcohol,
        p.any_healthcare  = s.any_healthcare,
        p.no_doc_cost     = s.no_doc_cost""")
con.commit()

# constraints on the new diagnosis column
run("ALTER TABLE patient MODIFY (diabetes_status NUMBER(1) NOT NULL)", ok=(1442,))
run("ALTER TABLE patient ADD CONSTRAINT ck_patient_diab CHECK (diabetes_status IN (0,1,2))",
    ok=(2264, 2260))                         # 2264/2260 = constraint name already used

# ---------------------------------------------------------------------------
# STEP 3 — rebuild HEALTH_EXAM with patient_id as PK (drop surrogate exam_id)
# ---------------------------------------------------------------------------
print("STEP 3 — HEALTH_EXAM을 patient_id PK로 재구성 (exam_id 제거)")
run("DROP TABLE tmp_hx CASCADE CONSTRAINTS", ok=(942,))
run("""CREATE TABLE tmp_hx AS SELECT
        patient_id, bmi, high_bp, high_chol, chol_check, gen_hlth,
        ment_hlth, phys_hlth, diff_walk, stroke, heart_disease
       FROM health_exam""")
run("DROP TABLE health_exam CASCADE CONSTRAINTS", ok=(942,))
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
        CONSTRAINT pk_health_exam  PRIMARY KEY (patient_id),
        CONSTRAINT fk_exam_patient FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
        CONSTRAINT ck_exam_bmi     CHECK (bmi BETWEEN 10 AND 60),
        CONSTRAINT ck_exam_genhlth CHECK (gen_hlth BETWEEN 1 AND 5)
     )""")
run("""INSERT INTO health_exam (patient_id, bmi, high_bp, high_chol, chol_check,
        gen_hlth, ment_hlth, phys_hlth, diff_walk, stroke, heart_disease)
       SELECT patient_id, bmi, high_bp, high_chol, chol_check, gen_hlth,
        ment_hlth, phys_hlth, diff_walk, stroke, heart_disease FROM tmp_hx""")
run("DROP TABLE tmp_hx CASCADE CONSTRAINTS")
con.commit()

# ---------------------------------------------------------------------------
# STEP 4 — drop LIFESTYLE, DIAGNOSIS and the surrogate sequences
# ---------------------------------------------------------------------------
print("STEP 4 — lifestyle·diagnosis 테이블과 시퀀스 제거")
run("DROP TABLE lifestyle CASCADE CONSTRAINTS", ok=(942,))
run("DROP TABLE diagnosis CASCADE CONSTRAINTS", ok=(942,))
for seq in ("seq_exam", "seq_lifestyle", "seq_diag"):
    run(f"DROP SEQUENCE {seq}", ok=(2289,))
con.commit()

# ---------------------------------------------------------------------------
# VERIFY
# ---------------------------------------------------------------------------
print("\n=== 테이블 목록 (patient / health_exam / analysis_result 만 남아야 함) ===")
cur.execute("""SELECT table_name FROM user_tables
               WHERE table_name IN ('PATIENT','HEALTH_EXAM','LIFESTYLE','DIAGNOSIS','ANALYSIS_RESULT')
               ORDER BY table_name""")
for r in cur.fetchall():
    print("  ", r[0])

print("\n=== row counts (patient / health_exam 모두 236,378) ===")
for t in ("patient", "health_exam"):
    print(f"  {t:12s}: {cur.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]:,}")

print("\n=== PATIENT 컬럼 (진단·생활습관 통합 확인) ===")
cur.execute("""SELECT column_name FROM user_tab_columns
               WHERE table_name='PATIENT' ORDER BY column_id""")
print("  ", ", ".join(r[0].lower() for r in cur.fetchall()))

print("\n=== HEALTH_EXAM PK/FK (patient_id 공유키) ===")
cur.execute("""SELECT constraint_type, constraint_name FROM user_constraints
               WHERE table_name='HEALTH_EXAM' AND constraint_type IN ('P','R')
               ORDER BY constraint_type""")
for r in cur.fetchall():
    print(f"   {r[0]}  {r[1]}")

con.close()
print("\n완료 — teammate 설계(3 테이블, patient_id 공유 PK)로 이전되었습니다.")
