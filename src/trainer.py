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
        self.optimizer = AdamW(self.model.parameters(), lr=2e-5)

    def train_on_vulnerabilities(self, data_path="data/vulnerabilities.json"):
        """
        Detector를 통과해버린(공격 성공) 데이터셋만 골라 학습하여 방어력을 강화합니다.
        (Normalization: 정상 데이터를 함께 학습하여 과적합/망각 방지)
        """
        if not os.path.exists(data_path):
            print(f"[!] 취약점 데이터셋을 찾을 수 없습니다: {data_path}")
            return

        with open(data_path, "r", encoding="utf-8") as f:
            vulnerabilities = json.load(f)

        # ... (rest of function until TARGET_CONFIDENCE) ...
        # [추가] 정상 데이터(Ham) 로드 - 균형 학습용 (Replay Buffer)
        ham_samples = []
        try:
            with open("data/test_dataset.json", "r", encoding="utf-8") as f:
                all_data = json.load(f)
                ham_samples = [d['text'] for d in all_data if d['label'] == 0]
                print(f"[*] 균형 학습을 위해 정상 데이터 {len(ham_samples)}개를 확보했습니다.")
        except Exception as e:
            print(f"[!] 정상 데이터 로드 실패 (Overfitting 위험): {e}")

        if not vulnerabilities:
            return

        print(f"[*] 총 {len(vulnerabilities)}개의 취약점 학습 시작 (with Regularization)...")
        
        self.model.train()
        
        # [수정] 과도한 학습(1.0000)을 방지하기 위해 목표 신뢰도를 0.95로 하향
        TARGET_CONFIDENCE = 0.95
        MAX_STEPS = 20 # 스텝 수도 줄임
        
        import random

        for item in vulnerabilities:
            text = item.get('generated_message', item.get('attack_message', ""))
            clean_text = self.detector.preprocess(text)
            
            print(f"[*] '{text[:20]}...' 집중 학습 중...")
            
            for step in range(MAX_STEPS):
                # 1. 취약점(Spam) 학습
                inputs = self.tokenizer(clean_text, return_tensors="pt", truncation=True, padding=True).to(self.detector.device)
                label = torch.tensor([1]).to(self.detector.device)

                self.optimizer.zero_grad()
                outputs = self.model(**inputs, labels=label)
                loss_spam = outputs.loss
                
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

                # Total Loss = Spam Loss + (Ham Loss * 2.0) : 정상 데이터 가중치 2배 부여
                total_loss = loss_spam + (loss_ham * 2.0)
                total_loss.backward()
                self.optimizer.step()

                # 확률 체크 (Spam에 대해서만)
                probs = torch.softmax(self.model(**inputs).logits, dim=1)
                smishing_prob = probs[0][1].item()
                
                if smishing_prob >= TARGET_CONFIDENCE:
                    print(f"    -> [Success] Step {step}: 확률 {smishing_prob:.4f} 도달!")
                    break

        self.save_model()

    def save_model(self):
        # trainer.py는 독립 실행보다는 앱 내부에서 호출되므로, 
        # detector가 로드하는 경로("models/smishing_detector_model.pth")에 저장해야 함.
        save_path = "models/smishing_detector_model.pth"
        
        # 전체 모델(가중치) 저장
        # HuggingFace save_pretrained 대신 torch.save 사용 (detector.py 로딩 방식과 통일)
        torch.save(self.model.state_dict(), save_path)
        print(f"[*] 모델 진화 완료. '{save_path}'에 업데이트되었습니다.")