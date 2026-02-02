
# 🛡️ Hackathon_Smishing
> **KcBERT 기반의 자가 진화형 지능형 스미싱 방어 시스템** > 최신 사회적 맥락 분석을 통한 적대적 공격 시뮬레이션 및 신뢰도 기반 자가 학습 아키텍처


## ⚙️ 시작하기 전 (Environment Setup)

### 1. 모델 파일 준비 (Pre-trained Weights)
본 프로젝트는 보안 및 효율성을 위해 대용량 모델 파일(`model.safetensors`)을 저장소에 포함하고 있지 않습니다. 실행 전 아래 가이드에 따라 모델을 배치하세요.
* **다운로드 링크:** [Notion 모델 다운로드](https://www.notion.so/MVP-2f2bf15f4f2680f5b964d51419383b0b?source=copy_link)
* **파일명:** `model.safetensors`
* **배치 경로:**
  ```text
  models/refined_kcbert/
  └── model.safetensors
  ```

### 2. API 환경 변수 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 아래의 인증 정보를 입력해야 합니다.

```env
# OpenAI API 설정 (Planner, Generator, Analyzer용)
OPENAI_API_KEY=your_openai_api_key_here

# Naver API 설정 (Crawler용)
NAVER_CLIENT_ID=your_naver_client_id_here
NAVER_CLIENT_SECRET=your_naver_client_secret_here

```

> **⚠️ 주의**: `.env` 파일은 절대 Git에 Push하지 마십시오. (본 저장소는 `.gitignore`로 보호됨)

---

## 🚀 설치 및 실행 방법

1. **Pipeline 통합 실행 (Main)**
데이터 수집부터 적대적 공격 생성, 자가 진화 학습까지의 전 과정을 자동 실행합니다.
```bash
python main.py

```

2. **데모 대시보드 실행 (Streamlit)**
인터랙티브한 시각화 화면에서 실시간 공격 분석 및 진화 과정을 시연합니다.
```bash
streamlit run app.py

```

---
## 📂 데이터 저장소 구조 (Data Store)

* `scam_news_api_raw.json`: 수집된 뉴스 원천 데이터.
* `smishing_context_data.jsonl`: AI 에이전트용으로 정제된 뉴스 맥락 지식 베이스.
* `final_dataset.json`: 생성 문구, 분석 결과, 탐지 확률이 포함된 통합 리포트.
* `vulnerabilities.json`: 모델 강화를 위해 선별된 고품질 취약점 샘플 로그.
