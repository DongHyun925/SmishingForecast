## 📄 README.md 

```markdown
# 🛡️ Hackathon_Smishing

스미싱 방지를 위한 KcBERT 기반 텍스트 분류 프로젝트입니다.

## ⚙️ 시작하기 전 (Pre-requisites)

이 프로젝트는 대용량 모델 파일(`model.safetensors`)을 포함하고 있지 않습니다. 프로젝트 실행을 위해 아래 가이드에 따라 모델 파일을 수동으로 다운로드해야 합니다.

### 1. 모델 파일 다운로드
* **다운로드 링크:** https://www.notion.so/MVP-2f2bf15f4f2680f5b964d51419383b0b?source=copy_link
* **파일명:** `model.safetensors`

### 2. 모델 파일 배치
다운로드한 파일을 프로젝트 내 아래 경로에 위치시켜 주세요:
```text
models/refined_kcbert/
└── model.safetensors

```

---

## 🚀 설치 및 실행 방법

1. **저장소 클론**
```bash
git clone [https://github.com/gracechoek/Hackathon_Smishing.git](https://github.com/gracechoek/Hackathon_Smishing.git)
cd Hackathon_Smishing

```

2. **모델 파일 확인**
위의 '시작하기 전' 가이드에 따라 모델 파일이 정해진 경로에 있는지 확인합니다.

3. **pipeline 통합 실행**
```bash
python main.py

```

4. **데모 실행**
```bash
streamlit run app.py
```



---

## 🛠️ 기술 스택

* **Language:** Python
* **Model:** KcBERT (Refined)
* **Library:** HuggingFace Transformers, PyTorch

```
