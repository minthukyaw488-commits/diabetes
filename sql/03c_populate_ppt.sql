-- =====================================================================
-- File   : 03c_populate_ppt.sql
-- Purpose: Load the child tables that match the presentation design
--          (surrogate PK from sequence + patient_id FK UNIQUE).
-- Requires: STG_DIABETES has a PID column. If not, run first:
--   ALTER TABLE stg_diabetes ADD (pid NUMBER(10));
--   UPDATE stg_diabetes SET pid = ROWNUM;  COMMIT;
-- =====================================================================

INSERT INTO health_exam (
    exam_id, patient_id, bmi, high_bp, high_chol, chol_check,
    gen_hlth, ment_hlth, phys_hlth, diff_walk, stroke, heart_disease)
SELECT seq_exam.NEXTVAL, pid, bmi, highbp, highchol, cholcheck,
       genhlth, menthlth, physhlth, diffwalk, stroke, heartdiseaseorattack
FROM   stg_diabetes;

INSERT INTO lifestyle (
    lifestyle_id, patient_id, smoker, phys_activity, fruits, veggies,
    hvy_alcohol, any_healthcare, no_doc_cost)
SELECT seq_lifestyle.NEXTVAL, pid, smoker, physactivity, fruits, veggies,
       hvyalcoholconsump, anyhealthcare, nodocbccost
FROM   stg_diabetes;

INSERT INTO diagnosis (diag_id, patient_id, diabetes_status)
SELECT seq_diag.NEXTVAL, pid, diabetes_012
FROM   stg_diabetes;

COMMIT;

-- Verify — all four tables must be 236378
SELECT 'patient'     AS table_name, COUNT(*) AS row_count FROM patient
UNION ALL SELECT 'health_exam', COUNT(*) FROM health_exam
UNION ALL SELECT 'lifestyle',   COUNT(*) FROM lifestyle
UNION ALL SELECT 'diagnosis',   COUNT(*) FROM diagnosis;

-- Re-running an INSERT is now blocked by UNIQUE(patient_id):
--   ORA-00001: unique constraint (UQ_EXAM_PATIENT) violated
-- => 1:1 is enforced and the duplicate-rows bug cannot happen.
