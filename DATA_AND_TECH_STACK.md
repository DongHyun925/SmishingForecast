# 🔮 Smishing Forecast - 데이터 및 기술 활용 정의서

## 📌 목차
1. [활용 데이터 종류](#1-활용-데이터-종류)
2. [데이터 처리 방식](#2-데이터-처리-방식)
3. [기술 스택 (Tech Stack)](#3-기술-스택-tech-stack)
4. [기술적 제약 및 해결 전략](#4-기술적-제약-및-해결-전략)

---

## 1. 활용 데이터 종류

### 1.1 외부 데이터 (External Data)
- **뉴스 기사 (News Articles)**: 사회적 이슈 및 잠재적 스미싱 트리거를 식별하기 위한 원천 데이터
  - 출처: Google News RSS (키워드: 'hiring', 'delivery', 'policy', 'loan' 등)
  - 속성: 제목, 본문 요약, 게시 날짜, 매체명

### 1.2 내부 생성 데이터 (Synthetic Data)
- **적대적 스미싱 시나리오 (Adversarial Smishing Scenarios)**
  - Red Team(GPT-4)이 뉴스 데이터를 기반으로 생성한 가상의 스미싱 문자
  - 속성: 시나리오 ID, 전략명(Intent), 생성된 메시지, 타겟 감정

### 1.3 학습용 데이터 (Training Data)
- **기존 스미싱 데이터셋**: KISA, 금융보안원 등에서 공개한 악성 문자 데이터 (베이스 모델 학습용)
- **자가 진화 데이터**: Blue Team이 탐지에 실패했으나 사후 분석으로 확인된 신종 스미싱 데이터 (파인튜닝용)

---

## 2. 데이터 처리 방식

### 2.1 데이터 수집 및 전처리 (ETL)
1. **Crawling**: `BeautifulSoup`을 사용하여 뉴스 RSS 피드에서 텍스트 추출
2. **Cleaning**: 광고 문구 제거, 특수문자 정제, 한국어 불용어 처리
3. **Structuring**: 비정형 텍스트를 JSON 형태로 구조화하여 `smishing_context_data.jsonl`에 저장

### 2.2 텍스트 분석 및 증강 (Analysis & Augmentation)
1. **Tokenization**: `KLUE-RoBERTa` 토크나이저를 사용하여 형태소 단위 분석
2. **Intent Classification**: 메시지의 잠재적 의도(금전 요구, 정보 탈취 등)를 다각도 분석
3. **Data Augmentation**: 동일한 의도의 메시지를 다양한 화행(Politeness, Urgency)으로 변형하여 학습 데이터 확장

### 2.3 벡터화 및 임베딩 (Vectorization)
- 텍스트 데이터를 768차원(RoBERTa-base 기준)의 고밀도 벡터로 변환하여 모델 입력값으로 사용

---

## 3. 기술 스택 (Tech Stack)

### 3.1 AI & Machine Learning
| 구분 | 기술/라이브러리 | 활용 목적 |
|------|-----------------|-----------|
| **LLM** | **OpenAI GPT-4** | 고도화된 스미싱 문구 생성, 시나리오 기획 |
| **Model** | **KLUE-RoBERTa** | 한국어 특화 스미싱 탐지 및 분류 |
| **Framework** | **PyTorch** | 딥러닝 모델 학습 및 추론 엔진 |
| **Library** | **Hugging Face Transformers** | 사전 학습 모델 로드 및 토크나이징 |

### 3.2 Application & Backend
| 구분 | 기술/라이브러리 | 활용 목적 |
|------|-----------------|-----------|
| **Language** | **Python 3.9+** | 전체 시스템 개발 언어 |
| **Web Framework** | **Streamlit** | 대시보드 UI 및 인터랙티브 시연 환경 구축 |
| **Database** | **SQLite / Supabase** | 경량 로컬 DB 및 클라우드 데이터 동기화 |
| **Environment** | **python-dotenv** | API 키 및 환경 변수 보안 관리 |

### 3.3 Utilities
- **ReportLab**: PDF 보안 리포트 생성
- **BeautifulSoup4**: 뉴스 데이터 크롤링
- **Scikit-learn**: 모델 성능 평가 지표(F1-score 등) 계산

---

## 4. 기술적 제약 및 해결 전략

### 4.1 실시간성(Real-time)과 정확도(Accuracy)의 트레이드오프
- **제약**: RoBERTa와 같은 트랜스포머 모델은 추론 속도가 상대적으로 느려 대용량 트래픽 처리에 병목이 발생할 수 있습니다.
- **해결 전략**:
  - **모델 경량화(Distillation)**: 성능 저하를 최소화하면서 모델 크기를 줄인 `DistilKoBERT` 등 도입 고려
  - **배치 처리(Batch Processing)**: 실시간성이 덜 중요한 대량 분석은 비동기 큐(Queue)로 처리
  - **캐싱(Caching)**: 동일한 문구에 대한 분석 결과는 Redis 등에 캐싱하여 중복 연산 방지

### 4.2 데이터 불균형 (Data Imbalance)
- **제약**: 정상 문자에 비해 스미싱 문자의 데이터 양이 절대적으로 부족하여, 모델이 정상 문자로 편향(Bias)될 수 있습니다.
- **해결 전략**:
  - **GenAI 기반 데이터 증강**: GPT-4를 활용하여 부족한 스미싱 데이터를 10~100배로 증강(Augmentation)
  - **Hard Negative Mining**: 모델이 헷갈려하는(탐지 실패한) 데이터를 집중적으로 수집하여 재학습

### 4.3 언어적 특성 및 문맥 파악의 어려움
- **제약**: "엄마 나 폰 고장났어"와 같은 문장은 단어 자체에는 악의성이 없어, 기존 키워드 필터링으로는 100% 탐지가 불가능합니다.
- **해결 전략**:
  - **Context-Aware Learning**: 단어 단위가 아닌 문장 전체의 '의도'를 파악하도록 학습
  - **메타데이터 활용**: 발신자 정보, 포함된 URL의 특징 등 비텍스트 정보를 앙상블(Ensemble) 모델로 통합

### 4.4 개인정보 보호 (Privacy)
- **제약**: 사용자 문자를 분석하는 과정에서 민감한 개인정보가 유출될 우려가 있습니다.
- **해결 전략**:
  - **On-Device AI 지향**: 민감 데이터는 서버로 전송하지 않고 로컬 기기 내에서 처리하도록 경량 모델 최적화 (향후 계획)
  - **비식별화(De-identification)**: 서버 전송 시 전화번호, 이름 등은 마스킹(Masking) 처리 후 분석 수행
