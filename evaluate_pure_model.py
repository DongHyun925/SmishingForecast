import os
import json
import sys
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.detector import SmishingDetector

def evaluate_pure():
    print("=== 🧪 순수 모델 성능 평가 (Threshold=0.5 고정) ===")
    
    # 1. 데이터셋 로드
    data_path = os.path.join("data", "test_dataset.json")
    if not os.path.exists(data_path):
        print(f"[!] Error: 데이터셋 파일이 없습니다: {data_path}")
        return

    with open(data_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    # 2. 모델 로드
    detector = SmishingDetector() # 기본 threshold는 무시하고 score만 가져옴
    
    y_true = []
    y_scores = []
    
    print("[*] Raw Score(확률) 추출 중...")
    
    spam_scores = []
    ham_scores = []

    for item in dataset:
        text = item['text']
        true_label = item['label']
        
        # predict() 호출 -> 내부 smishing_score (0.0~1.0) 반환
        result = detector.predict(text)
        score = result['smishing_score']
        
        y_true.append(true_label)
        y_scores.append(score)
        
        if true_label == 1:
            spam_scores.append(score)
        else:
            ham_scores.append(score)

    # 3. 성능 분석 (Threshold 0.5 기준)
    threshold = 0.5
    y_pred = [1 if s >= threshold else 0 for s in y_scores]
    
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    
    try:
        roc_auc = roc_auc_score(y_true, y_scores)
    except:
        roc_auc = 0.5

    # 4. 결과 출력
    print("\n" + "="*50)
    print(f"📊 Pure Model Metrics (Threshold {threshold})")
    print("="*50)
    print(f"  Accuracy  : {accuracy:.4f}")
    print(f"  Precision : {precision:.4f}")
    print(f"  Recall    : {recall:.4f}")
    print(f"  F1-Score  : {f1:.4f}")
    print(f"  ROC-AUC   : {roc_auc:.4f}")
    print("="*50)

    print("\n📈 Score Distribution Analysis")
    print(f"  [Spam] 평균 점수: {np.mean(spam_scores):.4f} (Min: {np.min(spam_scores):.4f}, Max: {np.max(spam_scores):.4f})")
    print(f"  [Ham]  평균 점수: {np.mean(ham_scores):.4f} (Min: {np.min(ham_scores):.4f}, Max: {np.max(ham_scores):.4f})")
    
    diff = np.mean(spam_scores) - np.mean(ham_scores)
    print(f"  => 점수 차이(변별력): {diff:.4f}")
    
    if abs(diff) < 0.05:
        print("\n[진단] ⚠️ 모델이 Spam과 Ham을 전혀 구별하지 못하고 있습니다. (Random Guessing 수준)")
        print("       원인: Pre-trained 모델 헤드가 초기화된 상태로 fine-tuning 되지 않았음.")
    else:
        print("\n[진단] ✅ 모델이 어느 정도 구별하고 있습니다.")

    # 5. 결과 저장
    with open("eval_pure_result.txt", "w", encoding="utf-8") as f:
        f.write(f"Accuracy: {accuracy}\nF1: {f1}\nAvg_Spam: {np.mean(spam_scores)}\nAvg_Ham: {np.mean(ham_scores)}")

if __name__ == "__main__":
    evaluate_pure()
