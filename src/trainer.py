# trainer.py
import torch
from torch.optim import AdamW
from src.detector import SmishingDetector
import json
import os

class SmishingTrainer:
    def __init__(self, detector):
        self.detector = detector
        self.model = detector.model
        self.tokenizer = detector.tokenizer
        self.optimizer = AdamW(self.model.parameters(), lr=2e-6)

    def train_on_vulnerabilities(self, data_path="data/vulnerabilities.json"):
        """
        Detector를 통과해버린(공격 성공) 데이터셋만 골라 학습하여 방어력을 강화합니다.
        """
        if not os.path.exists(data_path):
            print(f"[!] 취약점 데이터셋을 찾을 수 없습니다: {data_path}")
            return

        with open(data_path, "r", encoding="utf-8") as f:
            vulnerabilities = json.load(f)

        if not vulnerabilities:
            print("[!] 새로운 취약점 데이터가 없어 학습을 건너跳니다.")
            return

        print(f"[*] 총 {len(vulnerabilities)}개의 탐지 취약점 발견. 모델 강화 학습 시작...")
        
        
        self.model.train()
        for i, item in enumerate(vulnerabilities):
            # 'attack_message' 또는 'generated_message' 중 존재하는 필드 사용
            text = item.get('generated_message', item.get('attack_message', ""))
            severity = item.get('intent_analysis', {}).get('severity', 3)
            weight = severity / 3.0

            clean_text = self.detector.preprocess(text)
            inputs = self.tokenizer(clean_text, return_tensors="pt", truncation=True, padding=True).to(self.detector.device)
            label = torch.tensor([1]).to(self.detector.device) # 스미싱으로 강제 교정

            self.optimizer.zero_grad()
            outputs = self.model(**inputs, labels=label)
            loss = outputs.loss * weight
            loss.backward()
            self.optimizer.step()

            if (i+1) % 1 == 0:
                print(f"    [Step {i+1}] Loss: {loss.item():.4f} | Severity: {severity}")

        self.save_model()

    def save_model(self):
        save_path = "models/refined_kcbert"
        self.model.save_pretrained(save_path)
        self.tokenizer.save_pretrained(save_path)
        print(f"[*] 모델 진화 완료. '{save_path}'에 저장되었습니다.")