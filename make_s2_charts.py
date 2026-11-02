"""Stage 2 presentation charts — model comparison, confusion matrix, feature importance."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import koreanize_matplotlib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix

INK="#17211F"; TEAL="#0E7C74"; CORAL="#DD6B4D"; MUT="#7C8A87"; HAIR="#D9E1DF"; TEALSOFT="#E3F0EE"

# ---- data = same as the DB (diabetes_clean.csv was loaded into Oracle) ----
df = pd.read_csv("diabetes_clean.csv").rename(columns={
    "Diabetes_012":"diabetes_status","HighBP":"high_bp","HighChol":"high_chol",
    "HeartDiseaseorAttack":"heart_disease","Stroke":"stroke","Smoker":"smoker","BMI":"bmi"})
df.columns=[c.lower() for c in df.columns]
df["risk_count"]=(df["high_bp"]+df["high_chol"]+df["smoker"]+(df["bmi"]>=30).astype(int)
                  +df["heart_disease"]+df["stroke"])
X=df.drop(columns=["diabetes_status"]); y=df["diabetes_status"].astype(int)
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=0.2,random_state=42,stratify=y)

rf=RandomForestClassifier(n_estimators=200,min_samples_leaf=5,class_weight="balanced",
                          n_jobs=-1,random_state=42).fit(Xtr,ytr)
pred=rf.predict(Xte)

def style(ax):
    for s in ["top","right"]: ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(HAIR); ax.spines["bottom"].set_color(HAIR)
    ax.tick_params(length=0,labelcolor=MUT)

# ============ 1) model comparison (real numbers from the DB run) ============
fig,ax=plt.subplots(figsize=(8.4,4.8),dpi=200)
models=["RandomForest","XGBoost"]; x=np.arange(2); w=0.36
f1=[0.4435,0.3994]; acc=[0.7576,0.8405]
b1=ax.bar(x-w/2,f1,w,label="macro-F1",color=CORAL)
b2=ax.bar(x+w/2,acc,w,label="정확도(accuracy)",color=TEAL)
for b in list(b1)+list(b2):
    ax.text(b.get_x()+b.get_width()/2,b.get_height()+.012,f"{b.get_height():.3f}",
            ha="center",fontsize=10,fontweight="bold",color=INK)
ax.set_xticks(x); ax.set_xticklabels(models,fontsize=12,color=INK)
ax.set_ylim(0,1); ax.set_ylabel("점수",color=MUT)
ax.axhline(0,color=HAIR)
ax.set_title("모델 성능 비교  ·  최적 모델 = RandomForest",fontsize=14,fontweight="bold",
             color="#0C3B3B",loc="left",pad=14)
ax.legend(frameon=False,fontsize=10,loc="upper center",ncol=2,bbox_to_anchor=(.5,-.08))
style(ax); plt.tight_layout(); plt.savefig("s2_fig_models.png",bbox_inches="tight",facecolor="white")
print("saved s2_fig_models.png")

# ============ 2) confusion matrix (row-normalized = recall) ============
cm=confusion_matrix(yte,pred); cmn=cm/cm.sum(axis=1,keepdims=True)
labels=["정상","전당뇨","당뇨"]
cmap=LinearSegmentedColormap.from_list("teal",["#ffffff",TEAL])
fig,ax=plt.subplots(figsize=(6.2,5.4),dpi=200)
im=ax.imshow(cmn,cmap=cmap,vmin=0,vmax=1)
for i in range(3):
    for j in range(3):
        ax.text(j,i,f"{cmn[i,j]*100:.0f}%\n({cm[i,j]:,})",ha="center",va="center",
                fontsize=11,fontweight="bold",color="white" if cmn[i,j]>.5 else INK)
ax.set_xticks(range(3)); ax.set_xticklabels(labels,fontsize=11,color=INK)
ax.set_yticks(range(3)); ax.set_yticklabels(labels,fontsize=11,color=INK)
ax.set_xlabel("예측",color=MUT); ax.set_ylabel("실제",color=MUT)
ax.set_title("혼동행렬 (행 기준 비율 = 재현율)",fontsize=13,fontweight="bold",
             color="#0C3B3B",loc="left",pad=12)
for s in ax.spines.values(): s.set_visible(False)
ax.tick_params(length=0)
plt.tight_layout(); plt.savefig("s2_fig_confusion.png",bbox_inches="tight",facecolor="white")
print("saved s2_fig_confusion.png")

# ============ 3) feature importance (top 10) ============
imp=pd.Series(rf.feature_importances_,index=X.columns).sort_values(ascending=True).tail(10)
ko={"gen_hlth":"전반적 건강","genhlth":"전반적 건강","bmi":"BMI","high_bp":"고혈압","age":"연령",
    "income":"소득","diff_walk":"보행곤란","diffwalk":"보행곤란","phys_hlth":"신체건강일수",
    "physhlth":"신체건강일수","risk_count":"위험요인 수(파생)","high_chol":"고콜레스테롤",
    "education":"학력","ment_hlth":"정신건강일수","menthlth":"정신건강일수","heart_disease":"심장질환",
    "fruits":"과일 섭취","veggies":"채소 섭취","phys_activity":"운동","physactivity":"운동",
    "smoker":"흡연","chol_check":"콜레스테롤 검사","cholcheck":"콜레스테롤 검사"}
names=[ko.get(i,i) for i in imp.index]
fig,ax=plt.subplots(figsize=(8.2,5.0),dpi=200)
colors=[CORAL if n=="위험요인 수(파생)" else TEAL for n in names]
ax.barh(range(len(imp)),imp.values,color=colors)
for i,v in enumerate(imp.values):
    ax.text(v+.002,i,f"{v:.3f}",va="center",fontsize=9,color=MUT)
ax.set_yticks(range(len(imp))); ax.set_yticklabels(names,fontsize=11,color=INK)
ax.set_xlabel("중요도",color=MUT)
ax.set_title("변수 중요도 Top 10  ·  RandomForest",fontsize=14,fontweight="bold",
             color="#0C3B3B",loc="left",pad=12)
ax.text(.98,.04,"코랄 = 파생변수",transform=ax.transAxes,ha="right",fontsize=9,color=CORAL)
style(ax); plt.tight_layout(); plt.savefig("s2_fig_importance.png",bbox_inches="tight",facecolor="white")
print("saved s2_fig_importance.png")
print("\nRF macro-F1 check: done — charts ready")
