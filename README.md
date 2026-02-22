
# 🛡️ Hackathon_Smishing
> **KcBERT 기반의 자가 진화형 지능형 스미싱 방어 시스템** > 최신 사회적 맥락 분석을 통한 적대적 공격 시뮬레이션 및 신뢰도 기반 자가 학습 아키텍처

<<<<<<< Updated upstream
=======
### *실시간 뉴스 인텔리전스 기반 스미싱 위협 모델링 및 자가 진화형 방어 AI*
>>>>>>> Stashed changes

## ⚙️ 시작하기 전 (Environment Setup)

<<<<<<< Updated upstream
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
=======
</div>
>>>>>>> Stashed changes

---

## 🚀 설치 및 실행 방법

<<<<<<< Updated upstream
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
=======
| 이름 | 이메일 |
|------|--------|
| 조은경 | gracech0961@gmail.com |
| 안성민 | tjdals2299@gmail.com |
| 황동현 | myjewel29@naver.com |
| 황선우 | eddiehwang125@gmail.com |

---

## 📖 프로젝트 소개

**Smishing Forecast**는 공공 안전을 위한 **자가 진화형 AI 보안 인프라**입니다.

- 사회적 이슈를 실시간으로 수집하여 스미싱 공격자가 악용할 수 있는 위협 시나리오를 **선제적으로 예측 (Red Team)**
- 생성된 공격에 대해 즉각적으로 방어 가능한 **AI 가중치(Digital Vaccine)를 실시간 생성 및 배포 (Blue Team)**
- SOC, 금융기관, 통신사의 사기 대응 전문성을 고도화하여 **디지털 취약계층을 위한 기술적 안전망** 구축

---

## 🏛️ 사회적 가치 (Social Impact)

- **디지털 백신 배포**: 진화된 방어 모델을 오픈소스로 공유하여 국가 전체의 사이버 면역력 향상
- **피해 방지 표준**: SOC 표준 리포트를 통해 민·관 협력 대응 체계 강화

---

## ✨ 주요 기능

### 🌐 Global Security Monitor (실시간 뉴스 인텔리전스)
- **트렌드 기반 수집**: 구글 뉴스 RSS `주요 뉴스`, `경제`, `사회` 섹션에서 현재 가장 화제인 기사를 **키워드 없이** 자동 수집
- **보조 수집**: 네이버 뉴스 API를 통한 사회적 맥락 키워드 기반 보완 수집
- **Incremental Merge**: 링크 및 제목 기반 중복 제거 후 신규 항목만 증분 저장
- **동기화 피드백**: 사이드바의 "마지막 동기화" 시간과 신규 추가 건수 Toast 알림

### 🔴 Red Team (공격 시뮬레이션)
- **뉴스 기반 시나리오 기획**: LLM 기반 Planner가 사회적 맥락을 분석하여 3종의 공격 전략 도출
- **공격 문자 생성**: GPT-4o 기반 자연스럽고 교묘한 스미싱 메시지 자동 생성
- **스텔스 모드**: URL, 전화번호 등 탐지 가능 요소를 제거한 은밀한 시나리오 지원

### 🔵 Blue Team (방어 및 분석)
- **RoBERTa 기반 실시간 탐지**: `klue/roberta-base` Fine-tuned 모델 활용
- **지능형 위협 프로파일링**: 공격 의도, 위협 등급, 법적 위반 소지 분석 (SOC Standard)
- **자가 진화 (Stability Learning)**: 파괴적 망각을 최소화한 Replay Buffer 학습으로 실시간 방어력 강화
- **PDF 보안 리포트**: SOC 분석가용 IoC(침해 지표)를 포함한 보고서 자동 생성

### �️ Operation Monitoring (운영 모니터링)
- **Digital Vaccine Hub**: 현재 배포된 모델 가중치 최신화 상태 및 업데이트 일시 표시
- **Intelligence Source**: 확보된 위협 피드 건수 및 기사 선택 인터페이스
- **사이드바 메트릭**: 분석된 시나리오 수, 탐지 로그 수를 고대비 카드 UI로 표시

---

## 🚀 설치 및 실행

### 1. 저장소 클론
```bash
git clone https://github.com/gracechoek/Hackathon_Smishing.git
cd Hackathon_Smishing
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
`.env.example`을 `.env`로 복사하고 API 키를 입력하세요:
```bash
cp .env.example .env
```

`.env` 파일 내용:
```
OPENAI_API_KEY=your_actual_openai_api_key

# Naver Search API (For News Crawling)
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret

# Supabase (Optional, for Cloud DB mode)
# SUPABASE_URL=your_supabase_url
# SUPABASE_KEY=your_supabase_key
```

### 4. 사전 학습된 모델 (선택 사항)
```bash
# Hugging Face에서 Fine-tuned 모델 다운로드
# https://huggingface.co/donghyun95/smishing-detection-roberta-base
```
미설치 시 `klue/roberta-base` 기본 모델로 자동 시작합니다.

### 5. 애플리케이션 실행
```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501`로 접속하세요.

---

## 📁 프로젝트 구조

```
Hackathon_Smishing/
├── app.py                      # Streamlit 메인 애플리케이션 (대시보드 UI)
├── database_manager.py         # 데이터베이스 관리 (SQLite / Supabase 자동 전환)
├── requirements.txt            # Python 의존성
├── .env.example               # 환경 변수 템플릿
│
├── src/                       # 핵심 모듈
│   ├── crawler.py            # 뉴스 크롤러 (Google RSS Trending + Naver API)
│   ├── planner.py            # 공격 시나리오 기획 (Red Team, LLM 기반)
│   ├── generator.py          # 공격 문구 생성 (GPT-4o)
│   ├── intent_analyzer.py    # 의도 분석 및 위협 프로파일링 (Blue Team)
│   ├── detector.py           # 스미싱 탐지 모델 (RoBERTa Fine-tuned)
│   ├── trainer.py            # 자가 진화 학습 (Replay Buffer)
│   ├── report_generator.py   # 보안 리포트 생성 (PDF/Markdown)
│   └── utils.py              # 유틸리티 함수 (JSONL 로드 등)
│
├── data/                      # 데이터 저장소 (절대 경로 보장)
│   ├── smishing_context_data.jsonl  # 수집된 뉴스 인텔리전스 데이터베이스
│   ├── scam_news_api_raw.json       # 최신 크롤링 원본 데이터
│   └── scenario_bank.json           # 생성된 시나리오 뱅크
│
├── models/                    # 학습된 모델 가중치
│   └── smishing_detector_model.pth  # Fine-tuned RoBERTa 가중치
│
└── scripts/                   # 유틸리티 스크립트
    └── deploy_model.py       # Hugging Face Hub 배포 스크립트
```

---

## 🎯 사용 방법

### 1. 뉴스 인텔리전스 동기화
- 사이드바의 **[🔄 실시간 위협 정보 동기화 (Crawl)]** 버튼 클릭
- 구글 뉴스 및 네이버에서 트렌딩 기사를 자동 수집
- 동기화 완료 후 신규 추가 건수가 Toast로 표시됨

### 2. 공격 시나리오 생성 (Red Team)
1. 사이드바의 **Intelligence Source** 드롭다운에서 분석할 기사 선택
2. **[공격 시나리오 기획 (3종)]** 버튼 클릭
3. 3가지 전략 중 하나를 선택
4. **[이 전략으로 공격 문자 생성]** 버튼 클릭

### 3. 방어 분석 (Blue Team)
- 오른쪽 패널에서 자동으로 **의도 분석** 및 **실시간 스미싱 탐지** 수행
- 탐지 점수가 낮을 경우 **[자가 진화 시작]** 버튼(Adversarial Training)으로 즉시 재학습

### 4. 보안 리포트 생성
- **[리포트 생성 하기]** 버튼 클릭
- Markdown 미리보기 또는 PDF 다운로드

---

## 🧠 핵심 기술

### 아키텍처

```
[구글 뉴스 RSS Trending]  ──┐
                             ├──► Incremental Merge ──► smishing_context_data.jsonl
[네이버 뉴스 API 보조 수집] ──┘
         │
         ▼
[LLM Planner] ──► 3종 공격 전략 수립
         │
         ▼
[GPT-4o Generator] ──► 스미싱 문자 생성
         │
         ▼
[RoBERTa Detector] ──► 실시간 탐지 (score)
         │
    (score 낮을 때)
         ▼
[Adversarial Trainer] ──► Replay Buffer 학습 ──► 🛡️ Digital Vaccine 배포
```

### AI 모델
- **텍스트 생성**: OpenAI GPT-4o (시나리오 기획, 공격 문자, 의도 분석)
- **분류 모델**: `klue/roberta-base` (한국어 RoBERTa, 스미싱 탐지)
- **학습 방식**: Adversarial Training + Replay Buffer

### 데이터베이스
- **로컬**: SQLite3 (`smishing_db.db`) — 기본 모드
- **클라우드**: Supabase — 중앙 관제 모드 (선택 사항)

### 뉴스 크롤링
- **Primary**: Google News RSS (주요뉴스 / 경제 / 사회 섹션)
- **Secondary**: Naver News API (사회적 맥락 키워드 검색)
- **Full-Text**: BeautifulSoup4 (on-demand 기사 원문 수집)

---

## � 모델 성능

| 지표 | 초기 (Baseline) | 자가 진화 후 |
|------|----------------|-------------|
| Precision | 0.50 | **1.00** |
| Recall | 1.00 | **1.00** |
| F1-Score | 0.67 | **1.00** |

> ⚠️ *위 성능은 GPT-4o로 생성된 합성 데이터셋(100건) 기준입니다. 실제 스미싱 문자(Real-world)에 대해서는 Synthetic Distribution으로 인한 성능 차이가 발생할 수 있습니다.*

---

## 🚀 Hugging Face Hub 배포

```bash
# Hugging Face CLI 로그인
huggingface-cli login

# 모델 업로드
python scripts/deploy_model.py
```

배포된 모델: [donghyun95/smishing-detection-roberta-base](https://huggingface.co/donghyun95/smishing-detection-roberta-base)

---

## ⚠️ 주의사항

1. **윤리적 사용**: 이 시스템은 보안 연구 및 교육 목적으로만 사용하세요.
2. **API 비용**: OpenAI API 사용량에 따라 비용이 발생할 수 있습니다.
3. **데이터 보안**: `.env` 파일은 절대 공개 저장소에 업로드하지 마세요.

---

## 📝 라이선스

MIT License

---

## 🙏 감사의 말

- **KLUE Team**: 한국어 RoBERTa 모델 제공
- **Hugging Face**: 모델 호스팅 및 인프라 지원
- **OpenAI**: GPT-4o API 제공
- **Google / Naver**: 뉴스 RSS 및 검색 API 제공
>>>>>>> Stashed changes

---
## 📂 데이터 저장소 구조 (Data Store)

* `scam_news_api_raw.json`: 수집된 뉴스 원천 데이터.
* `smishing_context_data.jsonl`: AI 에이전트용으로 정제된 뉴스 맥락 지식 베이스.
* `final_dataset.json`: 생성 문구, 분석 결과, 탐지 확률이 포함된 통합 리포트.
* `vulnerabilities.json`: 모델 강화를 위해 선별된 고품질 취약점 샘플 로그.
