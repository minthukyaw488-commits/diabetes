"""New analysis charts: income, education, physical activity, HighBP x obesity."""
import pandas as pd, sqlite3
import matplotlib.pyplot as plt
import koreanize_matplotlib  # Korean font (NanumGothic)

df = pd.read_csv("diabetes_clean.csv")
con = sqlite3.connect(":memory:"); df.to_sql("stg", con, index=False)
R = "ROUND(100.0*SUM(CASE WHEN Diabetes_012=2 THEN 1 ELSE 0 END)/COUNT(*),2)"
def q(s): return pd.read_sql(s, con)

TEAL="#0E8080"; TEALLT="#9FC9C8"; CORAL="#E06D4F"; AMBER="#E9A66B"; INK="#1E2A2A"; MUT="#6E8383"; DEEP="#0C3B3B"

fig, ax = plt.subplots(2, 2, figsize=(13, 8.4), dpi=150)

def bars(a, labels, vals, colors, title, xlabel=None):
    b = a.bar(range(len(vals)), vals, color=colors, width=0.7)
    a.set_xticks(range(len(labels))); a.set_xticklabels(labels, fontsize=10, color=INK)
    a.set_title(title, fontsize=13, fontweight="bold", color=INK, pad=8)
    a.set_ylim(0, max(vals)*1.18)
    for s in ["top","right","left"]: a.spines[s].set_visible(False)
    a.tick_params(length=0); a.set_yticks([])
    for r, v in zip(b, vals):
        a.text(r.get_x()+r.get_width()/2, v+max(vals)*0.02, f"{v:.1f}%",
               ha="center", fontsize=10.5, fontweight="bold", color=INK)
    if xlabel: a.set_xlabel(xlabel, fontsize=10, color=MUT)

# Income
inc = q(f"SELECT Income, {R} r FROM stg GROUP BY Income ORDER BY Income")
_cmap = plt.get_cmap("YlOrRd")
grad = [_cmap(0.85-0.6*i/len(inc)) for i in range(len(inc))]
bars(ax[0,0], inc.Income.astype(int).tolist(), inc.r.tolist(), grad,
     "① 소득 수준별 당뇨병 비율 (낮을수록 ↑)", "Income level (1=low → 11=high)")

# Education
edu = q(f"SELECT Education, {R} r FROM stg GROUP BY Education ORDER BY Education")
bars(ax[0,1], ["초등","중등","고교중퇴","고졸","대학중퇴","대졸"], edu.r.tolist(),
     [CORAL,CORAL,AMBER,AMBER,TEALLT,TEAL],
     "② 학력별 당뇨병 비율 (낮을수록 ↑)")

# Physical activity (protective)
pa = q(f"SELECT PhysActivity, {R} r FROM stg GROUP BY PhysActivity ORDER BY PhysActivity")
bars(ax[1,0], ["운동 안 함","운동 함"], pa.r.tolist(), [CORAL, TEAL],
     "③ 운동 여부별 당뇨병 비율 (보호 요인)")

# HighBP x Obesity combination
comb = q(f"""SELECT HighBP, CASE WHEN BMI>=30 THEN 1 ELSE 0 END ob, {R} r
             FROM stg GROUP BY HighBP, ob ORDER BY HighBP, ob""")
lbl = ["정상혈압\n+정상체중","정상혈압\n+비만","고혈압\n+정상체중","고혈압\n+비만"]
bars(ax[1,1], lbl, comb.r.tolist(), [TEAL, TEALLT, AMBER, CORAL],
     "④ 고혈압 × 비만 조합 (겹칠수록 ↑)")

plt.tight_layout()
plt.savefig("extra_analysis_charts.png", bbox_inches="tight", facecolor="white")
print("saved extra_analysis_charts.png")
