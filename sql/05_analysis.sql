-- =====================================================================
-- File   : 05_analysis.sql
-- Purpose: Answer the project's analysis questions with SQL and store
--          the results in ANALYSIS_RESULT.
-- Note   : "diabetes_rate" = percentage of people with diabetes
--          (diabetes_status = 2) within each group.
-- =====================================================================

-- Optional: clear old results before re-running
DELETE FROM analysis_result;
COMMIT;

-- =====================================================================
-- Q1. Diabetes rate by AGE GROUP
-- =====================================================================
SELECT age_group,
       COUNT(*) AS patient_count,
       ROUND(100 * SUM(CASE WHEN d.diabetes_status = 2 THEN 1 ELSE 0 END)
             / COUNT(*), 2) AS diabetes_rate
FROM (
    SELECT p.patient_id,
           CASE p.age
               WHEN 1 THEN '18-24' WHEN 2 THEN '25-29' WHEN 3 THEN '30-34'
               WHEN 4 THEN '35-39' WHEN 5 THEN '40-44' WHEN 6 THEN '45-49'
               WHEN 7 THEN '50-54' WHEN 8 THEN '55-59' WHEN 9 THEN '60-64'
               WHEN 10 THEN '65-69' WHEN 11 THEN '70-74' WHEN 12 THEN '75-79'
               WHEN 13 THEN '80+' END AS age_group
    FROM patient p
) g
JOIN diagnosis d ON d.patient_id = g.patient_id
GROUP BY age_group
ORDER BY age_group;

-- store Q1
INSERT INTO analysis_result (result_id, analysis_name, category, metric_value)
SELECT seq_result.NEXTVAL, 'Diabetes rate by age group', age_group, diabetes_rate
FROM (
    SELECT CASE p.age
               WHEN 1 THEN '18-24' WHEN 2 THEN '25-29' WHEN 3 THEN '30-34'
               WHEN 4 THEN '35-39' WHEN 5 THEN '40-44' WHEN 6 THEN '45-49'
               WHEN 7 THEN '50-54' WHEN 8 THEN '55-59' WHEN 9 THEN '60-64'
               WHEN 10 THEN '65-69' WHEN 11 THEN '70-74' WHEN 12 THEN '75-79'
               WHEN 13 THEN '80+' END AS age_group,
           ROUND(100 * SUM(CASE WHEN d.diabetes_status = 2 THEN 1 ELSE 0 END)
                 / COUNT(*), 2) AS diabetes_rate
    FROM patient p
    JOIN diagnosis d ON d.patient_id = p.patient_id
    GROUP BY p.age
);
COMMIT;

-- =====================================================================
-- Q2. Diabetes rate by SEX
-- =====================================================================
SELECT CASE p.sex WHEN 0 THEN 'Female' ELSE 'Male' END AS sex,
       COUNT(*) AS patient_count,
       ROUND(100 * SUM(CASE WHEN d.diabetes_status = 2 THEN 1 ELSE 0 END)
             / COUNT(*), 2) AS diabetes_rate
FROM patient p
JOIN diagnosis d ON d.patient_id = p.patient_id
GROUP BY p.sex
ORDER BY p.sex;

INSERT INTO analysis_result (result_id, analysis_name, category, metric_value)
SELECT seq_result.NEXTVAL, 'Diabetes rate by sex',
       CASE p.sex WHEN 0 THEN 'Female' ELSE 'Male' END,
       ROUND(100 * SUM(CASE WHEN d.diabetes_status = 2 THEN 1 ELSE 0 END)
             / COUNT(*), 2)
FROM patient p
JOIN diagnosis d ON d.patient_id = p.patient_id
GROUP BY p.sex;
COMMIT;

-- =====================================================================
-- Q3. Diabetes rate by BMI CATEGORY (does higher BMI mean more diabetes?)
-- =====================================================================
SELECT bmi_cat,
       COUNT(*) AS patient_count,
       ROUND(100 * SUM(CASE WHEN d.diabetes_status = 2 THEN 1 ELSE 0 END)
             / COUNT(*), 2) AS diabetes_rate
FROM (
    SELECT e.patient_id,
           CASE
               WHEN e.bmi < 18.5 THEN '1_Underweight'
               WHEN e.bmi < 25   THEN '2_Normal'
               WHEN e.bmi < 30   THEN '3_Overweight'
               ELSE                   '4_Obese'
           END AS bmi_cat
    FROM health_exam e
) b
JOIN diagnosis d ON d.patient_id = b.patient_id
GROUP BY bmi_cat
ORDER BY bmi_cat;

INSERT INTO analysis_result (result_id, analysis_name, category, metric_value)
SELECT seq_result.NEXTVAL, 'Diabetes rate by BMI category', bmi_cat, diabetes_rate
FROM (
    SELECT CASE
               WHEN e.bmi < 18.5 THEN '1_Underweight'
               WHEN e.bmi < 25   THEN '2_Normal'
               WHEN e.bmi < 30   THEN '3_Overweight'
               ELSE                   '4_Obese'
           END AS bmi_cat,
           ROUND(100 * SUM(CASE WHEN d.diabetes_status = 2 THEN 1 ELSE 0 END)
                 / COUNT(*), 2) AS diabetes_rate
    FROM health_exam e
    JOIN diagnosis d ON d.patient_id = e.patient_id
    GROUP BY CASE
               WHEN e.bmi < 18.5 THEN '1_Underweight'
               WHEN e.bmi < 25   THEN '2_Normal'
               WHEN e.bmi < 30   THEN '3_Overweight'
               ELSE                   '4_Obese'
             END
);
COMMIT;

-- =====================================================================
-- Q4. Average BMI and general health: DIABETIC vs NON-DIABETIC
-- =====================================================================
SELECT CASE WHEN d.diabetes_status = 2 THEN 'Diabetic' ELSE 'Non-diabetic' END AS grp,
       COUNT(*)             AS patient_count,
       ROUND(AVG(e.bmi), 2)      AS avg_bmi,
       ROUND(AVG(e.gen_hlth), 2) AS avg_gen_hlth,
       ROUND(AVG(e.phys_hlth), 2) AS avg_bad_phys_days
FROM health_exam e
JOIN diagnosis d ON d.patient_id = e.patient_id
GROUP BY CASE WHEN d.diabetes_status = 2 THEN 'Diabetic' ELSE 'Non-diabetic' END;

INSERT INTO analysis_result (result_id, analysis_name, category, metric_value)
SELECT seq_result.NEXTVAL, 'Average BMI (diabetic vs non-diabetic)',
       CASE WHEN d.diabetes_status = 2 THEN 'Diabetic' ELSE 'Non-diabetic' END,
       ROUND(AVG(e.bmi), 2)
FROM health_exam e
JOIN diagnosis d ON d.patient_id = e.patient_id
GROUP BY CASE WHEN d.diabetes_status = 2 THEN 'Diabetic' ELSE 'Non-diabetic' END;
COMMIT;

-- =====================================================================
-- Q5. Diabetes rate by individual RISK FACTOR (with vs without)
--     High BP, Smoking, Physical inactivity
-- =====================================================================
-- High blood pressure
SELECT 'HighBP' AS risk_factor,
       CASE e.high_bp WHEN 1 THEN 'Yes' ELSE 'No' END AS has_factor,
       ROUND(100 * SUM(CASE WHEN d.diabetes_status = 2 THEN 1 ELSE 0 END)
             / COUNT(*), 2) AS diabetes_rate
FROM health_exam e
JOIN diagnosis d ON d.patient_id = e.patient_id
GROUP BY e.high_bp
UNION ALL
-- Smoking
SELECT 'Smoker',
       CASE l.smoker WHEN 1 THEN 'Yes' ELSE 'No' END,
       ROUND(100 * SUM(CASE WHEN d.diabetes_status = 2 THEN 1 ELSE 0 END)
             / COUNT(*), 2)
FROM lifestyle l
JOIN diagnosis d ON d.patient_id = l.patient_id
GROUP BY l.smoker
UNION ALL
-- Physical inactivity (phys_activity = 0)
SELECT 'No physical activity',
       CASE l.phys_activity WHEN 0 THEN 'Yes' ELSE 'No' END,
       ROUND(100 * SUM(CASE WHEN d.diabetes_status = 2 THEN 1 ELSE 0 END)
             / COUNT(*), 2)
FROM lifestyle l
JOIN diagnosis d ON d.patient_id = l.patient_id
GROUP BY l.phys_activity
ORDER BY risk_factor, has_factor;

INSERT INTO analysis_result (result_id, analysis_name, category, metric_value)
SELECT seq_result.NEXTVAL, 'Diabetes rate by HighBP',
       CASE e.high_bp WHEN 1 THEN 'HighBP=Yes' ELSE 'HighBP=No' END,
       ROUND(100 * SUM(CASE WHEN d.diabetes_status = 2 THEN 1 ELSE 0 END)
             / COUNT(*), 2)
FROM health_exam e
JOIN diagnosis d ON d.patient_id = e.patient_id
GROUP BY e.high_bp;
COMMIT;

-- =====================================================================
-- Q6. Diabetes rate by NUMBER OF RISK FACTORS present
--     Factors counted: HighBP, HighChol, Smoker, no PhysActivity, Obese(BMI>=30)
-- =====================================================================
SELECT risk_count,
       COUNT(*) AS patient_count,
       ROUND(100 * SUM(CASE WHEN d.diabetes_status = 2 THEN 1 ELSE 0 END)
             / COUNT(*), 2) AS diabetes_rate
FROM (
    SELECT p.patient_id,
           ( e.high_bp
           + e.high_chol
           + l.smoker
           + CASE WHEN l.phys_activity = 0 THEN 1 ELSE 0 END
           + CASE WHEN e.bmi >= 30 THEN 1 ELSE 0 END ) AS risk_count
    FROM patient p
    JOIN health_exam e ON e.patient_id = p.patient_id
    JOIN lifestyle   l ON l.patient_id = p.patient_id
) r
JOIN diagnosis d ON d.patient_id = r.patient_id
GROUP BY risk_count
ORDER BY risk_count;

INSERT INTO analysis_result (result_id, analysis_name, category, metric_value)
SELECT seq_result.NEXTVAL, 'Diabetes rate by number of risk factors',
       TO_CHAR(risk_count) || ' risk factors',
       ROUND(100 * SUM(CASE WHEN d.diabetes_status = 2 THEN 1 ELSE 0 END)
             / COUNT(*), 2)
FROM (
    SELECT p.patient_id,
           ( e.high_bp + e.high_chol + l.smoker
           + CASE WHEN l.phys_activity = 0 THEN 1 ELSE 0 END
           + CASE WHEN e.bmi >= 30 THEN 1 ELSE 0 END ) AS risk_count
    FROM patient p
    JOIN health_exam e ON e.patient_id = p.patient_id
    JOIN lifestyle   l ON l.patient_id = p.patient_id
) r
JOIN diagnosis d ON d.patient_id = r.patient_id
GROUP BY risk_count;
COMMIT;

-- =====================================================================
-- Review all stored analysis results
-- =====================================================================
SELECT analysis_name, category, metric_value, created_at
FROM   analysis_result
ORDER  BY analysis_name, category;
