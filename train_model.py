import os
import json
import torch
import sys
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from tqdm import tqdm

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.detector import SmishingDetector

# --- 설정 ---
EPOCHS = 3
BATCH_SIZE = 8
LEARNING_RATE = 2e-5
SAVE_PATH = "models/smishing_detector_model.pth"

class SmishingDataset(Dataset):
    def __init__(self, data, tokenizer, max_len=128):
        self.data = data
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        text = item['text']
        label = item['label']

        encoding = self.tokenizer(
            text,
            return_tensors='pt',
            max_length=self.max_len,
            padding='max_length',
            truncation=True
        )

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

def train():
    print("=== 🚀 모델 학습 (Fine-tuning) 시작 ===")
    
    # 1. 데이터 로드
    data_path = os.path.join("data", "train_dataset.json")
    if not os.path.exists(data_path):
        print(f"[!] 학습 데이터가 없습니다: {data_path}")
        return
        
    with open(data_path, "r", encoding="utf-8") as f:
        train_data = json.load(f)
        
    print(f"[*] 학습 데이터: {len(train_data)}건 로드 완료")

    # 2. 모델 및 토크나이저 초기화
    # detector를 초기화하면 pre-trained 모델이 로드됨
    detector = SmishingDetector() 
    model = detector.model
    tokenizer = detector.tokenizer
    device = detector.device
    
    model.train() # 학습 모드 전환

    # 3. DataLoader 준비
    dataset = SmishingDataset(train_data, tokenizer)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)

    # 4. 학습 루프
    print(f"[*] 학습 시작 (Epochs: {EPOCHS}, Device: {device})")
    print("-" * 50)
    
    for epoch in range(EPOCHS):
        total_loss = 0
        loop = tqdm(dataloader, desc=f"Epoch {epoch+1}/{EPOCHS}")
        
        for batch in loop:
            optimizer.zero_grad()
            
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            
            outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            loop.set_postfix(loss=loss.item())
            
        avg_loss = total_loss / len(dataloader)
        print(f"    -> Epoch {epoch+1} Average Loss: {avg_loss:.4f}")

    # 5. 모델 저장
    os.makedirs("models", exist_ok=True)
    
    # 전체 모델(가중치) 저장
    torch.save(model.state_dict(), SAVE_PATH)
    print("=" * 50)
    print(f"[Success] 학습된 모델 저장 완료: {SAVE_PATH}")
    print("이제 eval_pure_model.py를 실행하면 성능이 대폭 향상되었을 것입니다!")

if __name__ == "__main__":
    train()
