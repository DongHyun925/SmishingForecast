
import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from huggingface_hub import HfApi, HfFolder, create_repo

# 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # 프로젝트 루트 (scripts/.. => root)
MODEL_NAME = "klue/roberta-base"
WEIGHTS_PATH = os.path.join(BASE_DIR, "models", "smishing_detector_model.pth")
REPO_ID = "donghyun95/smishing-detection-roberta-base"
COMMIT_MESSAGE = "Upload fine-tuned smishing detection model"

def deploy():
    print(f"[*] Base Model 로딩 중: {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
    
    # 가중치 로드
    if os.path.exists(WEIGHTS_PATH):
        print(f"[*] Fine-tuned 가중치 로드 중: {WEIGHTS_PATH}")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.load_state_dict(torch.load(WEIGHTS_PATH, map_location=device))
    else:
        print(f"[!] 가중치 파일을 찾을 수 없습니다: {WEIGHTS_PATH}")
        print("    모델이 학습되지 않은 상태인 것 같습니다. 먼저 학습을 진행해주세요.")
        return

    # 저장할 디렉토리 생성
    output_dir = "./hf_model_upload"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"[*] 모델 및 토크나이저 저장 중: {output_dir}")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    # Model Card 생성
    readme_content = f"""---
language: kr
tags:
- smishing
- security
- classification
- roberta
pipeline_tag: text-classification
---

# Smishing Detection Model (RoBERTa-Base)

이 모델은 한국어 스미싱 탐지를 위해 `klue/roberta-base`를 파인튜닝한 모델입니다.

## Model Details
- **Base Model:** klue/roberta-base
- **Fine-tuning Data:** Synthesized Smishing/Ham Dataset + Self-Evolution via Adversarial Training
- **Author:** donghyun95
- **Task:** Binary Classification (0: Normal, 1: Smishing)

## Usage
```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model_name = "{REPO_ID}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

text = "엄마 나 폰 액정 깨졌어 급하게 송금해줘"
inputs = tokenizer(text, return_tensors="pt")

with torch.no_grad():
    logits = model(**inputs).logits
    probs = torch.softmax(logits, dim=1)
    print(f"Smishing Probability: {{probs[0][1].item()*100:.2f}}%")
```
"""
    with open(os.path.join(output_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)
        
    print("[*] Hugging Face Hub 업로드 준비 완료.")
    
    # 토큰 확인
    token = HfFolder.get_token()
    if token is None:
        print("\n[!] Hugging Face 로그인이 필요합니다.")
        print("    터미널에서 `huggingface-cli login`을 실행하거나, 아래에 토큰을 입력하세요.")
        token_input = input("    Enter your Hugging Face Write Token (or press Enter to skip): ").strip()
        if token_input:
            token = token_input
            HfFolder.save_token(token)
        else:
            print("[!] 업로드를 중단합니다. 로그인 후 다시 실행해주세요.")
            return

    try:
        print(f"[*] Hub에 업로드 중... Target: {REPO_ID}")
        api = HfApi()
        
        # Repo 생성 (없으면 생성, 있으면 무시)
        create_repo(repo_id=REPO_ID, token=token, exist_ok=True, private=False)
        
        # 폴더 업로드
        api.upload_folder(
            folder_path=output_dir,
            repo_id=REPO_ID,
            commit_message=COMMIT_MESSAGE,
            token=token
        )
        print(f"\n[SUCCESS] 모델 업로드 완료! 🚀")
        print(f"👉 https://huggingface.co/{REPO_ID}")
        
    except Exception as e:
        print(f"\n[ERROR] 업로드 실패: {e}")

if __name__ == "__main__":
    deploy()
