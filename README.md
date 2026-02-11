<div align="center">

#  Smishing Forecast

### *Self-Evolving AI-Powered Smishing Defense System*

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Transformers](https://img.shields.io/badge/🤗-Transformers-yellow.svg)](https://huggingface.co/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

![Smishing Forecast Screenshot](assets/main_screenshot.png)

</div>

---

## 👥 Team Members

| 이름 | 이메일 |
|------|--------|
| 조은경 | gracech0961@gmail.com |
| 안성민 | tjdals2299@gmail.com |
| 황동현 | myjewel29@naver.com |
| 황선우 | eddiehwang125@gmail.com |

---

## 📖 프로젝트 소개

AI 기반 자가 진화형 스미싱 탐지 및 방어 시스템입니다. 최신 뉴스를 기반으로 공격 시나리오를 예측하고, 적대적 학습(Adversarial Training)을 통해 실시간으로 방어력을 강화합니다.

## ✨ 주요 기능

### 🔴 Red Team (공격 시뮬레이션)
- **뉴스 기반 시나리오 기획**: 실제 사회 이슈를 활용한 현실적인 공격 전략 생성
- **GPT-4 기반 공격 문구 생성**: 자연스럽고 교묘한 스미싱 메시지 자동 생성
- **스텔스 모드**: URL, 전화번호, 의심 키워드를 제거한 은밀한 공격 시뮬레이션

### 🔵 Blue Team (방어 및 분석)
- **RoBERTa 기반 실시간 탐지**: `klue/roberta-base` 모델을 활용한 한국어 스미싱 탐지
- **의도 분석**: 공격자의 심리 기제, 위협 레벨, 법적 위반 소지 분석
- **자가 진화 (Self-Evolution)**: 탐지 실패 시 즉시 재학습하여 방어력 강화
- **보안 리포트 자동 생성**: PDF 보고서 생성 및 다운로드

### 💾 데이터 관리
- **SQLite 기반 영구 저장**: 뉴스, 공격 시나리오, 분석 결과, 보고서 자동 저장
- **Supabase 연동 지원**: 클라우드 데이터베이스 옵션 제공 (선택 사항)

## 🚀 설치 및 실행

### 1. 저장소 클론
```bash
git clone https://github.com/gracechoek/Hackathon_Smishing.git
cd Hackathon_Smishing
git checkout feat/ai-defense-update
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
```

### 4. 사전 학습된 모델 다운로드 (선택 사항)
사전 학습된 RoBERTa 모델을 사용하려면:
```bash
# Hugging Face에서 다운로드
# https://huggingface.co/donghyun95/smishing-detection-roberta-base
```

또는 프로그램 실행 시 `klue/roberta-base` 기본 모델로 시작 가능합니다.

### 5. 애플리케이션 실행
```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501`로 접속하세요.

## 📁 프로젝트 구조

```
Hackathon_Smishing/
├── app.py                      # Streamlit 메인 애플리케이션
├── database_manager.py         # 데이터베이스 관리 (SQLite/Supabase)
├── requirements.txt            # Python 의존성
├── .env.example               # 환경 변수 템플릿
│
├── src/                       # 핵심 모듈
│   ├── planner.py            # 공격 시나리오 기획 (Red Team)
│   ├── generator.py          # 공격 문구 생성 (GPT-4)
│   ├── intent_analyzer.py    # 의도 분석 (Blue Team)
│   ├── detector.py           # 스미싱 탐지 모델 (RoBERTa)
│   ├── trainer.py            # 자가 진화 학습 (Adversarial Training)
│   ├── report_generator.py   # 보안 리포트 생성 (PDF)
│   ├── utils.py              # 유틸리티 함수
│   └── crawler.py            # 뉴스 크롤러
│
├── data/                      # 데이터 저장소
│   ├── smishing_context_data.jsonl  # 뉴스 컨텍스트 데이터
│   └── test_dataset.json            # 평가용 데이터셋
│
├── models/                    # 학습된 모델 가중치
│   └── smishing_detector_model.pth  # Fine-tuned RoBERTa 가중치
│
└── scripts/                   # 유틸리티 스크립트
    └── deploy_model.py       # Hugging Face Hub 배포 스크립트
```

## 🎯 사용 방법

### 1. 공격 시나리오 생성
1. 왼쪽 사이드바에서 분석할 뉴스 선택
2. **[공격 시나리오 기획 (3종)]** 버튼 클릭
3. 3가지 전략 중 하나를 선택
4. **[이 전략으로 공격 문자 생성]** 버튼 클릭

### 2. 방어 분석
- 오른쪽 패널에서 자동으로 **의도 분석** 및 **실시간 탐지** 수행
- 탐지 점수가 낮을 경우 **[자가 진화 시작]** 버튼으로 즉시 재학습

### 3. 보안 리포트 생성
- **[리포트 생성 하기]** 버튼 클릭
- PDF 다운로드 또는 미리보기

## 🧠 핵심 기술

### AI 모델
- **텍스트 생성**: OpenAI GPT-4o (공격 시나리오 및 분석)
- **분류 모델**: klue/roberta-base (한국어 BERT 변형)
- **학습 방식**: Adversarial Training (적대적 학습)

### 데이터베이스
- **로컬**: SQLite3 (`smishing_db.db`)
- **클라우드**: Supabase (선택 사항)

### 프레임워크
- **UI**: Streamlit
- **ML**: PyTorch, Transformers (Hugging Face)

## 📊 데이터베이스 스키마

### `news_articles` (뉴스 기사)
- 뉴스 제목, 내용, 출처, 날짜, 카테고리

### `intents` (공격 시나리오)
- 전략명, 심리 기제, 논리, 메타데이터

### `attack_logs` (공격 로그)
- 생성된 메시지, 탐지 점수, 사용 모델, 타임스탬프

### `security_reports` (보안 리포트)
- 시나리오명, 뉴스 제목, 리포트 텍스트, PDF 데이터

## 🔬 모델 성능

### 초기 모델 (Pre-trained `klue/roberta-base`)
- **Precision**: 0.50 (Baseline)
- **Recall**: 1.00 (High False Positive)
- **F1-Score**: 0.67

### 진화 후 모델 (Self-Evolved)
- **Precision**: 0.50 → **1.00**
- **Recall**: 1.00 → **1.00**
- **F1-Score**: 0.67 → **1.00**


*(※ 위 성능은 합성 데이터셋 100건에 대한 평가 결과입니다. 학습 데이터와 동일한 생성 모델(GPT-4)로 만들어진 데이터이기에 높은 성능이 측정되었으며, 실제 스미싱 문자(Wild/Real-world)에 대해서는 성능 하락(Overfitting to Synthetic Distribution)이 발생할 수 있습니다.)*




## 🚀 Hugging Face Hub 배포

학습된 모델을 공유하려면:
```bash
# Hugging Face CLI 로그인
huggingface-cli login

# 모델 업로드
python scripts/deploy_model.py
```

배포된 모델: [donghyun95/smishing-detection-roberta-base](https://huggingface.co/donghyun95/smishing-detection-roberta-base)

## ⚠️ 주의사항

1. **윤리적 사용**: 이 시스템은 교육 및 연구 목적으로만 사용하세요.
2. **API 비용**: OpenAI API 사용량에 따라 비용이 발생할 수 있습니다.
3. **데이터 보안**: `.env` 파일은 절대 공개 저장소에 업로드하지 마세요.

## 📝 라이선스

MIT License

## 👥 기여자

- **Powered by**: OpenAI GPT-4, Hugging Face Transformers

## 🙏 감사의 말

- **KLUE Team**: 한국어 RoBERTa 모델 제공
- **Hugging Face**: 모델 호스팅 및 인프라 지원
- **OpenAI**: GPT-4 API 제공

---

**📧 문의**: gracechoek@github.com  
**🔗 Repository**: https://github.com/gracechoek/Hackathon_Smishing
