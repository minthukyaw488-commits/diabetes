# 당뇨병 데이터 웨어하우스 프로젝트 🩺

CDC **BRFSS 2021** 당뇨 건강지표 데이터를 Oracle DB로 설계·적재하고,
SQL 분석과 머신러닝으로 당뇨 위험요인을 규명하는 프로젝트입니다.

> **팀원**: 양다윗 ·민뚜쩌 ·한지은

---

## 📌 프로젝트 단계

| 단계 | 내용 | 상태 |
|------|------|------|
| **1단계** | 주제 선정 · 전처리 · 정규화 DB(DW) 설계 · Oracle 적재 | ✅ 완료 |
| **2단계** | 파이썬 DB 연동 · 데이터 추출 · 전처리 · 모델링/튜닝 · 암호화 저장 | ✅ 완료 |
| **3단계** | 저장 모델로 예측 · 결과를 ANALYSIS_RESULT에 저장 · 발표 | 🔄 예정 |

---

## 🗂️ 최종 DB 설계 (3 테이블 · 1:1)

한 명의 환자(`patient_id`)가 건강검사·분석결과와 각각 **1:1**로 연결됩니다.

| 테이블 | 설명 | 키 |
|--------|------|-----|
| **PATIENT** | 환자 · 진단 · 생활습관 **통합** | `patient_id` = PK |
| **HEALTH_EXAM** | 건강검사 (BMI, 고혈압 등) | `patient_id` = PK + FK |
| **ANALYSIS_RESULT** | 분석결과 (환자별 위험등급) | `patient_id` = PK + FK |

- 원본에 식별자가 없어 **첫 행부터 순번으로 `patient_id` 부여** (1행 = 환자 1명)
- 진단·생활습관은 환자당 값이 하나뿐이라 **PATIENT에 통합** (불필요한 조인 제거)

📊 **ER 다이어그램**: [`er_diagram.html`](er_diagram.html) · **요약 리포트**: [`summary_report.pdf`](summary_report.pdf)

---

## ▶️ 실행 방법

### 사전 준비
```bash
pip install -r requirements.txt          # 의존성 설치 (numpy<2 포함)
cp .env.example .env                      # 접속 정보 템플릿 복사
#  → .env 파일을 열어 DB_PASSWORD 를 본인 비밀번호로 수정
# Oracle Free (Docker) 컨테이너가 실행 중이어야 함  →  docker ps
```
> **비밀번호는 코드가 아니라 `.env` 에만** 둡니다 (`.env` 는 git에 올라가지 않음).
> 접속 로직은 `db_connection.py` 가 환경변수에서 읽습니다.

### 1) DB 구축 + 데이터 적재
```bash
python build_db.py          # 3개 테이블 생성 + CSV 적재 + 검증 (SQL Developer 불필요)
```
> SQL Developer를 쓰려면 [`create_tables_final.sql`](create_tables_final.sql) 사용.

### 2) 분석 · 모델링 (2단계)
```bash
python s2_pipeline.py       # DB연동 → 데이터(2테이블 JOIN) → 전처리 → RF/XGB 튜닝 → 암호화 저장
python s2_load_predict.py   # 저장한 암호화 모델 불러와 예측
```

---

## 📈 주요 결과

**최적 모델: RandomForest** (불균형 데이터라 macro-F1 기준 선정)

| 모델 | macro-F1 | 정확도 |
|------|----------|--------|
| **RandomForest** 🏆 | **0.44** | 0.76 |
| XGBoost | 0.40 | 0.84 |

- 당뇨 **재현율 73%** (실제 당뇨 10명 중 7명 탐지)
- 강한 예측 변수: **BMI · 연령 · 소득**, 파생변수 `risk_count`도 상위권

**위험등급별 당뇨 비율** (ANALYSIS_RESULT)

| 위험등급 | 환자 수 | 당뇨 비율 |
|----------|---------|-----------|
| 저위험 | 136,016 | 5.4% |
| 중위험 | 58,729 | 18.0% |
| 고위험 | 41,633 | **37.5%** |

➡️ 위험요인이 많을수록 당뇨 비율이 **약 7배** 증가.

---

## 📁 파일 안내 (현재 사용)

| 파일 | 설명 |
|------|------|
| `diabetes_clean.csv` | 전처리 완료 데이터 (236,378행 × 22변수) |
| `build_db.py` | **DB 구축 + 적재** (파이썬, csv 모듈 — pandas 불필요) |
| `create_tables_final.sql` | DB 구축 (SQL Developer용) |
| `s2_pipeline.py` | **2단계 전체 파이프라인** (DB연동~모델 저장) |
| `s2_load_predict.py` | 암호화 모델 불러와 예측 |
| `make_s2_charts.py` | 발표용 차트 생성 (모델비교·혼동행렬·변수중요도) |
| `er_diagram.html` / `summary_report.pdf` | ER 다이어그램 · 핵심 요약 |
| `diabetes_project_stage2.pptx` | 2단계 발표자료 (10장) |

> `sql/` 폴더와 `migrate_*.py`, `01b/01c` 등은 **이전 설계 버전(참고용 기록)** 입니다.
> 최종 설계는 위의 `create_tables_final.sql` / `build_db.py` 기준입니다.

---
