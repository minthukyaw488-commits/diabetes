-- =====================================================================
-- File   : 01c_create_tables_ppt.sql
-- Purpose: Rebuild the child tables to MATCH THE PRESENTATION design:
--          each child has its own surrogate PK (exam_id / lifestyle_id /
--          diag_id) from a sequence, and patient_id is FK + UNIQUE.
--          UNIQUE(patient_id) enforces the 1:1 relationship and blocks
--          duplicate inserts (bug-proof).
-- Keeps  : PATIENT, STG_DIABETES, ANALYSIS_RESULT unchanged.
-- =====================================================================

DROP TABLE health_exam CASCADE CONSTRAINTS;
DROP TABLE lifestyle   CASCADE CONSTRAINTS;
DROP TABLE diagnosis   CASCADE CONSTRAINTS;
DROP SEQUENCE seq_exam;
DROP SEQUENCE seq_lifestyle;
DROP SEQUENCE seq_diag;

CREATE SEQUENCE seq_exam      START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE seq_lifestyle START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE seq_diag      START WITH 1 INCREMENT BY 1 NOCACHE;

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
    CONSTRAINT uq_exam_patient UNIQUE (patient_id),        -- enforces 1:1
    CONSTRAINT ck_exam_bmi     CHECK (bmi BETWEEN 10 AND 60),
    CONSTRAINT ck_exam_genhlth CHECK (gen_hlth BETWEEN 1 AND 5)
);

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
    CONSTRAINT uq_lifestyle_pat UNIQUE (patient_id)        -- enforces 1:1
);

CREATE TABLE diagnosis (
    diag_id          NUMBER(10) NOT NULL,
    patient_id       NUMBER(10) NOT NULL,
    diabetes_status  NUMBER(1)  NOT NULL,
    CONSTRAINT pk_diagnosis    PRIMARY KEY (diag_id),
    CONSTRAINT fk_diag_patient FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    CONSTRAINT uq_diag_patient UNIQUE (patient_id),        -- enforces 1:1
    CONSTRAINT ck_diag_status  CHECK (diabetes_status IN (0, 1, 2))
);

-- Next: 03c_populate_ppt.sql
