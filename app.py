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

# --- 유효성 검사 함수 추가 ---
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

st.title("🛡️ 자가 진화형 지능형 스미싱 방어 시스템")
st.markdown("최신 뉴스를 기반으로 공격 시나리오를 예측하고, 의도를 분석하여 방어력을 스스로 강화하는 AI 데모입니다.")

# --- 세션 상태 초기화 ---
if 'initialized' not in st.session_state:
    with st.spinner("AI 에이전트 군단을 소집하고 있습니다..."):
        st.session_state.planner = SmishingPlanner()
        st.session_state.generator = SmishingGenerator()
        st.session_state.analyzer = IntentAnalyzer()
        st.session_state.detector = SmishingDetector(threshold=0.8)
        st.session_state.trainer = SmishingTrainer(st.session_state.detector)
        st.session_state.initialized = True
    st.success("시스템 준비 완료!")

# --- 사이드바: 데이터 로드 ---
st.sidebar.header("📂 Data Source")
data_path = "data/smishing_context_data.jsonl"
news_data = load_jsonl(data_path)

if news_data:
    st.sidebar.success(f"{len(news_data)}개의 뉴스 데이터를 로드했습니다.")
    selected_news = st.sidebar.selectbox("분석할 뉴스를 선택하세요", news_data, 
                                        format_func=lambda x: x['context']['news_title'])
else:
    st.sidebar.error("데이터 파일을 찾을 수 없습니다.")
    st.stop()

# --- 메인 화면 레이아웃 ---
col1, col2 = st.columns(2)

# --- LEFT: 공격 시뮬레이션 (Red Team) ---
with col1:
    st.header("😈 Attack Simulation (Red Team)")
    
    if st.button("🚀 공격 시나리오 기획 및 생성"):
        with st.status("공격 전략 수립 및 문구 생성 중...", expanded=True) as status:
            strategies = st.session_state.planner.plan_multiple_scenarios(selected_news, count=1)
            strategy = strategies[0]
            st.write(f"기획된 전략: **{strategy['strategy_name']}**")
            
            attack_msg = st.session_state.generator.generate_attack_message(strategy)
            
            # 생성 결과 검증
            is_valid, reason = validate_attack_message(attack_msg)
            
            if is_valid:
                st.session_state.current_attack = {"strategy": strategy, "message": attack_msg, "is_valid": True}
                status.update(label="공격 준비 완료!", state="complete", expanded=False)
            else:
                st.session_state.current_attack = {"strategy": strategy, "message": attack_msg, "is_valid": False, "reason": reason}
                status.update(label="공격 생성 실패", state="error", expanded=True)

    if 'current_attack' in st.session_state:
        attack = st.session_state.current_attack
        if attack['is_valid']:
            st.info(f"**[선택된 전략]** {attack['strategy']['strategy_name']}\n\n- 사칭: {attack['strategy']['impersonation']}\n- 논리: {attack['strategy']['logic']}")
            st.chat_message("user", avatar="😈").write(f"**생성된 적대적 문구:**\n\n> {attack['message']}")
        else:
            st.error(f"⚠️ **생성 실패 알림**\n\n사유: {attack['reason']}\n\n내용: {attack['message']}")
            st.warning("LLM의 안전 가이드라인에 의해 공격 문구 생성이 거부되었습니다. 다른 뉴스나 시나리오로 재시도하세요.")

# --- RIGHT: 방어 및 분석 (Blue Team) ---
with col2:
    st.header("🛡️ Intelligent Defense (Blue Team)")
    
    # 유효한 공격일 때만 분석 진행
    if 'current_attack' in st.session_state and st.session_state.current_attack['is_valid']:
        attack_msg = st.session_state.current_attack['message']
        
        # 3. Intent Analyzer 작동
        st.subheader("🔍 의도 분석 및 위험도 평가")
        with st.spinner("공격자의 의도를 파고드는 중..."):
            intent_res = st.session_state.analyzer.analyze_intent(attack_msg)
        
        i_col1, i_col2 = st.columns(2)
        with i_col1:
            st.metric("위험 점수", f"{intent_res.get('severity_score', 1)} / 5")
        with i_col2:
            st.metric("위협 레벨", intent_res.get('threat_level', 'Unknown'))
        
        st.write(f"**수법 분류:** {intent_res['intent_name']}")
        st.caption(f"**법적 위반 소지:** {', '.join(intent_res.get('legal_risks', []))}")
        
        st.divider()

        # 4. Detector 작동 및 자가 진화
        st.subheader("🛡️ 실시간 탐지 및 자가 진화")
        res_v1 = st.session_state.detector.predict(attack_msg)
        
        # 판정 결과 시각화
        status_color = "red" if not res_v1['is_smishing'] else "green"
        st.markdown(f"**판정 결과:** :{status_color}[{'스미싱(차단)' if res_v1['is_smishing'] else '정상(통과)'}]")
        st.progress(res_v1['smishing_score'], text=f"스미싱 확률: {res_v1['smishing_score']:.4f}")

        # 진화 임계값 (Harding Threshold)
        EVOLUTION_THRESHOLD = 0.95

        if res_v1['smishing_score'] < EVOLUTION_THRESHOLD:
            st.error(f"🚨 방어 보강 필요 (신뢰도 {res_v1['smishing_score']:.4f} < {EVOLUTION_THRESHOLD})")
            
            if st.button("⚙️ 자가 진화 (적대적 학습) 시작"):
                with st.spinner("가중치 업데이트 중..."):
                    train_data = [{"generated_message": attack_msg, "intent_analysis": intent_res}]
                    temp_path = "data/temp_app_train.json"
                    with open(temp_path, "w", encoding="utf-8") as f:
                        json.dump(train_data, f, indent=4, ensure_ascii=False)
                    st.session_state.trainer.train_on_vulnerabilities(temp_path)
                    os.remove(temp_path)
                
                res_v2 = st.session_state.detector.predict(attack_msg)
                diff = res_v2['smishing_score'] - res_v1['smishing_score']
                
                st.balloons()
                st.success(f"🛡️ 진화 완료! 확률 인지력이 `{res_v1['smishing_score']:.4f}` → `{res_v2['smishing_score']:.4f}`로 향상되었습니다.")
        else:
            st.success(f"🛡️ 신뢰도 {res_v1['smishing_score']:.4f}로 완벽 방어 중입니다.")
    
    elif 'current_attack' in st.session_state:
        st.info("유효하지 않은 공격 데이터입니다. 분석을 수행하지 않습니다.")

# --- 하단 로그 ---
st.divider()
st.subheader("📊 Scenario Bank")
with st.expander("시스템 인지 수법 도감"):
    st.table(st.session_state.analyzer.scenario_bank)