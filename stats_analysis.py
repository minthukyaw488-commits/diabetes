"""
Classification-oriented analysis of the diabetes dataset (binary target).
  target = 1 if diabetes (Diabetes_012 == 2) else 0
Produces:
  1) Univariate odds ratio + chi-square for each binary risk factor
  2) Multivariate logistic regression (adjusted odds ratios)
"""
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
import statsmodels.api as sm

df = pd.read_csv("diabetes_clean.csv")
df["diabetes"] = (df["Diabetes_012"] == 2).astype(int)   # binary target

binary_factors = ["HighBP", "HighChol", "Smoker", "Stroke", "HeartDiseaseorAttack",
                  "PhysActivity", "DiffWalk", "HvyAlcoholConsump", "Fruits", "Veggies"]

# ---------- 1) Univariate: odds ratio + chi-square ----------
print("="*74)
print("1) 단변량 분석 — 오즈비(Odds Ratio) + 카이제곱 (요인 있음 vs 없음)")
print("="*74)
print(f"{'요인':<22}{'OR':>7}{'95% CI':>16}{'chi2':>10}{'p-value':>12}")
rows = []
for f in binary_factors:
    ct = pd.crosstab(df[f], df["diabetes"])          # 2x2
    a = ct.loc[1, 1]; b = ct.loc[1, 0]               # factor=1: diab, no-diab
    c = ct.loc[0, 1]; d = ct.loc[0, 0]               # factor=0: diab, no-diab
    OR = (a * d) / (b * c)
    se = np.sqrt(1/a + 1/b + 1/c + 1/d)              # log-OR standard error
    lo, hi = np.exp(np.log(OR) - 1.96*se), np.exp(np.log(OR) + 1.96*se)
    chi2, p, _, _ = chi2_contingency(ct)
    ci = f"{lo:.2f}-{hi:.2f}"
    pstr = "<0.001" if p < 0.001 else f"{p:.3f}"
    print(f"{f:<22}{OR:>7.2f}{ci:>16}{chi2:>10.0f}{pstr:>12}")
    rows.append([f, round(OR,2), ci, round(chi2), pstr])
pd.DataFrame(rows, columns=["factor","OR","CI95","chi2","p"]).to_csv("stats_univariate.csv", index=False)

# ---------- 2) Multivariate logistic regression (adjusted OR) ----------
print()
print("="*74)
print("2) 다변량 로지스틱 회귀 — 보정 오즈비(adjusted OR)")
print("   (모든 요인을 동시에 고려했을 때 각 요인의 독립적 효과)")
print("="*74)
feat = binary_factors + ["BMI", "Age", "GenHlth", "Income", "Education"]
X = sm.add_constant(df[feat].astype(float))
y = df["diabetes"]
res = sm.Logit(y, X).fit(disp=0)
out = pd.DataFrame({
    "coef": res.params,
    "OR": np.exp(res.params),
    "CI_low": np.exp(res.conf_int()[0]),
    "CI_high": np.exp(res.conf_int()[1]),
    "p": res.pvalues,
}).drop("const")
out = out.sort_values("OR", ascending=False)
print(f"{'변수':<22}{'보정OR':>8}{'95% CI':>16}{'p-value':>12}")
mrows = []
for name, r in out.iterrows():
    pstr = "<0.001" if r["p"] < 0.001 else f"{r['p']:.3f}"
    ci = f"{r['CI_low']:.2f}-{r['CI_high']:.2f}"
    print(f"{name:<22}{r['OR']:>8.2f}{ci:>16}{pstr:>12}")
    mrows.append([name, round(r["OR"],3), ci, pstr])
pd.DataFrame(mrows, columns=["variable","adj_OR","CI95","p"]).to_csv("stats_logistic.csv", index=False)
print(f"\nPseudo R^2 = {res.prsquared:.4f}   N = {len(df):,}")
print("\n해석: OR > 1 → 당뇨 위험 증가,  OR < 1 → 위험 감소(보호 요인)")
