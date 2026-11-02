"""
Migrate the DB from 1:1 shared-key (patient_id = PK) to the feedback design:
each child table gets its own surrogate PK (exam_id / lifestyle_id / diag_id)
and patient_id becomes an FK with a UNIQUE constraint (still 1:1, duplicates
blocked with ORA-00001).

SAFE: the current rows are copied into a temp table first, so no data is lost
and stg_diabetes is NOT required. Run on the machine hosting the Oracle Free
container.
"""
import oracledb

# ===== fill in your DB info =====
con = oracledb.connect(
    user="system",
    password="Oracle123",            # <- 너의 비밀번호
    dsn="localhost:1521/FREEPDB1",
)
cur = con.cursor()
print("✅ connected\n")


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


# table -> (seq, pk col, new-table DDL, column list copied from the old table)
specs = {
    "health_exam": dict(
        seq="seq_exam", pk="exam_id",
        ddl="""
        CREATE TABLE health_exam (
            exam_id        NUMBER(10) NOT NULL,
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
            CONSTRAINT pk_health_exam  PRIMARY KEY (exam_id),
            CONSTRAINT fk_exam_patient FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
            CONSTRAINT uq_exam_patient UNIQUE (patient_id),
            CONSTRAINT ck_exam_bmi     CHECK (bmi BETWEEN 10 AND 60),
            CONSTRAINT ck_exam_genhlth CHECK (gen_hlth BETWEEN 1 AND 5)
        )""",
        cols="patient_id, bmi, high_bp, high_chol, chol_check, gen_hlth, "
             "ment_hlth, phys_hlth, diff_walk, stroke, heart_disease",
    ),
    "lifestyle": dict(
        seq="seq_lifestyle", pk="lifestyle_id",
        ddl="""
        CREATE TABLE lifestyle (
            lifestyle_id    NUMBER(10) NOT NULL,
            patient_id      NUMBER(10) NOT NULL,
            smoker          NUMBER(1),
            phys_activity   NUMBER(1),
            fruits          NUMBER(1),
            veggies         NUMBER(1),
            hvy_alcohol     NUMBER(1),
            any_healthcare  NUMBER(1),
            no_doc_cost     NUMBER(1),
            CONSTRAINT pk_lifestyle     PRIMARY KEY (lifestyle_id),
            CONSTRAINT fk_lifestyle_pat FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
            CONSTRAINT uq_lifestyle_pat UNIQUE (patient_id)
        )""",
        cols="patient_id, smoker, phys_activity, fruits, veggies, "
             "hvy_alcohol, any_healthcare, no_doc_cost",
    ),
    "diagnosis": dict(
        seq="seq_diag", pk="diag_id",
        ddl="""
        CREATE TABLE diagnosis (
            diag_id          NUMBER(10) NOT NULL,
            patient_id       NUMBER(10) NOT NULL,
            diabetes_status  NUMBER(1)  NOT NULL,
            CONSTRAINT pk_diagnosis    PRIMARY KEY (diag_id),
            CONSTRAINT fk_diag_patient FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
            CONSTRAINT uq_diag_patient UNIQUE (patient_id),
            CONSTRAINT ck_diag_status  CHECK (diabetes_status IN (0, 1, 2))
        )""",
        cols="patient_id, diabetes_status",
    ),
}

for tbl, s in specs.items():
    tmp = f"tmp_{tbl}"
    print(f"→ {tbl}")
    run(f"DROP TABLE {tmp} CASCADE CONSTRAINTS", ok=(942,))      # clean leftover
    run(f"CREATE TABLE {tmp} AS SELECT * FROM {tbl}")            # 1) snapshot data
    run(f"DROP TABLE {tbl} CASCADE CONSTRAINTS", ok=(942,))      # 2) drop old
    run(f"DROP SEQUENCE {s['seq']}", ok=(2289,))                 # 3) reset sequence
    run(f"CREATE SEQUENCE {s['seq']} START WITH 1 INCREMENT BY 1 NOCACHE")
    run(s["ddl"])                                                # 4) new structure
    run(f"INSERT INTO {tbl} ({s['pk']}, {s['cols']}) "          # 5) reload + new PK
        f"SELECT {s['seq']}.NEXTVAL, {s['cols']} FROM {tmp}")
    run(f"DROP TABLE {tmp} CASCADE CONSTRAINTS")                 # 6) drop temp
    con.commit()
    print(f"   ✅ {tbl} done\n")

# ---- verify ----
print("=== row counts (all must be 236,378) ===")
for t in ["patient", "health_exam", "lifestyle", "diagnosis"]:
    n = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"{t:12s}: {n:,}")

print("\n=== new PK / FK / UNIQUE ===")
cur.execute("""
    SELECT table_name, constraint_type, constraint_name
    FROM   user_constraints
    WHERE  table_name IN ('HEALTH_EXAM','LIFESTYLE','DIAGNOSIS')
      AND  constraint_type IN ('P','R','U')
    ORDER  BY table_name, constraint_type""")
for r in cur.fetchall():
    print(f"  {r[0]:12s} {r[1]}  {r[2]}")

con.close()
print("\n🎉 migration to 01c (surrogate PK + UNIQUE) complete")
