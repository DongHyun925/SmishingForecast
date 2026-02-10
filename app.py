import streamlit as st
import json
import random
import os
import sys
from datetime import datetime

# 프로젝트 루트 경로 추가 (src 모듈 임포트용)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.planner import SmishingPlanner
from src.generator import SmishingGenerator
from src.intent_analyzer import IntentAnalyzer
from src.detector import SmishingDetector
from src.trainer import SmishingTrainer
from src.utils import load_jsonl
from src.report_generator import SecurityReportGenerator
from database_manager import DBManager

# --- 유효성 검사 함수 ---
def validate_attack_message(message):
    refusal_patterns = [
        "수행할 수 없습니다", "도와드릴 수 없습니다", "죄송하지만", 
        "알 수 없는 오류", "부적절한 요청", "정책에 따라"
    ]
    if any(pattern in message for pattern in refusal_patterns):
        return False, "AI Safety Refusal (LLM 거절)"
    if len(message.replace(" ", "")) < 10:
        return False, "Too Short (정보량 부족)"
    return True, "Valid"

# --- 페이지 설정 ---
st.set_page_config(page_title="Adversarial Smishing Defense AI", layout="wide")


# 타이틀 섹션 (CSS 스타일링)
st.markdown("""
    <style>
    .main-title {
        font-family: "Arial Black", sans-serif;
        font-size: 60px;
        font-weight: 900;
        letter-spacing: -2px;
        background: linear-gradient(90deg, #00C6FF 0%, #343cc3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        padding-top: 10px;
        text-align: center; 
    }
    .sub-title {
        font-size: 20px;
        color: #555555;
        font-weight: 600;
        text-align: center; 
        margin-top: -10px;
        margin-bottom: 20px;
    }
    </style>
    <div class="main-title">Smishing Forecast</div>
    <div class="sub-title"> 자가 진화형 지능형 스미싱 방어 시스템</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center; color: #666; margin-bottom: 30px;'>
    최신 뉴스를 기반으로 공격 시나리오를 예측하고, 의도를 분석하여 방어력을 스스로 강화하는 AI 데모입니다.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- 세션 상태 초기화 ---
if 'initialized' not in st.session_state:
    with st.spinner("AI 에이전트 군단을 소집하고 있습니다..."):
        st.session_state.planner = SmishingPlanner()
        st.session_state.generator = SmishingGenerator()
        st.session_state.analyzer = IntentAnalyzer()
        # [변경] 학습 모델의 특성(Spam avg=0.72)을 고려하여 임계값을 0.5로 조정
        st.session_state.detector = SmishingDetector(threshold=0.5)
        st.session_state.reporter = SecurityReportGenerator()
        
        # [DB 연동] 데이터베이스 매니저 초기화
        st.session_state.db = DBManager()
        
        st.session_state.initialized = True
    
    # [수정] 코드가 변경되었을 때 최신 로직을 반영하기 위해 Trainer는 매번 새로 생성
    st.session_state.trainer = SmishingTrainer(st.session_state.detector)
    
    st.success("시스템 준비 완료!")

# --- 사이드바: 데이터 로드 ---
from email.utils import parsedate_to_datetime

# ... (imports)

# --- 사이드바: 데이터 로드 ---
st.sidebar.header("📂 Data Source")
data_path = "data/smishing_context_data.jsonl"
news_data = load_jsonl(data_path)

if news_data:
    # 날짜 기준 내림차순 정렬 (최신 기사가 상단에 오도록)
    try:
        news_data.sort(key=lambda x: parsedate_to_datetime(x['context']['source_date']), reverse=True)
    except Exception as e:
        st.sidebar.warning(f"날짜 정렬 중 오류가 발생했습니다: {e}")

    # [DB Sync] 로드된 뉴스 데이터를 DB에 저장 (중복 자동 무시)
    if 'db' in st.session_state:
        for news in news_data:
            st.session_state.db.insert_news(news)

    st.sidebar.success(f"{len(news_data)}개의 뉴스 데이터를 로드했습니다.")
    selected_news = st.sidebar.selectbox("분석할 뉴스를 선택하세요 (최신순)", news_data, 
                                        format_func=lambda x: f"[{x['context']['category']}] {x['context']['news_title']}")
else:
    st.sidebar.error("데이터 파일을 찾을 수 없습니다.")
    st.stop()

# --- 메인 화면 레이아웃 ---
# --- 메인 화면 레이아웃 ---
col1, col2 = st.columns(2)

# --- LEFT: 공격 시뮬레이션 (Red Team) ---
with col1:
    st.header("🔴 Attack Simulation (Red Team)")
    st.info(f"**선택된 뉴스**: {selected_news['context']['news_title']}")
    if st.button("🚀 공격 시나리오 기획 (3종)", use_container_width=True):
        with st.status("사회공학적 심리 분석 및 전략 수립 중...", expanded=True) as status:
            # [수정] 중복 방지를 위해 히스토리 전달
            history = st.session_state.get('generated_history', [])
            
            # 1. 3가지 시나리오 기획
            strategies = st.session_state.planner.plan_multiple_scenarios(
                selected_news, 
                count=3,
                used_patterns=history
            )
            
            if not strategies:
                status.update(label="시나리오 기획 실패", state="error", expanded=True)
                st.error("시나리오를 생성할 수 없습니다.")
                st.stop()
            
            # 성공 시 히스토리 업데이트
            for scn in strategies:
                summary = f"{scn['strategy_name']} (Logic: {scn['logic'][:20]}...)"
                history.append(summary)
            st.session_state['generated_history'] = history[-15:] # 최근 15개 기억

            st.session_state.strategies = strategies
            st.session_state.generated = False # 새로운 기획이므로 생성 상태 초기화
            status.update(label="3가지 전략 수립 완료!", state="complete", expanded=False)

    # 2. 시나리오 선택 및 생성 (기획된 전략이 있을 경우 표시)
    if 'strategies' in st.session_state and st.session_state.strategies:
        st.divider()
        st.subheader("🕵️‍♀️ 전략 선택")
        
        # 전략 표시 및 선택를 위한 라디오 버튼 (가독성을 위해 포맷팅)
        strategy_options = {
            f"{s['id']} : {s['strategy_name']}": i 
            for i, s in enumerate(st.session_state.strategies)
        }
        
        selected_option = st.radio(
            "공격을 수행할 시나리오를 선택하세요:",
            list(strategy_options.keys())
        )
        
        selected_idx = strategy_options[selected_option]
        selected_strategy = st.session_state.strategies[selected_idx]
        
        # 선택된 전략 상세 정보 보여주기
        with st.expander("📌 전략 상세 분석 (클릭하여 펼치기)", expanded=True):
            st.write(f"**사칭:** {selected_strategy['impersonation']}")
            st.write(f"**심리 기제:** {selected_strategy['trigger']}")
            st.write(f"**논리:** {selected_strategy['logic']}")

        # 3. 실제 공격 문구 생성 버튼
        if st.button("⚡ 이 전략으로 공격 문자 생성", type="primary", use_container_width=True):
            with st.spinner("AI가 실제 공격 문구를 생성하고 있습니다..."):
                attack_msg = st.session_state.generator.generate_attack_message(selected_strategy)
                
                # 생성 결과 검증
                is_valid, reason = validate_attack_message(attack_msg)
                
                if is_valid:
                    st.session_state.current_attack = {"strategy": selected_strategy, "message": attack_msg, "is_valid": True}
                    st.session_state.current_news = selected_news
                    st.session_state.generated = True
                    
                    # [DB] 생성된 시나리오(Intent) 저장
                    if 'db' in st.session_state:
                        st.session_state.db.upsert_intent({
                            "id": selected_strategy.get("id"),
                            "intent_name": selected_strategy.get("strategy_name"),
                            "description": selected_strategy.get("logic"),
                            "category": selected_strategy.get("trigger"),
                            "metadata": selected_strategy
                        })
                else:
                    st.session_state.current_attack = {"strategy": selected_strategy, "message": attack_msg, "is_valid": False, "reason": reason}

    if 'current_attack' in st.session_state and st.session_state.get('generated', False):
        attack = st.session_state.current_attack
        st.divider()
        if attack['is_valid']:
            st.success(f"**[전략] {attack['strategy']['strategy_name']}**")
            
            # [기능 개선] 모든 전략에 대해 상세 로드맵/논리 표시
            st.info("💀 **Attack Roadmap / Logic (공격 설계도)**")
            
            # [기능 개선] 구조화된 로드맵 필드 우선 사용
            roadmap_text = attack['strategy'].get('roadmap', attack['strategy'].get('logic', ''))
            strategy_name = attack['strategy']['strategy_name']
            
            # 다단계 시나리오일 경우 특별 경고 추가
            if "다단계" in strategy_name or "Multi-Stage" in strategy_name or "단계" in roadmap_text:
                st.caption("⚠️ **[Multi-Stage Detected]** 이 문자는 거대한 사기 플롯의 **'1단계 미끼(Bait)'**입니다.")
            
            # [시각화 개선] 화살표(->) 기준으로 단계 분리하여 표시
            if "->" in roadmap_text:
                steps = roadmap_text.split("->")
                for i, step in enumerate(steps):
                    st.markdown(f"**Step {i+1}:** {step.strip()}")
            else:
                st.info(roadmap_text) # 일반 텍스트면 그냥 박스로 표시

            st.chat_message("user", avatar="😈").write(f"**생성된 적대적 문구:**\n\n> {attack['message']}")
        else:
            st.error(f"⚠️ 생성 실패: {attack['reason']}")
            st.warning("안전 가이드라인 위반 등으로 생성이 거부되었습니다.")
            st.warning("LLM의 안전 가이드라인에 의해 공격 문구 생성이 거부되었습니다. 다른 뉴스나 시나리오로 재시도하세요.")

# --- RIGHT: 방어 및 분석 (Blue Team) ---
with col2:
    st.header("🔵 Intelligent Defense (Blue Team)")
    
    # 유효한 공격일 때만 분석 진행
    if 'current_attack' in st.session_state and st.session_state.current_attack['is_valid']:
        attack_msg = st.session_state.current_attack['message']
        
        # 1. Intent Analyzer
        st.subheader("🔍 의도 분석 (Intent Analysis)")
        with st.spinner("공격자의 의도를 파고드는 중..."):
            if 'last_analysis_msg' not in st.session_state or st.session_state.last_analysis_msg != attack_msg:
                st.session_state.intent_res = st.session_state.analyzer.analyze_intent(attack_msg)
                st.session_state.last_analysis_msg = attack_msg
            
            intent_res = st.session_state.intent_res
        
        i_col1, i_col2 = st.columns(2)
        with i_col1:
            st.metric("위협 레벨", intent_res.get('threat_level', 'Unknown'))
        with i_col2:
            st.metric("위험 점수", f"{intent_res.get('severity_score', 0)} / 5")
        
        st.write(f"**수법 분류:** {intent_res['intent_name']}")
        st.caption(f"**법적 위반 소지:** {', '.join(intent_res.get('legal_risks', []))}")
        
        st.divider()

        # 2. Detector & Evolution
        st.subheader("🛡️ 실시간 탐지 (Detection)")
        
        # [수정] 동적 업데이트를 위해 빈 컨테이너(placeholder) 생성
        detection_container = st.empty()
        
        def render_detection_ui(result):
            with detection_container.container():
                status_color = "red" if not result['is_smishing'] else "green"
                st.markdown(f"**판정 결과:** :{status_color}[{'스미싱(차단)' if result['is_smishing'] else '정상(통과)'}]")
                
                prob = result['smishing_score']
                st.metric(
                    label="AI 스미싱 탐지 확률", 
                    value=f"{prob*100:.2f}%", 
                    delta=f"{'⚠️ 위험' if prob > 0.5 else '✅ 안전'}",
                    delta_color="inverse"
                )
                st.progress(prob, text=f"Model Confidence: {prob:.4f}")

        # 초기 상태 렌더링
        INIT_TEMP = 2.5
        res_v1 = st.session_state.detector.predict(attack_msg)
        render_detection_ui(res_v1)
        
        # [DB] 1차 공격 시도 및 탐지 결과 저장
        if 'db' in st.session_state:
            st.session_state.db.insert_log({
                "scenario_name": st.session_state.current_attack['strategy']['strategy_name'],
                "generated_msg": attack_msg,
                "score": res_v1['smishing_score'],
                "model_used": "RoBERTa-Base (Initial)"
            })

        EVOLUTION_THRESHOLD = 0.95
        if res_v1['smishing_score'] < EVOLUTION_THRESHOLD:
            st.error(f"🚨 방어 보강 필요 (신뢰도 부족)")
            if st.button("⚙️ 자가 진화 (적대적 학습) 시작"):
                with st.spinner("가중치 업데이트 중..."):
                    train_data = [{"generated_message": attack_msg, "intent_analysis": intent_res}]
                    temp_path = "data/temp_app_train.json"
                    with open(temp_path, "w", encoding="utf-8") as f:
                        json.dump(train_data, f, indent=4, ensure_ascii=False)
                    st.session_state.trainer.train_on_vulnerabilities(temp_path)
                    os.remove(temp_path)
                
                res_v2 = st.session_state.detector.predict(attack_msg)
                
                # [핵심] 진화 완료 후 UI 즉시 갱신
                render_detection_ui(res_v2) 
                
                # [DB] 진화 후 결과 추가 저장
                if 'db' in st.session_state:
                    st.session_state.db.insert_log({
                        "scenario_name": st.session_state.current_attack['strategy']['strategy_name'],
                        "generated_msg": attack_msg,
                        "score": res_v2['smishing_score'],
                        "model_used": "RoBERTa-Base (Evolved)"
                    })
                
                st.success(f"🛡️ 진화 완료! 확률 인지력이 `{res_v1['smishing_score']:.4f}` → `{res_v2['smishing_score']:.4f}`로 향상되었습니다.")
                st.balloons() # 시각적 효과 추가

        st.divider()

        # 3. Security Report Generation
        st.header("📑 보안 리포트 발간")
        if st.button("📝 리포트 생성 하기", type="primary", use_container_width=True):
            with st.spinner("보고서 분석 및 PDF 생성 중..."):
                # 1. 텍스트 내용 생성
                text_content = st.session_state.reporter.generate_report_content(
                    st.session_state.current_news,
                    st.session_state.current_attack,
                    st.session_state.intent_res
                )
                # 2. PDF 변환
                pdf_bytes = st.session_state.reporter.create_pdf_report(text_content)
                st.session_state.report_pdf = pdf_bytes
                # 미리보기용 텍스트 저장
                st.session_state.report_preview = text_content
                
                # [DB] 생성된 리포트 저장
                if 'db' in st.session_state:
                    st.session_state.db.insert_report({
                        "scenario_name": st.session_state.current_attack['strategy']['strategy_name'],
                        "news_title": st.session_state.current_news['context']['news_title'],
                        "report_text": text_content,
                        "pdf_data": pdf_bytes
                    })

        if 'report_pdf' in st.session_state:
            with st.expander("📄 리포트 내용 미리보기", expanded=True):
                st.markdown(st.session_state.report_preview)
            
            st.download_button(
                label="📥 리포트 다운로드 (PDF 문서)",
                data=st.session_state.report_pdf,
                file_name=f"security_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    elif 'current_attack' in st.session_state:
        st.info("유효하지 않은 공격 데이터입니다. 분석을 수행하지 않습니다.")
    else:
        st.info("왼쪽에서 공격 시나리오를 생성해주세요.")

# --- 하단 로그 ---
st.divider()
with st.expander("📊 시스템 인지 수법 도감 (Scenario Bank)"):
    st.table(st.session_state.analyzer.scenario_bank)