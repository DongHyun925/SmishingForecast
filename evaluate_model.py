import os
import json
import sys
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.detector import SmishingDetector

def evaluate():
    print("=== 📊 모델 성능 평가 (Model Evaluation) ===")
    
    # 1. 데이터셋 로드
    data_path = os.path.join("data", "test_dataset.json")
    if not os.path.exists(data_path):
        print(f"[!] Error: 데이터셋 파일이 없습니다: {data_path}")
        return

    with open(data_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)
    
    print(f"[*] 테스트 데이터셋 로드 완료: {len(dataset)}건")

    # 2. 모델 로드
    print("[*] 모델 로드 중 (KLUE-RoBERTa)...")
    detector = SmishingDetector()

    # 3. 예측 실행
    y_true = []
    y_pred = []
    
    print("[*] 예측 수행 중...")
    for item in dataset:
        text = item['text']
        true_label = item['label'] # 1=Spam, 0=Ham
        
        # 모델 예측
        result = detector.predict(text)
        pred_label = 1 if result['is_smishing'] else 0
        
        y_true.append(true_label)
        y_pred.append(pred_label)

    # 4. 성능 지표 계산
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)

    # 5. 결과 출력 (파일 저장 및 콘솔 출력)
    output_lines = []
    output_lines.append("\n" + "="*40)
    output_lines.append(f"✅ 평가 결과 (데이터 개수: {len(dataset)})")
    output_lines.append("="*40)
    output_lines.append(f"  - 정확도 (Accuracy)  : {accuracy:.4f} ({accuracy*100:.1f}%)")
    output_lines.append(f"  - 정밀도 (Precision) : {precision:.4f}")
    output_lines.append(f"  - 재현율 (Recall)    : {recall:.4f}")
    output_lines.append(f"  - F1-Score           : {f1:.4f}")
    output_lines.append("="*40)
    
    output_lines.append("\n🔸 혼동 행렬 (Confusion Matrix):")
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    output_lines.append(f"  [True Negative (정상->정상)]: {tn}")
    output_lines.append(f"  [False Positive (정상->스미싱, 오탐)]: {fp}")
    output_lines.append(f"  [False Negative (스미싱->정상, 미탐)]: {fn}")
    output_lines.append(f"  [True Positive (스미싱->스미싱)]: {tp}")

    if fp > 0:
        output_lines.append("\n⚠️ 오탐(False Positive) 사례 분석 (정상인데 스미싱으로 분류):")
        cnt = 0
        for i, (t, p) in enumerate(zip(y_true, y_pred)):
            if t == 0 and p == 1:
                output_lines.append(f"  - \"{dataset[i]['text']}\"")
                cnt += 1
                if cnt >= 3: break

    if fn > 0:
        output_lines.append("\n⚠️ 미탐(False Negative) 사례 분석 (스미싱인데 정상으로 분류):")
        cnt = 0
        for i, (t, p) in enumerate(zip(y_true, y_pred)):
            if t == 1 and p == 0:
                output_lines.append(f"  - \"{dataset[i]['text']}\"")
                cnt += 1
                if cnt >= 3: break

    result_text = "\n".join(output_lines)
    print(result_text)
    
    with open("eval_result.txt", "w", encoding="utf-8") as f:
        f.write(result_text)
    print("\n[*] 결과 파일 저장 완료: eval_result.txt")

if __name__ == "__main__":
    evaluate()
