-- =====================================================================
-- File   : 06_analysis_extra.sql
-- Purpose: Additional SQL analyses (protective factors, socio-economic,
--          cross-tab, combination) stored in ANALYSIS_RESULT.
-- Note   : seq.NEXTVAL is wrapped OUTSIDE any GROUP BY (Oracle rule).
--          diabetes_rate = % with diabetes_status = 2.
-- Run AFTER 05_analysis.sql (adds to the same ANALYSIS_RESULT table).
-- =====================================================================

-- =====================================================================
-- Q7. Diabetes rate by INCOME level (사회·경제 요인)
-- =====================================================================
SELECT p.income,
       ROUND(100 * SUM(CASE WHEN d.diabetes_status = 2 THEN 1 ELSE 0 END)
             / COUNT(*), 2) AS diabetes_rate
FROM patient p JOIN diagnosis d ON d.patient_id = p.patient_id
GROUP BY p.income ORDER BY p.income;

INSERT INTO analysis_result (result_id, analysis_name, category, metric_value)
SELECT seq_result.NEXTVAL, analysis_name, category, metric_value
FROM (
    SELECT 'Diabetes rate by income' AS analysis_name,
           'Income ' || p.income AS category,
           ROUND(100 * SUM(CASE WHEN d.diabetes_status = 2 THEN 1 ELSE 0 END)
                 / COUNT(*), 2) AS metric_value
    FROM patient p JOIN diagnosis d ON d.patient_id = p.patient_id
    GROUP BY p.income
);
COMMIT;

-- =====================================================================
-- Q8. Diabetes rate by EDUCATION level (사회·경제 요인)
-- =====================================================================
INSERT INTO analysis_result (result_id, analysis_name, category, metric_value)
SELECT seq_result.NEXTVAL, analysis_name, category, metric_value
FROM (
    SELECT 'Diabetes rate by education' AS analysis_name,
           'Education ' || p.education AS category,
           ROUND(100 * SUM(CASE WHEN d.diabetes_status = 2 THEN 1 ELSE 0 END)
                 / COUNT(*), 2) AS metric_value
    FROM patient p JOIN diagnosis d ON d.patient_id = p.patient_id
    GROUP BY p.education
);
COMMIT;

-- =====================================================================
-- Q9. Diabetes rate by PHYSICAL ACTIVITY (보호 요인)
-- =====================================================================
SELECT CASE l.phys_activity WHEN 1 THEN 'Active' ELSE 'Inactive' END AS grp,
       ROUND(100 * SUM(CASE WHEN d.diabetes_status = 2 THEN 1 ELSE 0 END)
             / COUNT(*), 2) AS diabetes_rate
FROM lifestyle l JOIN diagnosis d ON d.patient_id = l.patient_id
GROUP BY l.phys_activity;

INSERT INTO analysis_result (result_id, analysis_name, category, metric_value)
SELECT seq_result.NEXTVAL, analysis_name, category, metric_value
FROM (
    SELECT 'Diabetes rate by physical activity' AS analysis_name,
           CASE l.phys_activity WHEN 1 THEN 'Active' ELSE 'Inactive' END AS category,
           ROUND(100 * SUM(CASE WHEN d.diabetes_status = 2 THEN 1 ELSE 0 END)
                 / COUNT(*), 2) AS metric_value
    FROM lifestyle l JOIN diagnosis d ON d.patient_id = l.patient_id
    GROUP BY l.phys_activity
);
COMMIT;

-- =====================================================================
-- Q10. Diabetes rate by FRUIT / VEGGIE intake (보호 요인)
-- =====================================================================
INSERT INTO analysis_result (result_id, analysis_name, category, metric_value)
SELECT seq_result.NEXTVAL, analysis_name, category, metric_value
FROM (
    SELECT 'Diabetes rate by veggie intake' AS analysis_name,
           CASE l.veggies WHEN 1 THEN 'Eats veggies' ELSE 'No veggies' END AS category,
           ROUND(100 * SUM(CASE WHEN d.diabetes_status = 2 THEN 1 ELSE 0 END)
                 / COUNT(*), 2) AS metric_value
    FROM lifestyle l JOIN diagnosis d ON d.patient_id = l.patient_id
    GROUP BY l.veggies
);
COMMIT;

-- =====================================================================
-- Q11. Cross-tab: AGE GROUP x SEX (교차 분석)
-- =====================================================================
SELECT age_grp, sex_label,
       ROUND(100 * SUM(CASE WHEN d.diabetes_status = 2 THEN 1 ELSE 0 END)
             / COUNT(*), 2) AS diabetes_rate
FROM (
    SELECT p.patient_id,
           CASE WHEN p.age <= 4 THEN '18-39'
                WHEN p.age <= 8 THEN '40-59' ELSE '60+' END AS age_grp,
           CASE p.sex WHEN 1 THEN 'Male' ELSE 'Female' END AS sex_label
    FROM patient p
) g JOIN diagnosis d ON d.patient_id = g.patient_id
GROUP BY age_grp, sex_label ORDER BY age_grp, sex_label;

INSERT INTO analysis_result (result_id, analysis_name, category, metric_value)
SELECT seq_result.NEXTVAL, analysis_name, category, metric_value
FROM (
    SELECT 'Diabetes rate by age group x sex' AS analysis_name,
           age_grp || ' / ' || sex_label AS category,
           ROUND(100 * SUM(CASE WHEN d.diabetes_status = 2 THEN 1 ELSE 0 END)
                 / COUNT(*), 2) AS metric_value
    FROM (
        SELECT p.patient_id,
               CASE WHEN p.age <= 4 THEN '18-39'
                    WHEN p.age <= 8 THEN '40-59' ELSE '60+' END AS age_grp,
               CASE p.sex WHEN 1 THEN 'Male' ELSE 'Female' END AS sex_label
        FROM patient p
    ) g JOIN diagnosis d ON d.patient_id = g.patient_id
    GROUP BY age_grp, sex_label
);
COMMIT;

-- =====================================================================
-- Q12. Combination: HIGH BP x OBESITY (조합 · 상호작용)
-- =====================================================================
SELECT bp_label, obese_label,
       ROUND(100 * SUM(CASE WHEN d.diabetes_status = 2 THEN 1 ELSE 0 END)
             / COUNT(*), 2) AS diabetes_rate
FROM (
    SELECT e.patient_id,
           CASE e.high_bp WHEN 1 THEN 'HighBP' ELSE 'NormalBP' END AS bp_label,
           CASE WHEN e.bmi >= 30 THEN 'Obese' ELSE 'NotObese' END AS obese_label
    FROM health_exam e
) g JOIN diagnosis d ON d.patient_id = g.patient_id
GROUP BY bp_label, obese_label ORDER BY bp_label, obese_label;

INSERT INTO analysis_result (result_id, analysis_name, category, metric_value)
SELECT seq_result.NEXTVAL, analysis_name, category, metric_value
FROM (
    SELECT 'Diabetes rate by HighBP x Obesity' AS analysis_name,
           bp_label || ' + ' || obese_label AS category,
           ROUND(100 * SUM(CASE WHEN d.diabetes_status = 2 THEN 1 ELSE 0 END)
                 / COUNT(*), 2) AS metric_value
    FROM (
        SELECT e.patient_id,
               CASE e.high_bp WHEN 1 THEN 'HighBP' ELSE 'NormalBP' END AS bp_label,
               CASE WHEN e.bmi >= 30 THEN 'Obese' ELSE 'NotObese' END AS obese_label
        FROM health_exam e
    ) g JOIN diagnosis d ON d.patient_id = g.patient_id
    GROUP BY bp_label, obese_label
);
COMMIT;

-- Review everything stored
SELECT analysis_name, category, metric_value
FROM analysis_result ORDER BY analysis_name, category;
