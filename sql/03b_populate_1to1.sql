-- =====================================================================
-- File   : 03b_populate_1to1.sql
-- Purpose: Load the 1:1 child tables from STG_DIABETES.
--          No sequences — patient_id is the primary key, so each patient
--          gets exactly one row and a repeated run is rejected.
-- Requires: STG_DIABETES already holds the data and a PID column
--          (added in 03_populate.sql). If PID is missing, run:
--              ALTER TABLE stg_diabetes ADD (pid NUMBER(10));
--              UPDATE stg_diabetes SET pid = ROWNUM;  COMMIT;
-- =====================================================================

INSERT INTO health_exam (
    patient_id, bmi, high_bp, high_chol, chol_check,
    gen_hlth, ment_hlth, phys_hlth, diff_walk, stroke, heart_disease)
SELECT pid, bmi, highbp, highchol, cholcheck,
       genhlth, menthlth, physhlth, diffwalk, stroke, heartdiseaseorattack
FROM   stg_diabetes;

INSERT INTO lifestyle (
    patient_id, smoker, phys_activity, fruits, veggies,
    hvy_alcohol, any_healthcare, no_doc_cost)
SELECT pid, smoker, physactivity, fruits, veggies,
       hvyalcoholconsump, anyhealthcare, nodocbccost
FROM   stg_diabetes;

INSERT INTO diagnosis (patient_id, diabetes_status)
SELECT pid, diabetes_012
FROM   stg_diabetes;

COMMIT;

-- Verify — all four tables must be 236378
SELECT 'patient'     AS table_name, COUNT(*) AS row_count FROM patient
UNION ALL SELECT 'health_exam', COUNT(*) FROM health_exam
UNION ALL SELECT 'lifestyle',   COUNT(*) FROM lifestyle
UNION ALL SELECT 'diagnosis',   COUNT(*) FROM diagnosis;

-- If you run the INSERTs a second time by mistake, Oracle now rejects it:
--   ORA-00001: unique constraint (PK_HEALTH_EXAM) violated
-- => the duplicate-rows bug can no longer happen.
