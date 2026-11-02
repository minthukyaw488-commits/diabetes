const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.defineLayout({ name: "W", width: 13.3, height: 7.5 });
p.layout = "W";

// ---------- design system (matches Stage 1 deck) ----------
const INK="17211F", TEAL="0E7C74", DEEP="0A413D", CORAL="DD6B4D",
      MIST="EDF1F0", MUT="7C8A87", HAIR="DBE4E1", PAPER="FFFFFF", TEALLT="9FC6C1",
      TEALSOFT="E3F0EE", CORALSOFT="F7E4DD";
const F="Malgun Gothic";
const W=13.3, H=7.5, M=0.8;
const IMG="/home/user/diabetes/";

let N=1;
function page(s, dark){ N++;
  s.addText(String(N).padStart(2,"0")+"  /  10", { x:W-2.0, y:H-0.52, w:1.5, h:0.3,
    isTextBox:true, align:"right", margin:0, fontFace:F, fontSize:9,
    color: dark?TEALLT:MUT, charSpacing:1 });
}
function kicker(s, t, dark){
  s.addText(t.toUpperCase(), { x:M, y:0.62, w:11, h:0.3, isTextBox:true, margin:0,
    fontFace:F, fontSize:11, bold:true, color: dark?TEALLT:TEAL, charSpacing:3 });
}
function head(s, k, title){
  kicker(s,k,false);
  s.addText(title, { x:M, y:0.95, w:11.7, h:0.7, isTextBox:true, margin:0,
    fontFace:F, fontSize:27, bold:true, color:INK });
}
function hair(s, x, y, w, color){
  s.addShape(p.ShapeType.line, { x, y, w, h:0, line:{ color: color||HAIR, width:1 } });
}
function chip(s, x, y, w, n, t){
  s.addText(n, { x, y, w:0.9, h:0.6, isTextBox:true, margin:0, fontFace:F, fontSize:22, bold:true, color:TEAL });
  s.addText(t, { x:x+0.75, y, w:w-0.75, h:0.6, isTextBox:true, valign:"middle", margin:0, fontFace:F, fontSize:13.5, color:INK });
}

// ============================================================ 1. TITLE
let s = p.addSlide(); s.background={color:DEEP};
s.addText("데이터 웨어하우스 프로젝트 · 2단계", { x:M, y:1.85, w:10, h:0.35, isTextBox:true, margin:0,
  fontFace:F, fontSize:13, bold:true, color:TEALLT, charSpacing:3 });
s.addText("당뇨병 예측 모델링", { x:M, y:2.35, w:11.7, h:1.1, isTextBox:true, margin:0,
  fontFace:F, fontSize:50, bold:true, color:PAPER });
hair(s, M, 3.75, 2.2, CORAL);
s.addText("Python에서 Oracle DB 연동 · 전처리 · 머신러닝 최적 모델 도출", { x:M, y:3.95, w:11.5, h:0.5, isTextBox:true, margin:0,
  fontFace:F, fontSize:18, color:TEALLT });
s.addText([
  { text:"RandomForest", options:{ bold:true, color:PAPER } },
  { text:"      236,378건 × 22변수      암호화 모델 저장", options:{ color:TEALLT } },
], { x:M, y:6.35, w:11.5, h:0.35, isTextBox:true, margin:0, fontFace:F, fontSize:13 });
s.addText("22619014 양다윗 · 24619042 민뚜쩌 · 24619040 한지은", { x:M, y:6.75, w:11, h:0.3, isTextBox:true, margin:0,
  fontFace:F, fontSize:11, color:MUT });

// ============================================================ 2. OVERVIEW / GOAL
s = p.addSlide(); s.background={color:PAPER};
kicker(s,"프로젝트 개요",false);
s.addText([
  { text:"1단계에서 만든 DB를 ", options:{ color:INK } },
  { text:"Python으로 연동", options:{ color:TEAL, bold:true } },
  { text:"하고,\n최적의 ", options:{ color:INK } },
  { text:"예측 모델", options:{ color:CORAL, bold:true } },
  { text:"을 만듭니다.", options:{ color:INK } },
], { x:M, y:1.15, w:11.3, h:1.5, isTextBox:true, margin:0, fontFace:F, fontSize:26, bold:true, lineSpacingMultiple:1.15 });
s.addText("정규화된 Oracle DB에서 데이터를 불러와 전처리한 뒤, 여러 기법을 비교·튜닝해 최적 모델을 암호화 파일로 저장합니다.",
  { x:M, y:2.85, w:11, h:0.5, isTextBox:true, margin:0, fontFace:F, fontSize:14, color:MUT });
hair(s, M, 3.7, W-2*M);
const goals=[["01","Oracle DB 연동 — oracledb"],
             ["02","필요 데이터 가져오기 — 4개 테이블 JOIN"],
             ["03","데이터 전처리 — 파생변수·분할"],
             ["04","모델링·튜닝 — 최적 모델 암호화 저장"]];
goals.forEach((q,i)=>{ const col=i%2,row=Math.floor(i/2);
  const x=M+col*6.05, y=4.1+row*1.35;
  s.addText(q[0], { x, y, w:1.1, h:0.9, isTextBox:true, margin:0, fontFace:F, fontSize:34, bold:true, color:MIST });
  s.addText(q[1], { x:x+1.15, y:y+0.06, w:4.8, h:0.9, isTextBox:true, valign:"middle", margin:0, fontFace:F, fontSize:14.5, color:INK });
});
page(s);

// ============================================================ 3. PIPELINE FLOW
s = p.addSlide(); s.background={color:PAPER};
head(s,"수행 흐름","분석 파이프라인");
const steps=[["①","DB 연동","oracledb\nFREEPDB1 접속"],
             ["②","데이터","4개 테이블 JOIN\n→ DataFrame"],
             ["③","전처리","결측치·이상치\n파생변수·분할"],
             ["④","모델링","RF vs XGBoost\nGridSearch 튜닝"],
             ["⑤","저장","암호화 pickle\n(best_model.enc)"]];
const bw=2.08, gap=0.32, startx=M, by=2.9;
steps.forEach((st,i)=>{
  const x=startx+i*(bw+gap);
  s.addShape(p.ShapeType.roundRect, { x, y:by, w:bw, h:2.0, rectRadius:0.08,
    fill:{color: i===3?TEALSOFT:PAPER}, line:{color: i===3?TEAL:HAIR, width:1} });
  s.addText(st[0], { x, y:by+0.18, w:bw, h:0.5, isTextBox:true, align:"center", margin:0, fontFace:F, fontSize:22, bold:true, color:TEAL });
  s.addText(st[1], { x, y:by+0.72, w:bw, h:0.4, isTextBox:true, align:"center", margin:0, fontFace:F, fontSize:15, bold:true, color:INK });
  s.addText(st[2], { x, y:by+1.15, w:bw, h:0.7, isTextBox:true, align:"center", margin:0, fontFace:F, fontSize:11, color:MUT, lineSpacingMultiple:1.05 });
  if(i<4) s.addText("→", { x:x+bw-0.02, y:by+0.6, w:gap+0.04, h:0.6, isTextBox:true, align:"center", valign:"middle", margin:0, fontFace:F, fontSize:18, color:TEALLT });
});
s.addText("평가 항목 4가지(DB연동·데이터·전처리·모델링/저장)를 순서대로 모두 수행합니다.",
  { x:M, y:5.5, w:11.7, h:0.4, isTextBox:true, margin:0, fontFace:F, fontSize:13.5, color:MUT });
page(s);

// ============================================================ 4. DB CONNECT + FETCH
s = p.addSlide(); s.background={color:PAPER};
head(s,"① DB 연동 · ② 데이터 가져오기","Python에서 Oracle DB 연결");
// left: code-ish card
s.addShape(p.ShapeType.roundRect, { x:M, y:2.0, w:6.0, h:2.7, rectRadius:0.06, fill:{color:"0C2E2B"}, line:{color:DEEP,width:1} });
s.addText([
  {text:"con = oracledb.connect(\n", options:{color:TEALLT}},
  {text:"    user=\"system\",\n", options:{color:PAPER}},
  {text:"    password=\"****\",\n", options:{color:PAPER}},
  {text:"    dsn=\"localhost:1521/FREEPDB1\")\n\n", options:{color:PAPER}},
  {text:"df = pd.read_sql(JOIN_4_TABLES, con)", options:{color:"F2C9A0"}},
], { x:M+0.3, y:2.25, w:5.5, h:2.2, isTextBox:true, margin:0, fontFace:"Consolas", fontSize:13, lineSpacingMultiple:1.2 });
// right: result stats
s.addText("가져온 데이터", { x:7.3, y:2.0, w:5, h:0.4, isTextBox:true, margin:0, fontFace:F, fontSize:12, bold:true, color:TEAL, charSpacing:2 });
s.addText("236,378", { x:7.25, y:2.4, w:5.5, h:1.1, isTextBox:true, margin:0, fontFace:F, fontSize:60, bold:true, color:TEAL });
s.addText("행  ·  22개 변수를 하나의 DataFrame으로", { x:7.3, y:3.55, w:5.3, h:0.4, isTextBox:true, margin:0, fontFace:F, fontSize:14, color:MUT });
hair(s, 7.3, 4.2, 5.2);
s.addText([
  {text:"patient  ⋈  health_exam  ⋈  lifestyle  ⋈  diagnosis\n", options:{color:INK, bold:true}},
  {text:"patient_id 기준 4개 테이블 JOIN", options:{color:MUT}},
], { x:7.3, y:4.35, w:5.3, h:0.9, isTextBox:true, margin:0, fontFace:F, fontSize:13, lineSpacingMultiple:1.3 });
s.addText("✓  1단계 DB 접속 성공  ✓  분석에 필요한 전체 변수 확보", { x:M, y:5.6, w:11.7, h:0.4, isTextBox:true, margin:0, fontFace:F, fontSize:13.5, color:TEAL, bold:true });
page(s);

// ============================================================ 5. PREPROCESS
s = p.addSlide(); s.background={color:PAPER};
head(s,"③ 데이터 전처리","모델 학습을 위한 데이터 정리");
const pp=[["결측치","0건 — 확인 결과 없음, 추가 처리 불필요"],
          ["이상치","BMI 12~60 — 1단계에서 극단값 상한 처리 완료"],
          ["파생변수","risk_count 생성 — 고혈압·고콜레스테롤·흡연·비만·심장질환·뇌졸중 합산 (0~6)"],
          ["데이터 분할","계층 샘플링 — train 189,102 / test 47,276 (클래스 비율 유지)"]];
let py=2.0;
pp.forEach((r,i)=>{
  s.addShape(p.ShapeType.rect, { x:M, y:py+0.05, w:0.12, h:0.9, fill:{color: i===2?CORAL:TEAL}, line:{type:"none"} });
  s.addText(r[0], { x:M+0.35, y:py, w:2.6, h:0.9, isTextBox:true, valign:"middle", margin:0, fontFace:F, fontSize:16, bold:true, color:INK });
  s.addText(r[1], { x:M+3.1, y:py, w:8.6, h:0.9, isTextBox:true, valign:"middle", margin:0, fontFace:F, fontSize:14, color:MUT });
  py+=1.1;
});
s.addText("파생변수 risk_count는 변수 중요도 상위권에 올라 유의미했습니다.", { x:M, y:6.5, w:11.7, h:0.4,
  isTextBox:true, margin:0, fontFace:F, fontSize:13, color:CORAL, bold:true });
page(s);

// ============================================================ 6. MODEL COMPARISON
s = p.addSlide(); s.background={color:PAPER};
head(s,"④ 모델링","여러 기법 비교 — 최적 모델 선정");
s.addImage({ path:IMG+"s2_fig_models.png", x:M, y:1.85, w:7.0, h:4.0, sizing:{type:"contain", w:7.0, h:4.0} });
// right insight
s.addShape(p.ShapeType.roundRect, { x:8.1, y:2.0, w:4.4, h:3.7, rectRadius:0.06, fill:{color:MIST}, line:{type:"none"} });
s.addText("왜 RandomForest?", { x:8.35, y:2.2, w:4, h:0.4, isTextBox:true, margin:0, fontFace:F, fontSize:15, bold:true, color:TEAL });
s.addText([
  {text:"XGBoost는 정확도(0.84)가 높지만, ", options:{color:INK}},
  {text:"다수 클래스(정상)에 치우쳐 ", options:{color:INK}},
  {text:"당뇨를 잘 못 잡습니다.\n\n", options:{color:INK}},
  {text:"불균형 데이터에서는 ", options:{color:INK}},
  {text:"macro-F1", options:{color:CORAL, bold:true}},
  {text:"이 공정한 지표이며, 이 기준으로 ", options:{color:INK}},
  {text:"RandomForest", options:{color:TEAL, bold:true}},
  {text:"를 최종 선택했습니다.", options:{color:INK}},
], { x:8.35, y:2.65, w:3.95, h:3.0, isTextBox:true, margin:0, fontFace:F, fontSize:13.5, lineSpacingMultiple:1.25 });
page(s);

// ============================================================ 7. TUNING + CONFUSION
s = p.addSlide(); s.background={color:PAPER};
head(s,"④ 하이퍼파라미터 튜닝 · 평가","GridSearch 튜닝과 혼동행렬");
s.addImage({ path:IMG+"s2_fig_confusion.png", x:7.4, y:1.85, w:4.6, h:4.0, sizing:{type:"contain", w:4.6, h:4.0} });
s.addText("GridSearchCV 튜닝", { x:M, y:2.0, w:6, h:0.4, isTextBox:true, margin:0, fontFace:F, fontSize:15, bold:true, color:TEAL });
s.addText([
  {text:"n_estimators, max_depth, min_samples_leaf 등\n조합을 3-fold 교차검증으로 탐색\n\n", options:{color:MUT}},
  {text:"최적: ", options:{color:INK, bold:true}},
  {text:"n_estimators=200, min_samples_leaf=5\n\n", options:{color:INK}},
  {text:"macro-F1 0.444   ·   accuracy 0.758", options:{color:TEAL, bold:true}},
], { x:M, y:2.5, w:6.0, h:2.0, isTextBox:true, margin:0, fontFace:F, fontSize:14, lineSpacingMultiple:1.25 });
hair(s, M, 4.7, 6.0);
s.addText([
  {text:"당뇨 재현율 73%", options:{color:CORAL, bold:true}},
  {text:" — 실제 당뇨 환자 10명 중 7명을 잡아냄.\n", options:{color:INK}},
  {text:"전당뇨는 표본이 적어(2%) 정확도가 낮음 (불균형 한계).", options:{color:MUT}},
], { x:M, y:4.85, w:6.1, h:1.1, isTextBox:true, margin:0, fontFace:F, fontSize:13, lineSpacingMultiple:1.2 });
page(s);

// ============================================================ 8. FEATURE IMPORTANCE
s = p.addSlide(); s.background={color:PAPER};
head(s,"④ 분석 — 변수 중요도","어떤 요인이 당뇨를 예측하는가");
s.addImage({ path:IMG+"s2_fig_importance.png", x:M, y:1.85, w:7.3, h:4.2, sizing:{type:"contain", w:7.3, h:4.2} });
s.addShape(p.ShapeType.roundRect, { x:8.4, y:2.0, w:4.1, h:3.9, rectRadius:0.06, fill:{color:TEALSOFT}, line:{type:"none"} });
s.addText("핵심 인사이트", { x:8.65, y:2.2, w:3.6, h:0.4, isTextBox:true, margin:0, fontFace:F, fontSize:15, bold:true, color:TEAL });
s.addText([
  {text:"• BMI·연령·소득", options:{color:INK, bold:true}},
  {text:"이 가장 강한 예측 변수\n\n", options:{color:INK}},
  {text:"• 파생변수 risk_count", options:{color:CORAL, bold:true}},
  {text:"가 상위 4위 → 복합 위험도가 유의미함을 확인\n\n", options:{color:INK}},
  {text:"• 생활습관보다 ", options:{color:INK}},
  {text:"신체·사회경제 지표", options:{color:INK, bold:true}},
  {text:"의 기여가 큼", options:{color:INK}},
], { x:8.65, y:2.65, w:3.65, h:3.1, isTextBox:true, margin:0, fontFace:F, fontSize:13.5, lineSpacingMultiple:1.2 });
page(s);

// ============================================================ 9. SAVE + PREDICT
s = p.addSlide(); s.background={color:PAPER};
head(s,"④ 최적 모델 저장 · 예측","암호화 저장과 예측 데모");
// left: save
s.addText("암호화 저장", { x:M, y:2.0, w:5, h:0.4, isTextBox:true, margin:0, fontFace:F, fontSize:15, bold:true, color:TEAL });
s.addShape(p.ShapeType.roundRect, { x:M, y:2.45, w:5.6, h:1.9, rectRadius:0.06, fill:{color:"0C2E2B"}, line:{type:"none"} });
s.addText([
  {text:"key = Fernet.generate_key()\n", options:{color:TEALLT}},
  {text:"enc = Fernet(key).encrypt(\n", options:{color:PAPER}},
  {text:"        pickle.dumps(best_model))\n", options:{color:PAPER}},
  {text:"→ best_model.enc  +  model.key", options:{color:"F2C9A0"}},
], { x:M+0.3, y:2.7, w:5.1, h:1.5, isTextBox:true, margin:0, fontFace:"Consolas", fontSize:12.5, lineSpacingMultiple:1.25 });
s.addText("키가 없으면 열 수 없는 암호화 파일로 모델을 안전하게 보관.", { x:M, y:4.5, w:5.6, h:0.6, isTextBox:true, margin:0, fontFace:F, fontSize:12.5, color:MUT });
// right: predict demo
s.addText("예측 데모 — 고위험 환자", { x:7.1, y:2.0, w:5.4, h:0.4, isTextBox:true, margin:0, fontFace:F, fontSize:15, bold:true, color:TEAL });
s.addShape(p.ShapeType.roundRect, { x:7.1, y:2.45, w:5.4, h:2.6, rectRadius:0.06, fill:{color:CORALSOFT}, line:{type:"none"} });
s.addText("예측 결과", { x:7.4, y:2.65, w:4.8, h:0.35, isTextBox:true, margin:0, fontFace:F, fontSize:12, color:MUT });
s.addText("당뇨", { x:7.4, y:2.95, w:4.8, h:0.9, isTextBox:true, margin:0, fontFace:F, fontSize:46, bold:true, color:CORAL });
s.addText("확률 71.8%", { x:7.4, y:3.9, w:4.8, h:0.4, isTextBox:true, margin:0, fontFace:F, fontSize:16, bold:true, color:INK });
s.addText("비만·고혈압·고콜레스테롤·심장질환 보유 환자를\n당뇨로 정확히 분류 (정상 12.7% · 전당뇨 15.5%)", { x:7.4, y:4.35, w:4.9, h:0.7, isTextBox:true, margin:0, fontFace:F, fontSize:11.5, color:MUT, lineSpacingMultiple:1.1 });
s.addText("✓  저장한 암호화 모델을 불러와 예측까지 정상 동작 확인", { x:M, y:5.6, w:11.7, h:0.4, isTextBox:true, margin:0, fontFace:F, fontSize:13.5, color:TEAL, bold:true });
page(s);

// ============================================================ 10. ROLES + REFLECTION
s = p.addSlide(); s.background={color:DEEP};
kicker(s,"역할 분담 · 소감",true);
s.addText("팀 역할과 소감", { x:M, y:0.95, w:11, h:0.7, isTextBox:true, margin:0, fontFace:F, fontSize:27, bold:true, color:PAPER });
const roles=[["양다윗","모델 설계 및 성능 비교","여러 기법을 비교·튜닝하며 모델 선택 기준을 이해했습니다."],
             ["민뚜쩌","DB 연동 및 전처리","Python-DB 연동과 전처리 과정을 직접 구현해 보았습니다."],
             ["한지은","모델링·저장 및 발표자료","최적 모델을 암호화 저장하고 예측까지 연결해 보았습니다."]];
let ry=2.1;
roles.forEach((r)=>{
  hair(s, M, ry, W-2*M, "1C4B47");
  s.addText(r[0], { x:M, y:ry+0.2, w:2.4, h:0.6, isTextBox:true, margin:0, fontFace:F, fontSize:18, bold:true, color:TEALLT });
  s.addText(r[1], { x:M+2.6, y:ry+0.22, w:4.0, h:0.6, isTextBox:true, valign:"middle", margin:0, fontFace:F, fontSize:14, bold:true, color:PAPER });
  s.addText(r[2], { x:M+6.8, y:ry+0.22, w:5.0, h:0.6, isTextBox:true, valign:"middle", margin:0, fontFace:F, fontSize:12.5, color:TEALLT });
  ry+=1.35;
});
hair(s, M, ry, W-2*M, "1C4B47");
s.addText("2단계 완료 — RandomForest 최적 모델을 암호화 파일로 저장", { x:M, y:6.5, w:11.7, h:0.4,
  isTextBox:true, margin:0, fontFace:F, fontSize:13, color:TEALLT });
page(s, true);

p.writeFile({ fileName: "/home/user/diabetes/diabetes_project_stage2.pptx" }).then(f=>console.log("saved", f));
