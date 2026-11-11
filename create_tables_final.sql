-- =====================================================================
-- File    : create_tables_final.sql
-- Purpose : 최종 ER 다이어그램 구조로 테이블 생성 + 데이터 적재 (Oracle)
--             PATIENT          (환자 · 진단 · 생활습관 통합)   PK = patient_id
--             HEALTH_EXAM      (건강검사)                     PK = FK = patient_id  (1:1)
--             ANALYSIS_RESULT  (분석결과)                     PK = FK = patient_id  (1:1)
-- Order   : 1) 기존 테이블 정리 → 2) STG_DIABETES 생성 → 3) CSV Import
--           → 4) 본 테이블 생성 → 5) 적재 → 6) 검증
-- Note    : SQL Developer를 쓰지 않으려면 build_db.py (파이썬 버전)로 대체 가능.
-- =====================================================================


-- ---------------------------------------------------------------------
-- 1) 기존 테이블 정리 (없으면 건너뜀 → 여러 번 실행해도 안전)
-- ---------------------------------------------------------------------
BEGIN
    FOR t IN (SELECT table_name FROM user_tables
              WHERE  table_name IN ('ANALYSIS_RESULT', 'HEALTH_EXAM', 'LIFESTYLE',
                                    'DIAGNOSIS', 'PATIENT', 'STG_DIABETES')) LOOP
        EXECUTE IMMEDIATE 'DROP TABLE ' || t.table_name || ' CASCADE CONSTRAINTS PURGE';
    END LOOP;
    FOR s IN (SELECT sequence_name FROM user_sequences
              WHERE  sequence_name IN ('SEQ_RESULT', 'SEQ_EXAM', 'SEQ_LIFESTYLE', 'SEQ_DIAG')) LOOP
        EXECUTE IMMEDIATE 'DROP SEQUENCE ' || s.sequence_name;
    END LOOP;
END;
/


-- ---------------------------------------------------------------------
-- 2) STG_DIABETES (스테이징) — diabetes_clean.csv 22개 컬럼을 그대로 받는 임시 테이블
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

-- ★ 여기서 SQL Developer [데이터 임포트]로 diabetes_clean.csv → STG_DIABETES 적재
--   (sql/02_import_guide.md 참고) 후 아래를 이어서 실행

ALTER TABLE stg_diabetes ADD (pid NUMBER(10));
UPDATE stg_diabetes SET pid = ROWNUM;
COMMIT;


-- ---------------------------------------------------------------------
-- 3) PATIENT (환자 · 진단 · 생활습관 통합) — 부모 테이블, PK만 보유
-- ---------------------------------------------------------------------
CREATE TABLE patient (
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
    CONSTRAINT pk_patient          PRIMARY KEY (patient_id),
    CONSTRAINT ck_patient_age      CHECK (age BETWEEN 1 AND 13),
    CONSTRAINT ck_patient_sex      CHECK (sex IN (0, 1)),
    CONSTRAINT ck_patient_edu      CHECK (education BETWEEN 1 AND 6),
    CONSTRAINT ck_patient_income   CHECK (income BETWEEN 1 AND 11),
    CONSTRAINT ck_patient_diab     CHECK (diabetes_status IN (0, 1, 2))
);


-- ---------------------------------------------------------------------
-- 4) HEALTH_EXAM (건강검사) — 1:1, patient_id = PK이자 FK
-- ---------------------------------------------------------------------
CREATE TABLE health_exam (
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
    CONSTRAINT pk_health_exam    PRIMARY KEY (patient_id),
    CONSTRAINT fk_exam_patient   FOREIGN KEY (patient_id)
                                 REFERENCES patient (patient_id),
    CONSTRAINT ck_exam_bmi       CHECK (bmi BETWEEN 10 AND 60),
    CONSTRAINT ck_exam_genhlth   CHECK (gen_hlth BETWEEN 1 AND 5),
    CONSTRAINT ck_exam_menthlth  CHECK (ment_hlth BETWEEN 0 AND 30),
    CONSTRAINT ck_exam_physhlth  CHECK (phys_hlth BETWEEN 0 AND 30)
);


-- ---------------------------------------------------------------------
-- 5) ANALYSIS_RESULT (분석결과) — 1:1, patient_id = PK이자 FK
-- ---------------------------------------------------------------------
CREATE TABLE analysis_result (
    patient_id     NUMBER(10)    NOT NULL,
    analysis_name  VARCHAR2(100) NOT NULL,
    category       VARCHAR2(100),
    metric_value   NUMBER(12,4),
    created_at     DATE DEFAULT SYSDATE,
    CONSTRAINT pk_analysis_result  PRIMARY KEY (patient_id),
    CONSTRAINT fk_result_patient   FOREIGN KEY (patient_id)
                                   REFERENCES patient (patient_id)
);


-- ---------------------------------------------------------------------
-- 6) 데이터 적재 (부모 → 자식 순서)
-- ---------------------------------------------------------------------
INSERT INTO patient (
    patient_id, age, sex, education, income, diabetes_status,
    smoker, phys_activity, fruits, veggies, hvy_alcohol, any_healthcare, no_doc_cost)
SELECT pid, age, sex, education, income, diabetes_012,
       smoker, physactivity, fruits, veggies, hvyalcoholconsump, anyhealthcare, nodocbccost
FROM   stg_diabetes;

INSERT INTO health_exam (
    patient_id, bmi, high_bp, high_chol, chol_check,
    gen_hlth, ment_hlth, phys_hlth, diff_walk, stroke, heart_disease)
SELECT pid, bmi, highbp, highchol, cholcheck,
       genhlth, menthlth, physhlth, diffwalk, stroke, heartdiseaseorattack
FROM   stg_diabetes;

-- 분석 결과 예시: 환자별 위험요인 개수 (고혈압 + 고콜레스테롤 + 비만 + 주관적 건강 나쁨, 0~4개)
INSERT INTO analysis_result (patient_id, analysis_name, category, metric_value)
SELECT h.patient_id,
       '위험요인 개수',
       CASE WHEN cnt >= 3 THEN '고위험'
            WHEN cnt = 2  THEN '중위험'
            ELSE               '저위험' END,
       cnt
FROM (
    SELECT patient_id,
           NVL(high_bp, 0) + NVL(high_chol, 0)
         + CASE WHEN bmi >= 30     THEN 1 ELSE 0 END
         + CASE WHEN gen_hlth >= 4 THEN 1 ELSE 0 END AS cnt
    FROM   health_exam
) h;

COMMIT;


-- ---------------------------------------------------------------------
-- 7) 검증
-- ---------------------------------------------------------------------
SELECT 'patient'         AS tbl, COUNT(*) AS cnt FROM patient
UNION ALL SELECT 'health_exam',     COUNT(*) FROM health_exam
UNION ALL SELECT 'analysis_result', COUNT(*) FROM analysis_result;

SELECT COUNT(*) AS no_exam_patients
FROM   patient p
WHERE  NOT EXISTS (SELECT 1 FROM health_exam h WHERE h.patient_id = p.patient_id);

SELECT a.category                                                     AS risk_group,
       COUNT(*)                                                       AS patients,
       ROUND(AVG(CASE WHEN p.diabetes_status = 2 THEN 1 ELSE 0 END) * 100, 1) AS diabetes_rate_pct
FROM   patient p
JOIN   health_exam     h ON h.patient_id = p.patient_id
JOIN   analysis_result a ON a.patient_id = p.patient_id
GROUP  BY a.category
ORDER  BY diabetes_rate_pct;

-- Done.
