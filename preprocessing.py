"""
preprocessing.py — 전처리 로직만 분리 (데이터 누수 방지에 유의)
---------------------------------------------------------------------------
  * add_derived_features() : 파생변수 risk_count 생성
        - 각 '행 자신의 값'만으로 계산하는 row-wise 변환이므로
          분할 전에 계산해도 train/test 정보가 섞이지 않습니다 (누수 없음).
  * split_data() : 계층(stratified) 분할로 3-class 비율 유지
※ 정규화/인코딩은 생략합니다:
   - 모든 변수가 이미 숫자 코드(이진 0/1, 순서형 코드)라 인코딩 불필요
   - 트리 모델(RandomForest)은 스케일에 영향받지 않아 정규화 불필요
   (만약 LogisticRegression 등 스케일 민감 모델을 쓸 경우에는
    StandardScaler 를 'train 에만 fit' 하여 누수를 피해야 합니다.)
"""
from sklearn.model_selection import train_test_split

TARGET = "diabetes_status"


def add_derived_features(df):
    """복합 위험도 파생변수 risk_count (0~6) 추가. 원본은 보존(copy)."""
    df = df.copy()
    df["risk_count"] = (
        df["high_bp"] + df["high_chol"] + df["smoker"]
        + (df["bmi"] >= 30).astype(int)      # 비만
        + df["heart_disease"] + df["stroke"]
    )
    return df


def split_data(df, target=TARGET, test_size=0.2, seed=42):
    """stratified train/test 분할. (X_train, X_test, y_train, y_test) 반환."""
    X = df.drop(columns=[target])
    y = df[target].astype(int)
    return train_test_split(
        X, y, test_size=test_size, random_state=seed, stratify=y
    )
