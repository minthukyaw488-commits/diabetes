"""Editorial chart set for the redesigned deck. Consistent palette, minimal chartjunk."""
import pandas as pd, sqlite3
import matplotlib.pyplot as plt
import matplotlib as mpl
import koreanize_matplotlib  # NanumGothic (Korean)

df = pd.read_csv("diabetes_clean.csv"); con = sqlite3.connect(":memory:"); df.to_sql("stg", con, index=False)
R = "ROUND(100.0*SUM(CASE WHEN Diabetes_012=2 THEN 1 ELSE 0 END)/COUNT(*),2)"
q = lambda s: pd.read_sql(s, con)

INK="#17211F"; TEAL="#0E7C74"; TEALLT="#A9CDC8"; CORAL="#DD6B4D"; MUT="#7C8A87"; MIST="#EDF1F0"
mpl.rcParams.update({"font.size":12, "axes.edgecolor":INK, "text.color":INK,
                     "axes.labelcolor":MUT, "xtick.color":MUT, "ytick.color":MUT})

def style(a):
    for s in ["top","right","left"]: a.spines[s].set_visible(False)
    a.spines["bottom"].set_color("#D5DEDC")
    a.tick_params(length=0); a.set_yticks([])

def collabel(a, bars, vals, fmt="{:.0f}%", emph=None, size=13):
    mx=max(vals)
    for i,(b,v) in enumerate(zip(bars,vals)):
        c = CORAL if (emph is not None and i in emph) else INK
        a.text(b.get_x()+b.get_width()/2, v+mx*0.03, fmt.format(v),
               ha="center", fontsize=size, fontweight="bold", color=c)

# ---------- FIG 1: 위험요인 개수 (hero) ----------
d = q(f'''SELECT (HighBP+HighChol+Smoker+(CASE WHEN PhysActivity=0 THEN 1 ELSE 0 END)
      +(CASE WHEN BMI>=30 THEN 1 ELSE 0 END)) rc, {R} r FROM stg GROUP BY rc ORDER BY rc''')
fig,a=plt.subplots(figsize=(7.6,4.6),dpi=200)
colors=[TEALLT]*4+[CORAL,CORAL]; colors=[TEALLT,TEALLT,TEAL,TEAL,CORAL,CORAL]
b=a.bar(range(len(d)), d.r, width=0.66, color=[TEALLT,TEALLT,TEAL,TEAL,"#D98A5E",CORAL])
a.set_xticks(range(len(d))); a.set_xticklabels([f"{i}개" for i in d.rc], fontsize=13, color=INK)
a.set_ylim(0,max(d.r)*1.16); style(a); collabel(a,b,d.r.tolist(),emph=[5])
plt.tight_layout(); plt.savefig("fig_risk.png",bbox_inches="tight",facecolor="white"); plt.close()

# ---------- FIG 2: 연령 + BMI (2 panel) ----------
age=q(f'''SELECT CASE WHEN Age<=1 THEN \"18-24\" WHEN Age<=3 THEN \"25-34\" WHEN Age<=5 THEN \"35-44\"
   WHEN Age<=7 THEN \"45-54\" WHEN Age<=9 THEN \"55-64\" WHEN Age<=11 THEN \"65-74\" ELSE \"75+\" END g,{R} r
   FROM stg GROUP BY g ORDER BY g''')
bmi=q(f'''SELECT CASE WHEN BMI<18.5 THEN \"저체중\" WHEN BMI<25 THEN \"정상\" WHEN BMI<30 THEN \"과체중\"
   ELSE \"비만\" END c,{R} r FROM stg GROUP BY c ORDER BY MIN(BMI)''')
fig,ax=plt.subplots(1,2,figsize=(11.4,4.5),dpi=200)
ax[0].fill_between(range(len(age)), age.r, color=TEAL, alpha=0.10)
ax[0].plot(range(len(age)), age.r, color=TEAL, lw=2.6, marker="o", ms=7, mfc=TEAL, mec="white", mew=1.4)
ax[0].scatter([len(age)-1],[age.r.iloc[-1]], s=90, color=CORAL, zorder=5, ec="white", lw=1.4)
for i,v in enumerate(age.r):
    ax[0].text(i, v+1.1, f"{v:.0f}", ha="center", fontsize=11, fontweight="bold",
               color=CORAL if i==len(age)-1 else INK)
ax[0].set_xticks(range(len(age))); ax[0].set_xticklabels(age.g, fontsize=10.5, color=MUT)
ax[0].set_ylim(0,max(age.r)*1.22); style(ax[0])
ax[0].set_title("연령대별 당뇨병 비율 (%)", fontsize=13, color=INK, fontweight="bold", loc="left", pad=10)
b=ax[1].bar(range(len(bmi)), bmi.r, width=0.6, color=[TEALLT,TEALLT,"#D98A5E",CORAL])
ax[1].set_xticks(range(len(bmi))); ax[1].set_xticklabels(bmi.c, fontsize=11.5, color=INK)
ax[1].set_ylim(0,max(bmi.r)*1.16); style(ax[1]); collabel(ax[1],b,bmi.r.tolist(),emph=[3],size=12)
ax[1].set_title("BMI 구간별 당뇨병 비율 (%)", fontsize=13, color=INK, fontweight="bold", loc="left", pad=10)
plt.tight_layout(); plt.savefig("fig_age_bmi.png",bbox_inches="tight",facecolor="white"); plt.close()

# ---------- FIG 3: 소득 + 운동 + 조합 (3 panel) ----------
inc=q(f"SELECT Income,{R} r FROM stg GROUP BY Income ORDER BY Income")
pa=q(f"SELECT PhysActivity,{R} r FROM stg GROUP BY PhysActivity ORDER BY PhysActivity")
cb=q(f'''SELECT HighBP,CASE WHEN BMI>=30 THEN 1 ELSE 0 END ob,{R} r FROM stg GROUP BY HighBP,ob ORDER BY HighBP,ob''')
fig,ax=plt.subplots(1,3,figsize=(13,4.2),dpi=200)
# income as descending line
ax[0].plot(inc.Income, inc.r, color=TEAL, lw=2.6, marker="o", ms=5, mfc=TEAL, mec="white")
ax[0].fill_between(inc.Income, inc.r, color=TEAL, alpha=0.09)
ax[0].text(inc.Income.iloc[0], inc.r.iloc[0]+1.2, f"{inc.r.iloc[0]:.0f}%", fontsize=11, fontweight="bold", color=CORAL, ha="center")
ax[0].text(inc.Income.iloc[-1], inc.r.iloc[-1]+1.2, f"{inc.r.iloc[-1]:.0f}%", fontsize=11, fontweight="bold", color=TEAL, ha="center")
ax[0].set_xticks([1,11]); ax[0].set_xticklabels(["저소득","고소득"], fontsize=11, color=INK)
ax[0].set_ylim(0,max(inc.r)*1.2); style(ax[0])
ax[0].set_title("소득 수준별 (낮을수록 ↑)", fontsize=12.5, color=INK, fontweight="bold", loc="left", pad=10)
b=ax[1].bar([0,1], pa.r, width=0.5, color=[CORAL,TEAL])
ax[1].set_xticks([0,1]); ax[1].set_xticklabels(["운동 안 함","운동 함"], fontsize=11.5, color=INK)
ax[1].set_ylim(0,max(pa.r)*1.18); style(ax[1]); collabel(ax[1],b,pa.r.tolist(),size=12)
ax[1].set_title("운동 여부 (보호 요인)", fontsize=12.5, color=INK, fontweight="bold", loc="left", pad=10)
lab=["정상혈압\n정상체중","정상혈압\n비만","고혈압\n정상체중","고혈압\n비만"]
b=ax[2].bar(range(4), cb.r, width=0.62, color=[TEAL,TEALLT,"#D98A5E",CORAL])
ax[2].set_xticks(range(4)); ax[2].set_xticklabels(lab, fontsize=9.5, color=MUT)
ax[2].set_ylim(0,max(cb.r)*1.18); style(ax[2]); collabel(ax[2],b,cb.r.tolist(),emph=[3],size=11.5)
ax[2].set_title("고혈압 × 비만 조합", fontsize=12.5, color=INK, fontweight="bold", loc="left", pad=10)
plt.tight_layout(); plt.savefig("fig_social.png",bbox_inches="tight",facecolor="white"); plt.close()

print("saved fig_risk.png, fig_age_bmi.png, fig_social.png")
