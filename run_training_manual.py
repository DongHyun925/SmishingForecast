
import sys
import os
import json
import torch
import random
from torch.utils.data import DataLoader, Dataset
from torch.optim import AdamW

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.detector import SmishingDetector

# Define dataset class
class SmishingDataset(Dataset):
    def __init__(self, data_path, tokenizer):
        with open(data_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        text = item['text']
        label = item['label']
        
        encoding = self.tokenizer(text, return_tensors='pt', padding='max_length', truncation=True, max_length=128)
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

def train():
    print("[*] Starting manual retraining to calibrate model sensitivity...")
    
    # Initialize detector (loads current model)
    detector = SmishingDetector()
    model = detector.model
    tokenizer = detector.tokenizer
    device = detector.device
    model.to(device)
    model.train()

    # Load dataset with new 'Business = Safe' examples
    dataset = SmishingDataset('data/train_dataset.json', tokenizer)
    loader = DataLoader(dataset, batch_size=8, shuffle=True)

    # Optimizer
    optimizer = AdamW(model.parameters(), lr=2e-5)

    epochs = 3
    for epoch in range(epochs):
        print(f"Epoch {epoch+1}/{epochs}")
        total_loss = 0
        for batch in loader:
            optimizer.zero_grad()
            
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        print(f"  Average Loss: {total_loss / len(loader):.4f}")

    # Save model
    save_path = "models/smishing_detector_model.pth"
    torch.save(model.state_dict(), save_path)
    print(f"[*] Model saved to {save_path}")

if __name__ == "__main__":
    train()
