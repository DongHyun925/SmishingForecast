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
<<<<<<< Updated upstream
        # [변경] 데모 효과를 위해 학습률을 2e-6 -> 5e-5로 대폭 상향 (즉각 반응 유도)
        self.optimizer = AdamW(self.model.parameters(), lr=5e-5)
=======
        self.optimizer = AdamW(self.model.parameters(), lr=1e-5) # [조정] 더 세밀한 학습을 위해 LR 하향
>>>>>>> Stashed changes

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
        
<<<<<<< Updated upstream
        # [변경] "될 때까지 학습한다" (Target-based Overfitting)
        TARGET_CONFIDENCE = 0.98
        MAX_STEPS = 30
=======
        # [수정] 과도한 학습(Extreme Learning) 방지를 위해 수치 대폭 완화
        TARGET_CONFIDENCE = 0.85 # 0.95 -> 0.85 (완만한 학습 유도)
        MAX_STEPS = 5           # 20 -> 5 (과적합 방지)
>>>>>>> Stashed changes
        
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
                
<<<<<<< Updated upstream
                # 현재 확률 확인
                probs = torch.softmax(outputs.logits, dim=1)
=======
                # 2. [강화된 Regularization] 정상 데이터(Ham) 4배수 학습 (Overfitting 강력 억제)
                loss_ham = 0
                if ham_samples:
                    # 안정성을 위해 정상 데이터를 4개 뽑아서 평균 Loss를 구함
                    ham_batch = random.sample(ham_samples, k=min(len(ham_samples), 4))
                    for h_text in ham_batch:
                        h_inputs = self.tokenizer(h_text, return_tensors="pt", truncation=True, padding=True).to(self.detector.device)
                        h_label = torch.tensor([0]).to(self.detector.device) # Target: Ham(0)
                        
                        h_outputs = self.model(**h_inputs, labels=h_label)
                        loss_ham += h_outputs.loss
                    
                    # 4개분 Loss를 평균내거나 합산 (여기서는 합산하여 정상 데이터 비중을 높임)
                    loss_ham = loss_ham / len(ham_batch) 

                # Total Loss = Spam Loss + (Ham Loss * 3.0) : 정상 데이터 가중치 대폭 강화 (일반 문장 망각 방지)
                total_loss = loss_spam + (loss_ham * 3.0)
                total_loss.backward()
                self.optimizer.step()

                # 확률 체크 (Spam에 대해서만)
                probs = torch.softmax(self.model(**inputs).logits, dim=1)
>>>>>>> Stashed changes
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