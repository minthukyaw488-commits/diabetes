-- =====================================================================
-- Project Stage 1 : DB(DW) Design - Diabetes Risk Factor Analysis
-- File   : 01_create_tables.sql
-- Purpose: Create the staging table, the normalized (3NF) tables,
--          the analysis-result table, and the sequences.
-- Run in : Oracle SQL Developer  (run this file first)
-- Dataset: BRFSS2021 Diabetes Health Indicators (diabetes_clean.csv)
-- =====================================================================

-- ---------------------------------------------------------------------
-- 0) Clean up if the objects already exist (safe to re-run)
--    Ignore "table/sequence does not exist" errors on the first run.
-- ---------------------------------------------------------------------
DROP TABLE analysis_result CASCADE CONSTRAINTS;
DROP TABLE diagnosis       CASCADE CONSTRAINTS;
DROP TABLE lifestyle       CASCADE CONSTRAINTS;
DROP TABLE health_exam     CASCADE CONSTRAINTS;
DROP TABLE patient         CASCADE CONSTRAINTS;
DROP TABLE stg_diabetes    CASCADE CONSTRAINTS;

DROP SEQUENCE seq_exam;
DROP SEQUENCE seq_lifestyle;
DROP SEQUENCE seq_diag;
DROP SEQUENCE seq_result;

-- ---------------------------------------------------------------------
-- 1) STAGING TABLE  (raw copy of the cleaned CSV, 22 columns)
--    The cleaned CSV is imported into this table with the SQL Developer
--    Import Data wizard (see 02_import_guide.md).
-- ---------------------------------------------------------------------
CREATE TABLE stg_diabetes (
    diabetes_012          NUMBER(1),
    highbp                NUMBER(1),
    highchol              NUMBER(1),
    cholcheck             NUMBER(1),
    bmi                   NUMBER(3),
    smoker                NUMBER(1),
    stroke                NUMBER(1),
    heartdiseaseorattack  NUMBER(1),
    physactivity          NUMBER(1),
    fruits                NUMBER(1),
    veggies               NUMBER(1),
    hvyalcoholconsump     NUMBER(1),
    anyhealthcare         NUMBER(1),
    nodocbccost           NUMBER(1),
    genhlth               NUMBER(1),
    menthlth              NUMBER(2),
    physhlth              NUMBER(2),
    diffwalk              NUMBER(1),
    sex                   NUMBER(1),
    age                   NUMBER(2),
    education             NUMBER(1),
    income                NUMBER(2)
);

-- ---------------------------------------------------------------------
-- 2) PATIENT  (환자) - demographics, one row per respondent
-- ---------------------------------------------------------------------
CREATE TABLE patient (
    patient_id  NUMBER(10)  NOT NULL,
    age         NUMBER(2)   NOT NULL,   -- age bracket 1..13
    sex         NUMBER(1)   NOT NULL,   -- 0 = female, 1 = male
    education   NUMBER(1),              -- 1..6
    income      NUMBER(2),              -- 1..11
    CONSTRAINT pk_patient      PRIMARY KEY (patient_id),
    CONSTRAINT ck_patient_age  CHECK (age BETWEEN 1 AND 13),
    CONSTRAINT ck_patient_sex  CHECK (sex IN (0, 1))
);

-- ---------------------------------------------------------------------
-- 3) HEALTH_EXAM  (건강검사) - clinical measurements
-- ---------------------------------------------------------------------
CREATE TABLE health_exam (
    exam_id        NUMBER(10) NOT NULL,
    patient_id     NUMBER(10) NOT NULL,
    bmi            NUMBER(3),           -- 12..60 (capped)
    high_bp        NUMBER(1),           -- 0/1 high blood pressure
    high_chol      NUMBER(1),           -- 0/1 high cholesterol
    chol_check     NUMBER(1),           -- 0/1 cholesterol checked in 5y
    gen_hlth       NUMBER(1),           -- 1(excellent)..5(poor)
    ment_hlth      NUMBER(2),           -- bad mental-health days 0..30
    phys_hlth      NUMBER(2),           -- bad physical-health days 0..30
    diff_walk      NUMBER(1),           -- 0/1 difficulty walking
    stroke         NUMBER(1),           -- 0/1 ever had a stroke
    heart_disease  NUMBER(1),           -- 0/1 heart disease or attack
    CONSTRAINT pk_health_exam    PRIMARY KEY (exam_id),
    CONSTRAINT fk_exam_patient   FOREIGN KEY (patient_id)
                                 REFERENCES patient (patient_id),
    CONSTRAINT ck_exam_bmi       CHECK (bmi BETWEEN 10 AND 60),
    CONSTRAINT ck_exam_genhlth   CHECK (gen_hlth BETWEEN 1 AND 5)
);

-- ---------------------------------------------------------------------
-- 4) LIFESTYLE  (생활습관) - behaviour / access to care
-- ---------------------------------------------------------------------
CREATE TABLE lifestyle (
    lifestyle_id    NUMBER(10) NOT NULL,
    patient_id      NUMBER(10) NOT NULL,
    smoker          NUMBER(1),          -- 0/1
    phys_activity   NUMBER(1),          -- 0/1 physical activity in 30d
    fruits          NUMBER(1),          -- 0/1 eats fruit daily
    veggies         NUMBER(1),          -- 0/1 eats veggies daily
    hvy_alcohol     NUMBER(1),          -- 0/1 heavy alcohol use
    any_healthcare  NUMBER(1),          -- 0/1 has any healthcare coverage
    no_doc_cost     NUMBER(1),          -- 0/1 skipped doctor due to cost
    CONSTRAINT pk_lifestyle       PRIMARY KEY (lifestyle_id),
    CONSTRAINT fk_lifestyle_pat   FOREIGN KEY (patient_id)
                                  REFERENCES patient (patient_id)
);

-- ---------------------------------------------------------------------
-- 5) DIAGNOSIS  (진단결과) - the target variable
-- ---------------------------------------------------------------------
CREATE TABLE diagnosis (
    diag_id          NUMBER(10) NOT NULL,
    patient_id       NUMBER(10) NOT NULL,
    diabetes_status  NUMBER(1)  NOT NULL,  -- 0 none, 1 prediabetes, 2 diabetes
    CONSTRAINT pk_diagnosis     PRIMARY KEY (diag_id),
    CONSTRAINT fk_diag_patient  FOREIGN KEY (patient_id)
                                REFERENCES patient (patient_id),
    CONSTRAINT ck_diag_status   CHECK (diabetes_status IN (0, 1, 2))
);

-- ---------------------------------------------------------------------
-- 6) ANALYSIS_RESULT  (분석결과) - stores the SQL analysis outputs
--    Required by the rubric: a table to save analysis results.
-- ---------------------------------------------------------------------
CREATE TABLE analysis_result (
    result_id      NUMBER(10)    NOT NULL,
    analysis_name  VARCHAR2(100) NOT NULL,  -- e.g. 'Diabetes rate by age group'
    category       VARCHAR2(100),           -- e.g. '60-64', 'Male', 'Obese'
    metric_value   NUMBER(12, 4),           -- the computed number
    created_at     DATE DEFAULT SYSDATE,
    CONSTRAINT pk_analysis_result PRIMARY KEY (result_id)
);

-- ---------------------------------------------------------------------
-- 7) SEQUENCES for surrogate primary keys
-- ---------------------------------------------------------------------
CREATE SEQUENCE seq_exam      START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE seq_lifestyle START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE seq_diag      START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE seq_result    START WITH 1 INCREMENT BY 1 NOCACHE;

-- Done. Next: import diabetes_clean.csv into STG_DIABETES (02_import_guide.md)
