const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.defineLayout({ name: "W", width: 13.3, height: 7.5 });
p.layout = "W";

// ---------- design system ----------
const INK="17211F", TEAL="0E7C74", DEEP="0A413D", CORAL="DD6B4D",
      MIST="EDF1F0", MUT="7C8A87", HAIR="DBE4E1", PAPER="FFFFFF", TEALLT="9FC6C1";
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

// ============================================================ 1. TITLE
let s = p.addSlide(); s.background={color:DEEP};
s.addText("데이터 웨어하우스 프로젝트 · 1단계", { x:M, y:1.85, w:10, h:0.35, isTextBox:true, margin:0,
  fontFace:F, fontSize:13, bold:true, color:TEALLT, charSpacing:3 });
s.addText("당뇨병 위험요인 분석", { x:M, y:2.35, w:11.7, h:1.1, isTextBox:true, margin:0,
  fontFace:F, fontSize:50, bold:true, color:PAPER });
hair(s, M, 3.75, 2.2, CORAL);
s.addText("SQL 기반 데이터 웨어하우스 설계와 위험요인 규명", { x:M, y:3.95, w:11, h:0.5, isTextBox:true, margin:0,
  fontFace:F, fontSize:18, color:TEALLT });
s.addText([
  { text:"CDC BRFSS 2021", options:{ bold:true, color:PAPER } },
  { text:"      236,378건      Oracle Database", options:{ color:TEALLT } },
], { x:M, y:6.35, w:11, h:0.35, isTextBox:true, margin:0, fontFace:F, fontSize:13 });
s.addText("조 이름 · 발표일 2025.__.__", { x:M, y:6.75, w:11, h:0.3, isTextBox:true, margin:0,
  fontFace:F, fontSize:11, color:MUT });

// ============================================================ 2. OVERVIEW
s = p.addSlide(); s.background={color:PAPER};
kicker(s,"프로젝트 개요",false);
s.addText([
  { text:"머신러닝 예측이 아니라, ", options:{ color:INK } },
  { text:"DB를 설계하고 SQL로", options:{ color:TEAL, bold:true } },
  { text:" 위험요인을 분석합니다.", options:{ color:INK } },
], { x:M, y:1.15, w:11.3, h:1.2, isTextBox:true, margin:0, fontFace:F, fontSize:26, bold:true, lineSpacingMultiple:1.15 });
s.addText("수업 목적에 맞춰 원본 데이터를 정규화된 DB(DW)에 저장하고, SQL 질의로 분석 결과를 도출했습니다.",
  { x:M, y:2.5, w:10.5, h:0.5, isTextBox:true, margin:0, fontFace:F, fontSize:14, color:MUT });
hair(s, M, 3.35, W-2*M);
const qs=[["01","연령·성별에 따라 당뇨병 비율은 어떻게 다른가"],
          ["02","BMI가 높아질수록 위험도 높아지는가"],
          ["03","고혈압·흡연·운동 부족은 어떤 관계인가"],
          ["04","위험요인이 겹치면 얼마나 더 위험한가"]];
qs.forEach((q,i)=>{ const col=i%2,row=Math.floor(i/2);
  const x=M+col*6.05, y=3.75+row*1.45;
  s.addText(q[0], { x, y, w:1.1, h:0.9, isTextBox:true, margin:0, fontFace:F, fontSize:34, bold:true, color:MIST });
  s.addText(q[1], { x:x+1.15, y:y+0.06, w:4.7, h:0.9, isTextBox:true, valign:"middle", margin:0, fontFace:F, fontSize:14.5, color:INK });
});
page(s);

// ============================================================ 3. DATA (large stat)
s = p.addSlide(); s.background={color:PAPER};
kicker(s,"데이터",false);
s.addText("분석 데이터", { x:M, y:0.95, w:8, h:0.6, isTextBox:true, margin:0, fontFace:F, fontSize:27, bold:true, color:INK });
s.addText("236,378", { x:M-0.05, y:2.1, w:8.6, h:1.7, isTextBox:true, margin:0, fontFace:F, fontSize:104, bold:true, color:TEAL });
s.addText("건의 응답 기록  ·  CDC BRFSS 2021 건강 설문", { x:M, y:3.75, w:8, h:0.4, isTextBox:true, margin:0, fontFace:F, fontSize:15, color:MUT });
// right meta stack
const meta=[["22","변수(컬럼)"],["3","당뇨 분류 (정상·전당뇨·당뇨)"],["0","결측치"]];
let my=2.15;
meta.forEach((mm,i)=>{
  s.addText(mm[0], { x:9.5, y:my, w:1.4, h:0.7, isTextBox:true, margin:0, fontFace:F, fontSize:34, bold:true, color:INK });
  s.addText(mm[1], { x:10.7, y:my+0.18, w:2.6, h:0.6, isTextBox:true, valign:"middle", margin:0, fontFace:F, fontSize:12.5, color:MUT });
  if(i<2) hair(s, 9.5, my+0.95, 3.3);
  my+=1.15;
});
hair(s, M, 5.35, W-2*M);
s.addText("주요 변수", { x:M, y:5.5, w:4, h:0.35, isTextBox:true, margin:0, fontFace:F, fontSize:12, bold:true, color:TEAL, charSpacing:2 });
s.addText("당뇨 여부   BMI   고혈압 · 고콜레스테롤   흡연 · 운동   전반적 건강   소득 · 학력",
  { x:M, y:5.9, w:11.7, h:0.5, isTextBox:true, margin:0, fontFace:F, fontSize:14, color:INK });
page(s);

// ============================================================ 4. PREPROCESSING (two-col list)
s = p.addSlide(); s.background={color:PAPER};
head(s,"데이터 전처리","분석 전, 데이터를 정리했습니다");
const pp=[["결측치","확인 결과 없음 — 별도 처리 불필요"],
          ["BMI 이상치","60 초과 비현실적 값 411건을 60으로 조정"],
          ["중복 행","설문 특성상 유효 응답으로 간주해 유지"],
          ["데이터 타입","모든 값을 정수형으로 변환해 DB 저장 최적화"]];
let yy=2.2;
pp.forEach((c,i)=>{
  s.addText(c[0], { x:M, y:yy, w:3.2, h:0.6, isTextBox:true, valign:"middle", margin:0, fontFace:F, fontSize:16, bold:true, color:INK });
  s.addText(c[1], { x:M+3.4, y:yy, w:8.3, h:0.6, isTextBox:true, valign:"middle", margin:0, fontFace:F, fontSize:14.5, color:MUT });
  yy+=0.92; if(i<pp.length-1) hair(s, M, yy-0.16, W-2*M);
});
s.addText("결과 → diabetes_clean.csv", { x:M, y:6.35, w:8, h:0.35, isTextBox:true, margin:0, fontFace:F, fontSize:12.5, italic:true, color:TEAL });
page(s);

// ============================================================ 5. DB DESIGN (schema rows)
s = p.addSlide(); s.background={color:PAPER};
head(s,"DB(DW) 설계","정규화된 5개 테이블로 분리");
const tb=[["PATIENT","환자","patient_id · age · sex · education · income", TEAL],
          ["HEALTH_EXAM","건강검사","exam_id · patient_id · bmi · high_bp · gen_hlth …", INK],
          ["LIFESTYLE","생활습관","lifestyle_id · patient_id · smoker · phys_activity …", INK],
          ["DIAGNOSIS","진단결과","diag_id · patient_id · diabetes_status", INK],
          ["ANALYSIS_RESULT","분석결과","result_id · analysis_name · category · metric_value", CORAL]];
let ty=2.05;
tb.forEach((t,i)=>{
  s.addShape(p.ShapeType.rect, { x:M, y:ty+0.1, w:0.09, h:0.62, fill:{color:t[3]} });
  s.addText(t[0], { x:M+0.28, y:ty, w:3.0, h:0.8, isTextBox:true, valign:"middle", margin:0, fontFace:F, fontSize:15, bold:true, color:INK });
  s.addText(t[1], { x:M+3.25, y:ty, w:1.6, h:0.8, isTextBox:true, valign:"middle", margin:0, fontFace:F, fontSize:12.5, color:MUT });
  s.addText(t[2], { x:M+4.9, y:ty, w:6.8, h:0.8, isTextBox:true, valign:"middle", margin:0, fontFace:"Consolas", fontSize:11, color:MUT });
  ty+=0.88; if(i<tb.length-1) hair(s, M, ty-0.06, W-2*M);
});
s.addText("PK · FK · NOT NULL · CHECK 제약조건 적용", { x:M, y:6.65, w:9, h:0.35, isTextBox:true, margin:0, fontFace:F, fontSize:12, italic:true, color:MUT });
page(s);

// ============================================================ 6. ER DIAGRAM
s = p.addSlide(); s.background={color:PAPER};
head(s,"ER 다이어그램","테이블 간의 관계");
function box(x,y,w,h,name,ko,accent,fillDark){
  s.addShape(p.ShapeType.rect, { x, y, w, h, fill:{color: fillDark?DEEP:PAPER}, line:{color: accent, width:1.25} });
  s.addText([{text:name+"  ",options:{bold:true,color: fillDark?PAPER:INK}},{text:ko,options:{color: fillDark?TEALLT:MUT,fontSize:10}}],
    { x:x+0.15, y, w:w-0.3, h, isTextBox:true, valign:"middle", margin:0, fontFace:F, fontSize:12.5 });
}
box(0.8,2.9,3.0,0.75,"PATIENT","환자",TEAL,true);
box(6.4,2.05,4.1,0.7,"HEALTH_EXAM","건강검사",TEAL,false);
box(6.4,2.95,4.1,0.7,"DIAGNOSIS","진단결과",TEAL,false);
box(6.4,3.85,4.1,0.7,"LIFESTYLE","생활습관",TEAL,false);
box(0.8,5.1,3.0,0.7,"ANALYSIS_RESULT","분석결과",CORAL,false);
[2.4,3.3,4.2].forEach(cy=>{ s.addShape(p.ShapeType.line,{ x:3.8, y:3.27, w:2.6, h:cy-3.27, line:{color:TEAL,width:1.1} }); });
s.addText("1 : N", { x:4.4, y:2.5, w:1, h:0.3, isTextBox:true, margin:0, fontFace:F, fontSize:11, bold:true, color:MUT });
s.addText("한 명의 환자가 patient_id로 건강검사·생활습관·진단 기록과 연결됩니다.\nANALYSIS_RESULT는 분석 결과를 담는 독립 테이블입니다.",
  { x:0.8, y:6.15, w:11.5, h:0.7, isTextBox:true, margin:0, fontFace:F, fontSize:13, color:MUT, lineSpacingMultiple:1.2 });
page(s);

// ============================================================ 7. IMPLEMENTATION (process)
s = p.addSlide(); s.background={color:PAPER};
head(s,"DB 구현","Oracle SQL Developer 작업 흐름");
const st=[["01","테이블 생성","DDL(CREATE TABLE)로 테이블 5개·시퀀스 정의"],
          ["02","데이터 적재","정리된 CSV를 staging 테이블에 입력"],
          ["03","정규화 분배","INSERT INTO … SELECT 로 5개 테이블에 분배"],
          ["04","검증","SELECT로 236,378건 정상 입력 확인"]];
let sx=M;
const cw=(W-2*M-0.9)/4;
st.forEach((t,i)=>{
  const x=M+i*(cw+0.3);
  s.addText(t[0], { x, y:2.3, w:cw, h:0.7, isTextBox:true, margin:0, fontFace:F, fontSize:30, bold:true, color:TEAL });
  s.addText(t[1], { x, y:3.05, w:cw, h:0.4, isTextBox:true, margin:0, fontFace:F, fontSize:15, bold:true, color:INK });
  s.addText(t[2], { x, y:3.5, w:cw, h:1.2, isTextBox:true, margin:0, fontFace:F, fontSize:12.5, color:MUT, lineSpacingMultiple:1.2 });
  if(i<3) s.addText("→", { x:x+cw+0.02, y:2.35, w:0.28, h:0.6, isTextBox:true, align:"center", margin:0, fontFace:F, fontSize:18, color:HAIR });
});
hair(s, M, 5.3, W-2*M);
s.addText([{text:"결과   ",options:{bold:true,color:TEAL}},
  {text:"모든 테이블 236,378건 확인 · 분석 결과 29건 저장",options:{color:INK}}],
  { x:M, y:5.55, w:11.7, h:0.4, isTextBox:true, margin:0, fontFace:F, fontSize:14 });
page(s);

// ============================================================ 8. 실행 화면 (evidence)
s = p.addSlide(); s.background={color:PAPER};
head(s,"실행 화면","SQL Developer 구현 증거");
// two landscape panels (ratio 1.54): each ~5.75 wide -> 3.73 tall
// left: DDL success
s.addShape(p.ShapeType.rect, { x:M-0.03, y:2.12, w:5.81, h:3.79, fill:{color:PAPER}, line:{color:HAIR,width:1} });
s.addImage({ path:IMG+"evidence_ddl.jpg", x:M, y:2.15, w:5.75, h:3.73 });
s.addText([{text:"DDL 실행   ",options:{bold:true,color:TEAL}},{text:"테이블·시퀀스 생성 완료",options:{color:MUT}}],
  { x:M, y:6.05, w:5.75, h:0.35, isTextBox:true, margin:0, fontFace:F, fontSize:12 });
// right: JOIN result
s.addShape(p.ShapeType.rect, { x:6.72, y:2.12, w:5.81, h:3.79, fill:{color:PAPER}, line:{color:HAIR,width:1} });
s.addImage({ path:IMG+"evidence_join.jpg", x:6.75, y:2.15, w:5.75, h:3.73 });
s.addText([{text:"JOIN 조회   ",options:{bold:true,color:TEAL}},{text:"4개 테이블 연결 · 정상 조회",options:{color:MUT}}],
  { x:6.75, y:6.05, w:5.75, h:0.35, isTextBox:true, margin:0, fontFace:F, fontSize:12 });
page(s);

// ============================================================ 9. ANALYSIS PLAN (2단계 예고)
s = p.addSlide(); s.background={color:PAPER};
head(s,"분석 계획","2단계에서 수행할 분석");
s.addText("정규화된 DB를 SQL로 질의해 위험요인을 규명하고, 그 결과를 ANALYSIS_RESULT 테이블에 저장합니다.",
  { x:M, y:1.75, w:11.3, h:0.5, isTextBox:true, margin:0, fontFace:F, fontSize:14.5, color:MUT });
hair(s, M, 2.5, W-2*M);
const plan=[["기술 통계 분석","연령·성별·BMI·소득·학력별 당뇨병 비율","GROUP BY · CASE · AVG"],
            ["조합 · 상호작용","위험요인 개수, 고혈압 × 비만 등 복합 위험","다중 조건 집계"],
            ["통계 검정","요인별 오즈비(Odds Ratio) · 카이제곱 검정","이진 데이터에 적합"],
            ["예측 모델링","로지스틱 회귀로 위험요인 기여도 추정","2 · 3단계 진행"]];
let py2=2.75;
plan.forEach((c,i)=>{
  s.addText(String(i+1).padStart(2,"0"), { x:M, y:py2, w:0.9, h:0.85, isTextBox:true, valign:"middle", margin:0, fontFace:F, fontSize:24, bold:true, color:MIST });
  s.addText(c[0], { x:M+1.05, y:py2, w:3.6, h:0.85, isTextBox:true, valign:"middle", margin:0, fontFace:F, fontSize:15.5, bold:true, color:INK });
  s.addText(c[1], { x:M+4.75, y:py2, w:5.2, h:0.85, isTextBox:true, valign:"middle", margin:0, fontFace:F, fontSize:13, color:MUT });
  s.addText(c[2], { x:M+10.0, y:py2, w:1.7, h:0.85, isTextBox:true, valign:"middle", margin:0, fontFace:F, fontSize:10.5, color:TEAL });
  py2+=0.98; if(i<plan.length-1) hair(s, M, py2-0.1, W-2*M);
});
s.addText("분석 결과 저장 테이블(ANALYSIS_RESULT)까지 1단계에서 설계 완료 → 2단계에서 채웁니다.",
  { x:M, y:6.75, w:11.7, h:0.35, isTextBox:true, margin:0, fontFace:F, fontSize:12, italic:true, color:TEAL });
page(s);

// ============================================================ 9. CONCLUSION + TEAM
s = p.addSlide(); s.background={color:PAPER};
kicker(s,"1단계 마무리",false);
s.addText([{text:"주제 · 데이터 · DB 설계 · 데이터 입력",options:{color:TEAL,bold:true}},{text:"까지\n1단계를 완료했습니다.",options:{color:INK}}],
  { x:M, y:1.15, w:11.3, h:1.4, isTextBox:true, margin:0, fontFace:F, fontSize:25, bold:true, lineSpacingMultiple:1.18 });
hair(s, M, 3.05, W-2*M);
s.addText("역할 분담", { x:M, y:3.3, w:5, h:0.35, isTextBox:true, margin:0, fontFace:F, fontSize:12, bold:true, color:TEAL, charSpacing:2 });
const roles=[["주제·데이터","OOO"],["DB 설계·ER","OOO"],["DB 구현·입력","OOO"],["SQL 분석·발표","OOO"]];
roles.forEach((r,i)=>{ const y=3.75+i*0.62;
  s.addText(r[0], { x:M, y, w:4.2, h:0.5, isTextBox:true, valign:"middle", margin:0, fontFace:F, fontSize:14, color:INK });
  s.addText(r[1], { x:M+4.2, y, w:1.6, h:0.5, isTextBox:true, valign:"middle", margin:0, fontFace:F, fontSize:14, bold:true, color:MUT });
  if(i<3) hair(s, M, y+0.55, 5.8);
});
s.addShape(p.ShapeType.rect, { x:7.3, y:3.75, w:5.2, h:2.55, fill:{color:MIST} });
s.addText("조원 소감", { x:7.6, y:4.0, w:4, h:0.35, isTextBox:true, margin:0, fontFace:F, fontSize:12, bold:true, color:TEAL, charSpacing:2 });
s.addText("조원별로 한 줄씩 소감을 작성해 주세요.", { x:7.6, y:4.45, w:4.6, h:0.5, isTextBox:true, margin:0, fontFace:F, fontSize:13, color:MUT });
page(s);

p.writeFile({ fileName:"/home/user/diabetes/diabetes_project_stage1.pptx" }).then(f=>console.log("saved",f));
