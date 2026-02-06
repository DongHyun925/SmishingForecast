import torch
import re
import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class SmishingDetector:
    def __init__(self, model_name="klue/roberta-base", threshold=0.7):
        print(f"[*] 모델 로딩 중: {model_name}...")
        
        # Hugging Face 표준 AutoClass 사용 (별도 설정 불필요)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
        
        # [수정] 학습된 가중치가 있으면 로드
        weights_path = "models/smishing_detector_model.pth"
        if os.path.exists(weights_path):
            print(f"[*] 학습된 가중치 발견! 로드 중: {weights_path}")
            # map_location을 사용하여 CPU/GPU 호환성 확보
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.load_state_dict(torch.load(weights_path, map_location=device))
        else:
            print("[!] 학습된 가중치가 없습니다. Pre-trained 상태로 시작합니다.")

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()
        
        # 보안 민감도 설정을 위한 임계값
        self.threshold = threshold

    def preprocess(self, text):
        """특수문자 노이즈 제거 및 입력 정제"""
        # 한글, 숫자, 영문, 기본적인 문장부호 제외 제거
        clean_text = re.sub(r'[^가-힣a-zA-Z0-9\s]', '', text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text

    def predict(self, text):
        """
        문장이 스미싱일 확률을 계산하고 상세 분석 결과를 반환
        """
        processed_text = self.preprocess(text)
        
        inputs = self.tokenizer(
            processed_text, 
            return_tensors="pt", 
            truncation=True, 
            max_length=128, 
            padding=True
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # 확률 변환
        probs = torch.softmax(outputs.logits, dim=1)
        # 보통 라벨 1을 스미싱(Positive)으로 학습함
        smishing_prob = probs[0][1].item() 
        
        # 단순 argmax가 아닌 임계값 기반 판정
        is_smishing = smishing_prob >= self.threshold
        
        return {
            "is_smishing": is_smishing,
            "confidence": smishing_prob if is_smishing else (1 - smishing_prob),
            "smishing_score": smishing_prob, # 0~1 사이의 순수 스미싱 확률
            "original_text": text,
            "processed_text": processed_text
        }