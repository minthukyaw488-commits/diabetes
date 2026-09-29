"""Odds-ratio forest plot (univariate) — classification-appropriate view."""
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency
import koreanize_matplotlib  # Korean font

df = pd.read_csv("diabetes_clean.csv")
df["target"] = (df["Diabetes_012"] == 2).astype(int)

# factor : Korean label
factors = [
    ("HighBP", "고혈압"), ("HeartDiseaseorAttack", "심장질환"),
    ("DiffWalk", "보행 곤란"), ("HighChol", "고콜레스테롤"),
    ("Stroke", "뇌졸중"), ("Smoker", "흡연"),
    ("Veggies", "채소 섭취"), ("Fruits", "과일 섭취"),
    ("PhysActivity", "운동"), ("HvyAlcoholConsump", "과음"),
]

rows = []
for col, ko in factors:
    ct = pd.crosstab(df[col], df["target"])
    a, b = ct.loc[1, 1], ct.loc[1, 0]
    c, d = ct.loc[0, 1], ct.loc[0, 0]
    OR = (a * d) / (b * c)
    se = np.sqrt(1/a + 1/b + 1/c + 1/d)
    lo, hi = np.exp(np.log(OR) - 1.96*se), np.exp(np.log(OR) + 1.96*se)
    _, p, _, _ = chi2_contingency(ct)
    rows.append((ko, OR, lo, hi, p))

rows.sort(key=lambda r: r[1])          # ascending OR
labels = [r[0] for r in rows]
ors    = [r[1] for r in rows]
los    = [r[2] for r in rows]
his    = [r[3] for r in rows]

INK="#17211F"; TEAL="#0E7C74"; CORAL="#DD6B4D"; MUT="#7C8A87"; HAIR="#D9E1DF"
fig, ax = plt.subplots(figsize=(9.2, 5.6), dpi=200)
y = np.arange(len(labels))

for i,(orr,lo,hi) in enumerate(zip(ors,los,his)):
    color = CORAL if orr > 1 else TEAL
    ax.plot([lo, hi], [i, i], color=color, lw=2.2, solid_capstyle="round", zorder=2)
    ax.scatter([orr], [i], s=70, color=color, zorder=3, ec="white", lw=1.2)
    ax.text(hi*1.04, i, f"{orr:.2f}", va="center", fontsize=11, fontweight="bold", color=color)

ax.axvline(1.0, color=MUT, lw=1.2, ls="--", zorder=1)
ax.text(1.02, -0.75, "기준 1.0", color=MUT, fontsize=9, va="center", ha="left")

ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=12, color=INK)
ax.set_xscale("log")
ax.set_xticks([0.3, 0.5, 1, 2, 3, 5])
ax.get_xaxis().set_minor_locator(plt.NullLocator())
ax.get_xaxis().set_major_formatter(plt.FixedFormatter(["0.3","0.5","1","2","3","5"]))
ax.set_xlabel("오즈비 (Odds Ratio, 로그 스케일)", fontsize=11, color=MUT)
ax.set_xlim(0.3, 7); ax.set_ylim(-1.2, len(labels)-0.3)
for s in ["top","right","left"]: ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(HAIR); ax.tick_params(length=0, labelcolor=MUT)
ax.set_title("당뇨병 위험요인 오즈비 (단변량)   ·   전 요인 p < 0.001",
             fontsize=14, fontweight="bold", color="#0C3B3B", pad=16, loc="left")
# legend
ax.scatter([],[],color=CORAL,label="위험 요인 (OR>1)")
ax.scatter([],[],color=TEAL,label="보호 요인 (OR<1)")
ax.legend(loc="lower right", frameon=False, fontsize=10)

plt.tight_layout()
plt.savefig("odds_ratio_chart.png", bbox_inches="tight", facecolor="white")
print("saved odds_ratio_chart.png")
