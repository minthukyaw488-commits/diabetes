"""
Step 1 - Data cleaning for the BRFSS2021 diabetes DW project.

Decisions:
  - Missing values : none in this dataset -> nothing to do
  - Duplicate rows : KEPT (survey data has no patient ID; identical answers
                     from different respondents are legitimate, not errors)
  - BMI outliers   : capped at 60 (values above 60 are implausible)
  - Types          : every column is a whole number, so cast to int for a
                     clean NUMBER schema when loading into the database
Output: diabetes_clean.csv
"""
import pandas as pd

SRC = "/root/.claude/uploads/f8af793c-17b3-5b18-8d87-5a32de0927a6/5a245d99-diabetes_012_health_indicators_BRFSS2021.csv"
OUT = "diabetes_clean.csv"

df = pd.read_csv(SRC)
print(f"[before] rows={len(df):,}  cols={df.shape[1]}")
print(f"[before] missing={int(df.isnull().sum().sum())}  "
      f"duplicates={int(df.duplicated().sum()):,}  BMI_max={df['BMI'].max():.0f}")

# 1) Cap BMI outliers at 60
n_capped = int((df["BMI"] > 60).sum())
df["BMI"] = df["BMI"].clip(upper=60)

# 2) Duplicates: kept on purpose (survey respondents) -> no drop

# 3) Cast all columns to integer (all values are whole numbers)
df = df.astype(int)

df.to_csv(OUT, index=False)

print(f"\n[clean ] BMI values capped to 60 : {n_capped}")
print(f"[after ] rows={len(df):,}  BMI_max={df['BMI'].max()}  all_int=True")
print(f"[saved ] {OUT}")
print("\nColumn dtypes after cleaning:")
print(df.dtypes.value_counts().to_string())
