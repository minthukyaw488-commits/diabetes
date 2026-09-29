-- =====================================================================
-- File   : 01b_create_tables_1to1.sql
-- Purpose: 1:1 redesign of the child tables (shared primary key).
--          Each child table uses patient_id AS ITS OWN PRIMARY KEY,
--          so one patient can have exactly ONE row per table (1:1).
--          Re-running an INSERT then fails with ORA-00001 (unique
--          violation) -> the duplicate-rows bug becomes impossible.
-- Note   : keeps PATIENT, STG_DIABETES, ANALYSIS_RESULT unchanged.
--          No sequences are needed for the child tables anymore.
-- Run    : after 01_create_tables.sql + data already loaded into patient.
-- =====================================================================

-- Drop the old 1:N child tables (safe to re-run)
DROP TABLE health_exam CASCADE CONSTRAINTS;
DROP TABLE lifestyle   CASCADE CONSTRAINTS;
DROP TABLE diagnosis   CASCADE CONSTRAINTS;

-- ---------------------------------------------------------------------
-- HEALTH_EXAM (건강검사) — 1:1, PK = patient_id
-- ---------------------------------------------------------------------
CREATE TABLE health_exam (
    patient_id     NUMBER(10) NOT NULL,   -- PK and FK at the same time (1:1)
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
    CONSTRAINT pk_health_exam   PRIMARY KEY (patient_id),
    CONSTRAINT fk_exam_patient  FOREIGN KEY (patient_id)
                                REFERENCES patient (patient_id),
    CONSTRAINT ck_exam_bmi      CHECK (bmi BETWEEN 10 AND 60),
    CONSTRAINT ck_exam_genhlth  CHECK (gen_hlth BETWEEN 1 AND 5)
);

-- ---------------------------------------------------------------------
-- LIFESTYLE (생활습관) — 1:1, PK = patient_id
-- ---------------------------------------------------------------------
CREATE TABLE lifestyle (
    patient_id      NUMBER(10) NOT NULL,
    smoker          NUMBER(1),
    phys_activity   NUMBER(1),
    fruits          NUMBER(1),
    veggies         NUMBER(1),
    hvy_alcohol     NUMBER(1),
    any_healthcare  NUMBER(1),
    no_doc_cost     NUMBER(1),
    CONSTRAINT pk_lifestyle      PRIMARY KEY (patient_id),
    CONSTRAINT fk_lifestyle_pat  FOREIGN KEY (patient_id)
                                 REFERENCES patient (patient_id)
);

-- ---------------------------------------------------------------------
-- DIAGNOSIS (진단결과) — 1:1, PK = patient_id
-- ---------------------------------------------------------------------
CREATE TABLE diagnosis (
    patient_id       NUMBER(10) NOT NULL,
    diabetes_status  NUMBER(1)  NOT NULL,
    CONSTRAINT pk_diagnosis     PRIMARY KEY (patient_id),
    CONSTRAINT fk_diag_patient  FOREIGN KEY (patient_id)
                                REFERENCES patient (patient_id),
    CONSTRAINT ck_diag_status   CHECK (diabetes_status IN (0, 1, 2))
);

-- Done. Next: 03b_populate_1to1.sql
