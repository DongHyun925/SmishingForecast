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
    /* 사이드바 너비 확장 */
    section[data-testid="stSidebar"] {
        width: 420px !important;
    }
    section[data-testid="stSidebar"] > div {
        width: 420px !important;
    }
    
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

    /* Badge system */
    .badge-container {
        display: flex;
        gap: 10px;
        margin-bottom: 15px;
        align-items: center;
    }
    .pill-badge {
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 13px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        border: 1px solid transparent;
    }
    .badge-standard {
        background-color: #f1f5f9;
        color: #475569;
        border-color: #e2e8f0;
    }
    .badge-expert {
        background-color: #f0fdf4;
        color: #166534;
        border-color: #dcfce7;
    }
    .badge-refining {
        background-color: #f0f9ff;
        color: #075985;
        border-color: #e0f2fe;
    }
    .badge-analysis {
        background-color: #fff7ed;
        color: #9a3412;
        border-color: #ffedd5;
    }

    /* Sidebar Metric Styling */
    .sidebar-metric-container {
        background: white;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        margin-bottom: 10px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .sidebar-metric-label {
        font-size: 13px;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .sidebar-metric-value {
        font-size: 32px;
        font-weight: 800;
        margin: 0;
        line-height: 1;
    }
    .value-scenarios {
        color: #0080ff; /* Royal Blue */
    }
    .value-logs {
        color: #10b981; /* Emerald Green */
    }
    .sidebar-metric-unit {
        font-size: 16px;
        font-weight: 600;
        color: #94a3b8;
        margin-left: 2px;
    }
    </style>
    <div class="main-title">Smishing Forecast</div>
    <div class="sub-title"> Institutional Security Monitoring & Adaptive Defense System </div>
""", unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center; color: #666; margin-bottom: 30px;'>
    실시간 뉴스 인텔리전스 기반의 스미싱 위협 모델링 및 자가 진화형 방어 체계입니다.
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
        
        # database_manager 임포트 및 초기화 (메인 브랜치에서 가져옴)
        from database_manager import DatabaseManager
        st.session_state.db = DatabaseManager()
        st.session_state.initialized = True
    
    # [수정] 코드가 변경되었을 때 최신 로직을 반영하기 위해 Trainer는 매번 새로 생성
    st.session_state.trainer = SmishingTrainer(st.session_state.detector)
    
    st.success("시스템 준비 완료!")

# --- 사이드바: 데이터 로드 ---
from email.utils import parsedate_to_datetime

# --- 사이드바: Global Security Monitor ---
st.sidebar.title("🌐 Global Security Monitor")

# [고도화] 최신 위협 동기화 기능
if st.sidebar.button("🔄 실시간 위협 정보 동기화 (Crawl)", use_container_width=True):
    with st.sidebar.status("Global Threat Intelligence Synchronizing...", expanded=False) as status:
        from src.crawler import run_crawling
        try:
            # fetch_full=False로 하여 속도 우선 (필요시 상세페이지에서 BS4 호출)
            new_count, total_count = run_crawling(fetch_full=False)
            status.update(label=f"Synchronization Complete ({total_count} Trends Collected)", state="complete", expanded=False)
            
            # [신규] 동기화 결과 피드백 및 시간 기록
            if new_count > 0:
                st.toast(f"✅ {new_count}개의 최신 트렌드 뉴스가 추가되었습니다!", icon="🚀")
            else:
                st.toast("이미 최신 상태입니다.", icon="✅")
            
            st.session_state.last_sync_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            st.rerun()
        except Exception as e:
            status.update(label=f"오류 발생: {e}", state="error")

# [신규] 최근 업데이트 시간 표시
if 'last_sync_time' in st.session_state:
    st.sidebar.caption(f"🕒 **마지막 동기화**: {st.session_state.last_sync_time}")

st.sidebar.divider()

st.sidebar.markdown("""
    <div style='margin-bottom: 15px; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px; text-align: center;'>
        <h3 style='margin: 0; color: #1e293b; font-size: 1.2rem; font-weight: 800;'>🖥️ Operation Monitoring</h3>
    </div>
""", unsafe_allow_html=True)

# DB 통계 가져오기
if 'db' in st.session_state:
    stats = st.session_state.db.get_stats()
    
    # 분석된 시나리오 카드
    st.sidebar.markdown(f"""
        <div class="sidebar-metric-container">
            <div class="sidebar-metric-label">분석된 시나리오</div>
            <div class="sidebar-metric-value value-scenarios">
                {stats['intents']}<span class="sidebar-metric-unit">건</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # 탐지 로그 카드
    st.sidebar.markdown(f"""
        <div class="sidebar-metric-container">
            <div class="sidebar-metric-label">탐지 로그</div>
            <div class="sidebar-metric-value value-logs">
                {stats['logs']}<span class="sidebar-metric-unit">건</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # [신규] 하위 섹션: Digital Vaccine Hub
    st.sidebar.subheader("🛡️ Digital Vaccine Hub")
    st.sidebar.caption("실시간 진화 모델 배포 현황")
    if os.path.exists("models/smishing_detector_model.pth"):
        st.sidebar.success("✅ 최신 백신(Weights) 적용 중")
        last_mod = os.path.getmtime("models/smishing_detector_model.pth")
        st.sidebar.caption(f"최근 업데이트: {datetime.fromtimestamp(last_mod).strftime('%Y-%m-%d %H:%M')}")
    else:
        st.sidebar.warning("⚠️ 기본 모델 사용 중")

    st.sidebar.divider()
    
    # [신규] 하위 섹션: Intelligence Source
    st.sidebar.subheader("📂 Intelligence Source")

# [개선] 데이터 파일 경로 절대 경로화 (Persistence 보장)
base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "data", "smishing_context_data.jsonl")
news_data = load_jsonl(data_path)

# [고도화] 전문 수집 데이터 캐시 (세션 유지용)
if 'full_text_cache' not in st.session_state:
    st.session_state.full_text_cache = {}

if news_data:
    # [수정] 날짜 파싱 및 최신순 정렬 강화
    def get_sort_key(x):
        try:
            date_str = x['context']['source_date']
            # 1. RFC 2822 (RSS) 형식 시도
            try:
                dt = parsedate_to_datetime(date_str)
                return dt.timestamp()
            except:
                pass
            
            # 2. ISO / Naver API 형식 시도
            try:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return dt.timestamp()
            except:
                pass
                
            return 0
        except Exception:
            return 0

    # 안정적인 정렬 (Timsort는 기존 순서 유지)
    news_data.sort(key=get_sort_key, reverse=True)

    # [DB Sync] 로드된 뉴스 데이터를 DB에 저장 (중복 자동 무시)
    if 'db' in st.session_state:
        for news in news_data:
            st.session_state.db.insert_news(news)

    st.sidebar.success(f"{len(news_data)}개의 위협 피드 확보")
    selected_news = st.sidebar.selectbox("기사 분석 및 위협 모델링 선택", news_data, 
                                        format_func=lambda x: f"[{x['context']['category']}] {x['context']['news_title']}")
else:
    st.sidebar.error("데이터 피드를 로드할 수 없습니다.")
    st.stop()

# --- 메인 화면 레이아웃 ---
col1, col2 = st.columns(2)

# --- LEFT: 위협 시뮬레이션 (Threat Simulation) ---
with col1:
    st.header("🔴 Threat Modeling (Red Team)")
    
    # 지능 분석 깊이 표시 (SOC 상태 배지) - "버튼 클릭 액션" 여부로 판단
    current_link = selected_news['context'].get('link', '')
    is_upgraded = current_link in st.session_state.full_text_cache
    
    # [신규] Expert 지원 가능성 체크 (호환성 배지)
    supported_domains = [
        "news.naver.com", "chosun.com", "joins.com", "joongang.co.kr",
        "newsis.com", "gukjenews.com", "mk.co.kr", "fnnews.com", 
        "biz.sbs.co.kr", "news.kbs.co.kr", "sedaily.com", "kukinews.com", "edaily.co.kr"
    ]
    is_highly_compatible = any(domain in current_link for domain in supported_domains)
    
    # 화면 표시 및 분석용 텍스트 결정 (캐시 우선)
    current_raw_text = st.session_state.full_text_cache.get(current_link) if is_upgraded else selected_news.get('raw_text', '')
    
    # [수정] 즉시 갱신을 위해 빈 컨테이너 활용
    depth_badge_placeholder = st.empty()
    
    def render_depth_badge(upgraded, refining=False):
        with depth_badge_placeholder.container():
            if refining:
                main_badge = '<div class="pill-badge badge-refining">📄 Intelligence Depth: Standard (Refining...)</div>'
            elif upgraded:
                main_badge = '<div class="pill-badge badge-expert">🎯 Intelligence Depth: Expert (Full-Text)</div>'
            else:
                main_badge = '<div class="pill-badge badge-standard">📄 Intelligence Depth: Standard (Snippet)</div>'
            
            # Deep Analysis Compatibility Badge
            if not upgraded and not refining:
                if is_highly_compatible:
                    side_badge = '<div class="pill-badge badge-analysis">✅ Deep Analysis: Highly Compatible</div>'
                else:
                    side_badge = '<div class="pill-badge badge-analysis">ℹ️ Deep Analysis: Heuristic Fallback</div>'
            else:
                side_badge = ''

            st.markdown(f"""
                <div class="badge-container">
                    {main_badge}
                    {side_badge}
                </div>
            """, unsafe_allow_html=True)
    
    render_depth_badge(is_upgraded)

    st.info(f"**Target Intel**: {selected_news['context']['news_title']}")
    
    if st.button("🔍 사회공학적 공격 시나리오 모델링 (3종)", use_container_width=True):
        with st.status("Intelligence Upgrading & Strategy Modeling...", expanded=True) as status:
            # [고도화] 하이브리드: 분석 시점에 부족한 정보 보완 (On-Demand)
            current_context = current_raw_text # 상단에서 결정된 텍스트 사용
            if not is_upgraded:
                # [개선] 크롤링 시작 시 '정제 중' 상태 표시
                render_depth_badge(False, refining=True)
                status.update(label="심층 분석을 위한 기사 전문 수집 중 (BS4)...")
                try:
                    from src.crawler import fetch_full_content
                    target_url = selected_news['context'].get('link')
                    if target_url:
                        full_text = fetch_full_content(target_url)
                        if full_text:
                            current_context = full_text
                            # [핵심] 수집 '완료' 후에만 Expert로 격상
                            st.session_state.full_text_cache[target_url] = full_text
                            status.update(label="지능 업그레이드 완료 (심층 분석 데이터 확보)")
                            render_depth_badge(True) # 여기서 Expert로 전환
                        else:
                            # 실패(결과 없음) 시 다시 원래 상태로
                            render_depth_badge(False)
                            status.update(label="⚠️ 전문 수집 실패 (사이트 차단 등)", state="error")
                            st.warning("일부 뉴스 사이트의 보안 정책으로 전문을 가져오는 데 실패했습니다. 시스템이 자동으로 '요약본(Snippet)' 인텔리전스를 사용하여 분석을 계속합니다.")
                    else:
                        # 링크 자체가 없을 경우
                        render_depth_badge(False)
                        st.warning("유효한 기사 링크가 없어 요약본으로 분석을 진행합니다.")
                except Exception as e:
                    # 에러 발생 시 원래 상태로 복구
                    render_depth_badge(False)
                    st.error(f"심층 분석 중 오류 발생: {e}")
                    pass

            status.update(label="사회공학적 심리 분석 및 전략 수립 중...")
            # [수정] 중복 방지를 위해 히스토리 전달
            history = st.session_state.get('generated_history', [])
            
            # [고도화] 업그레이드된 full context가 있으면 그것을 사용
            upgraded_item = selected_news.copy()
            upgraded_item['raw_text'] = current_context
            
            strategies = st.session_state.planner.plan_multiple_scenarios(
                processed_item=upgraded_item,
                used_patterns=history
            )
            
            if not strategies:
                status.update(label="시나리오 기획 실패", state="error", expanded=True)
                st.error("시나리오를 생성할 수 없습니다.")
                st.stop()
            
            st.session_state.strategies = strategies
            st.session_state.generated = False # 새로운 기획이므로 생성 상태 초기화
            status.update(label="3가지 전략 수립 완료!", state="complete", expanded=False)
            
            # [핵심] 모든 처리가 끝난 후 전체 앱 재실행을 유도하여 상단 배지 상태 동기화
            st.rerun()

    # 2. 시나리오 선택 및 생성 (기획된 전략이 있을 경우 표시)
    if 'strategies' in st.session_state and st.session_state.strategies:
        st.divider()
        st.subheader("기획된 전략 선택")
        
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

            st.chat_message("user").write(f"**생성된 적대적 문구:**\n\n> {attack['message']}")
        else:
            st.error(f"⚠️ 생성 실패: {attack['reason']}")
            st.warning("안전 가이드라인 위반 등으로 생성이 거부되었습니다.")
            st.warning("LLM의 안전 가이드라인에 의해 공격 문구 생성이 거부되었습니다. 다른 뉴스나 시나리오로 재시도하세요.")

# --- RIGHT: 위협 분석 및 관제 (Intelligence & Defense) ---
with col2:
    st.header("🔵 Adaptive Defense (Blue Team)")
    
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
        res_v1 = st.session_state.detector.predict(attack_msg)
        render_detection_ui(res_v1)

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
                
                st.success(f"🛡️ 진화 완료! 확률 인지력이 `{res_v1['smishing_score']:.4f}` → `{res_v2['smishing_score']:.4f}`로 향상되었습니다.")

        st.divider()

        # 3. Security Report Generation
        st.header("🏛️ 포괄적 위협 인텔리전스 발간")
        if st.button("📋 보안 분석 리포트(SOC Standard) 생성", type="primary", use_container_width=True):
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
    # [수정] 최신 수법이 가장 위에 오도록 정렬 순서 변경
    st.table(reversed(st.session_state.analyzer.scenario_bank))