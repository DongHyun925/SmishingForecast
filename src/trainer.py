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
        # [변경] 데모 효과를 위해 학습률을 2e-6 -> 5e-5로 대폭 상향 (즉각 반응 유도)
        self.optimizer = AdamW(self.model.parameters(), lr=5e-5)

    def train_on_vulnerabilities(self, data_path="data/vulnerabilities.json"):
        """
        Detector를 통과해버린(공격 성공) 데이터셋만 골라 학습하여 방어력을 강화합니다.
        (데모 효과를 위해 Target Probability(0.98)에 도달할 때까지 반복 학습합니다.)
        """
        if not os.path.exists(data_path):
            print(f"[!] 취약점 데이터셋을 찾을 수 없습니다: {data_path}")
            return

        with open(data_path, "r", encoding="utf-8") as f:
            vulnerabilities = json.load(f)

        if not vulnerabilities:
            print("[!] 새로운 취약점 데이터가 없어 학습을 건너뜁니다.")
            return

        print(f"[*] 총 {len(vulnerabilities)}개의 탐지 취약점 발견. 모델 강화 학습 시작...")
        
        self.model.train()
        
        # [변경] "될 때까지 학습한다" (Target-based Overfitting)
        TARGET_CONFIDENCE = 0.98
        MAX_STEPS = 30
        
        for item in vulnerabilities:
            # 'attack_message' 또는 'generated_message' 중 존재하는 필드 사용
            text = item.get('generated_message', item.get('attack_message', ""))
            clean_text = self.detector.preprocess(text)
            
            print(f"[*] '{text[:20]}...'에 대한 집중 학습 시작")
            
            for step in range(MAX_STEPS):
                # 1. 현재 상태 평가 (Eval 모드 아님 - Train 모드에서 평가하여 그라디언트 유지)
                inputs = self.tokenizer(clean_text, return_tensors="pt", truncation=True, padding=True).to(self.detector.device)
                label = torch.tensor([1]).to(self.detector.device) # Target: Smishing(1)

                self.optimizer.zero_grad()
                outputs = self.model(**inputs, labels=label)
                
                # 현재 확률 확인
                probs = torch.softmax(outputs.logits, dim=1)
                smishing_prob = probs[0][1].item()
                
                if smishing_prob >= TARGET_CONFIDENCE:
                    print(f"    -> [Success] Step {step}: 확률 {smishing_prob:.4f} 도달! (목표 달성)")
                    break
                
                # 2. 학습 (Backprop)
                loss = outputs.loss
                loss.backward()
                self.optimizer.step()

                if step % 5 == 0:
                    print(f"    -> [Step {step}] Prob({smishing_prob:.4f}) / Loss({loss.item():.4f}) - 학습 진행 중...")

        # [수정] 학습된 가중치를 메인 모델 경로에 덮어씌움 (앱 재실행 시 반영되도록)
        self.save_model()

    def save_model(self):
        # trainer.py는 독립 실행보다는 앱 내부에서 호출되므로, 
        # detector가 로드하는 경로("models/smishing_detector_model.pth")에 저장해야 함.
        save_path = "models/smishing_detector_model.pth"
        
        # 전체 모델(가중치) 저장
        # HuggingFace save_pretrained 대신 torch.save 사용 (detector.py 로딩 방식과 통일)
        torch.save(self.model.state_dict(), save_path)
        print(f"[*] 모델 진화 완료. '{save_path}'에 업데이트되었습니다.")