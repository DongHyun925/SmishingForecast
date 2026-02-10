# 🔮 Smishing Forecast - 데이터 출처 및 참고 문헌

본 문서는 프로젝트에서 **실제로 사용된** 외부 데이터, 모델, 도구의 출처와 라이선스 정보를 명시합니다.

## 📌 목차
1. [활용 데이터 (Data Sources)](#1-활용-데이터-data-sources)
2. [사전 학습 모델 (Pre-trained Models)](#2-사전-학습-모델-pre-trained-models)
3. [오픈소스 라이브러리 (Open Source Libraries)](#3-오픈소스-라이브러리-open-source-libraries)

---

## 1. 활용 데이터 (Data Sources)

### 1.1 NAVER News Search API (외부 데이터)
- **데이터셋 명칭**: 네이버 뉴스 검색 API 결과 (Title, Description)
- **출처 (URL)**: [NAVER Developers - Search API (News)](https://developers.naver.com/docs/serviceapi/search/news/news.md)
- **사용 목적**: 실시간 사회 이슈 파악 및 시나리오 생성의 맥락(Context) 정보로 활용
- **라이선스**: NAVER Developers Terms of Service (비상업적 연구 목적 / Fair Use 준수)
- **증빙**: `src/crawler.py` 내 `NaverApiCrawler` 클래스 구현

### 1.2 Synthetic Smishing Dataset (자체 생성 데이터)
- **데이터셋 명칭**: 적대적 생성 스미싱 데이터셋 (Adversarial Smishing Dataset)
- **출처**: OpenAI GPT-4o API를 통해 자체 생성 (Self-Generated)
- **데이터 규모**: 약 1,000건+ (스미싱 및 정상 문자)
- **사용 목적**: 방어 모델(RoBERTa)의 학습 및 검증 데이터로 활용
- **라이선스**: 생성된 결과물의 소유권은 사용자에게 있음 (OpenAI Terms of Use 준수)
- **증빙**: `make_test_dataset.py` 및 `data/test_dataset.json`

---

## 2. 사전 학습 모델 (Pre-trained Models)

### 2.1 KLUE-RoBERTa-Base
- **모델 명칭**: klue/roberta-base
- **출처 (URL)**: [Hugging Face Hub](https://huggingface.co/klue/roberta-base)
- **원문 논문**: Park, S., et al. "KLUE: Korean Language Understanding Evaluation", 2021. ([arXiv:2105.09680](https://arxiv.org/abs/2105.09680))
- **사용 목적**: 스미싱 탐지 및 분류 (Classification)
- **라이선스**: CC-BY-SA 4.0

### 2.2 OpenAI GPT-4o
- **모델 명칭**: gpt-4o
- **출처 (URL)**: [OpenAI API](https://platform.openai.com/docs/models)
- **사용 목적**: 공격 시나리오(Intent) 기획 및 적대적 메시지 생성
- **라이선스**: Commercial License (API Usage)

---

## 3. 오픈소스 라이브러리 (Open Source Libraries)

| 라이브러리명 | 버전 | 라이선스 | 출처 (URL) |
|-------------|-----|---------|------------|
| **PyTorch** | 2.0+ | BSD-3-Clause | [https://pytorch.org](https://pytorch.org) |
| **Transformers** | 4.30+ | Apache-2.0 | [https://github.com/huggingface/transformers](https://github.com/huggingface/transformers) |
| **Streamlit** | 1.25+ | Apache-2.0 | [https://streamlit.io](https://streamlit.io) |
| **Requests** | 2.31+ | Apache-2.0 | [https://requests.readthedocs.io](https://requests.readthedocs.io) |
| **Python-dotenv** | 1.0+ | BSD-3-Clause | [https://github.com/theskumar/python-dotenv](https://github.com/theskumar/python-dotenv) |
| **ReportLab** | 4.0+ | BSD-3-Clause | [https://www.reportlab.com](https://www.reportlab.com) |

---

## ⚠️ 라이선스 고지 (License Notice)
- 본 프로젝트는 **NAVER Developers**의 오픈 API 이용 약관을 준수하며, 수집된 뉴스 데이터는 원문 전체가 아닌 **요약 정보(Description)** 형태로만 일시적으로 활용됩니다.
- 생성형 AI(GPT-4o)를 통해 만들어진 데이터셋은 개인정보가 포함되지 않은 **가상 데이터**이므로, 별도의 개인정보 활용 동의가 필요하지 않습니다.
