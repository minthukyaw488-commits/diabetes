"""
===========================================================================
 프로젝트 2단계 — 저장한 암호화 모델 불러와서 예측하기
 (교재: pickle 파일 불러와 모델로 변환 → 신규 데이터 예측)
===========================================================================
"""
import warnings; warnings.filterwarnings("ignore")
import pickle
import pandas as pd
from cryptography.fernet import Fernet

# 1) 키 + 암호화 모델 불러오기
key = open("model.key", "rb").read()
fernet = Fernet(key)
encrypted = open("best_model.enc", "rb").read()

# 2) 복호화 → 모델 객체로 변환
model = pickle.loads(fernet.decrypt(encrypted))
print("✅ 암호화 모델 복호화 완료:", type(model).__name__)

# 3) 신규 환자 1명 예측 (컬럼 순서는 학습 때와 동일해야 함)
#    age sex education income bmi high_bp high_chol chol_check gen_hlth
#    ment_hlth phys_hlth diff_walk stroke heart_disease smoker phys_activity
#    fruits veggies hvy_alcohol any_healthcare no_doc_cost risk_count
new_patient = pd.DataFrame([{
    "age": 10, "sex": 1, "education": 5, "income": 6,
    "bmi": 34, "high_bp": 1, "high_chol": 1, "chol_check": 1, "gen_hlth": 4,
    "ment_hlth": 5, "phys_hlth": 10, "diff_walk": 1, "stroke": 0, "heart_disease": 1,
    "smoker": 1, "phys_activity": 0, "fruits": 0, "veggies": 1,
    "hvy_alcohol": 0, "any_healthcare": 1, "no_doc_cost": 0,
    "risk_count": 1 + 1 + 1 + 1 + 1 + 0,   # high_bp+high_chol+smoker+비만+heart+stroke
}])

pred = int(model.predict(new_patient)[0])
label = {0: "정상", 1: "전당뇨", 2: "당뇨"}[pred]
print(f"🔮 예측 결과: {pred} ({label})")

# 확률도 확인 (지원 모델이면)
if hasattr(model, "predict_proba"):
    proba = model.predict_proba(new_patient)[0]
    print("   확률:", {["정상", "전당뇨", "당뇨"][i]: round(float(p), 3)
                      for i, p in enumerate(proba)})
