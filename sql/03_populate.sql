-- =====================================================================
-- File   : 03_populate.sql
-- Purpose: Move data from the staging table into the normalized tables
--          using INSERT INTO ... SELECT.
-- Run AFTER importing diabetes_clean.csv into STG_DIABETES.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1) Give every staging row a stable patient id (PID)
--    ALTER TABLE adds the column; ROWNUM assigns 1..N.
-- ---------------------------------------------------------------------
ALTER TABLE stg_diabetes ADD (pid NUMBER(10));

UPDATE stg_diabetes SET pid = ROWNUM;
COMMIT;

-- ---------------------------------------------------------------------
-- 2) PATIENT  (demographics)
-- ---------------------------------------------------------------------
INSERT INTO patient (patient_id, age, sex, education, income)
SELECT pid, age, sex, education, income
FROM   stg_diabetes;

-- ---------------------------------------------------------------------
-- 3) HEALTH_EXAM  (clinical measurements)  -- exam_id from sequence
-- ---------------------------------------------------------------------
INSERT INTO health_exam (
    exam_id, patient_id, bmi, high_bp, high_chol, chol_check,
    gen_hlth, ment_hlth, phys_hlth, diff_walk, stroke, heart_disease)
SELECT seq_exam.NEXTVAL, pid, bmi, highbp, highchol, cholcheck,
       genhlth, menthlth, physhlth, diffwalk, stroke, heartdiseaseorattack
FROM   stg_diabetes;

-- ---------------------------------------------------------------------
-- 4) LIFESTYLE  (behaviour / access to care)  -- lifestyle_id from sequence
-- ---------------------------------------------------------------------
INSERT INTO lifestyle (
    lifestyle_id, patient_id, smoker, phys_activity, fruits, veggies,
    hvy_alcohol, any_healthcare, no_doc_cost)
SELECT seq_lifestyle.NEXTVAL, pid, smoker, physactivity, fruits, veggies,
       hvyalcoholconsump, anyhealthcare, nodocbccost
FROM   stg_diabetes;

-- ---------------------------------------------------------------------
-- 5) DIAGNOSIS  (target)  -- diag_id from sequence
-- ---------------------------------------------------------------------
INSERT INTO diagnosis (diag_id, patient_id, diabetes_status)
SELECT seq_diag.NEXTVAL, pid, diabetes_012
FROM   stg_diabetes;

COMMIT;

-- Done. Next: run 04_verify.sql
