-- =====================================================================
-- File   : 04_verify.sql
-- Purpose: Confirm the data loaded correctly with SELECT statements.
-- =====================================================================

-- 1) Row counts should all be 236378
SELECT 'patient'     AS table_name, COUNT(*) AS rows FROM patient
UNION ALL SELECT 'health_exam', COUNT(*) FROM health_exam
UNION ALL SELECT 'lifestyle',   COUNT(*) FROM lifestyle
UNION ALL SELECT 'diagnosis',   COUNT(*) FROM diagnosis;

-- 2) Sample of a fully joined patient record
SELECT p.patient_id, p.age, p.sex, p.income,
       e.bmi, e.high_bp, e.gen_hlth,
       l.smoker, l.phys_activity,
       d.diabetes_status
FROM   patient p
JOIN   health_exam e ON e.patient_id = p.patient_id
JOIN   lifestyle   l ON l.patient_id = p.patient_id
JOIN   diagnosis   d ON d.patient_id = p.patient_id
FETCH FIRST 10 ROWS ONLY;

-- 3) Target distribution (0 none / 1 prediabetes / 2 diabetes)
SELECT diabetes_status, COUNT(*) AS cnt,
       ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM   diagnosis
GROUP  BY diabetes_status
ORDER  BY diabetes_status;

-- 4) Referential integrity check: every child row has a valid patient
SELECT COUNT(*) AS orphan_exams
FROM   health_exam e
WHERE  NOT EXISTS (SELECT 1 FROM patient p WHERE p.patient_id = e.patient_id);
-- expect 0
