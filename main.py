import os
import sys
import json
import random
from datetime import datetime

# 모듈 로드 로직
try:
    from src.planner import SmishingPlanner
    from src.generator import SmishingGenerator
    from src.intent_analyzer import IntentAnalyzer
    from src.detector import SmishingDetector
    from src.trainer import SmishingTrainer
    from src.utils import load_jsonl
except Exception as e:
    print(f"[Critical Error] 모듈 로드 실패: {e}")
    sys.exit(1)

def is_valid_attack_message(message):
    """
    생성된 문구가 LLM의 거절 응답인지, 혹은 물리적으로 유효한 공격 샘플인지 검증
    """
    # 1. LLM의 대표적인 거절 패턴 (Safety Refusal)
    refusal_patterns = [
        "수행할 수 없습니다", "도와드릴 수 없습니다", "죄송하지만", 
        "알 수 없는 오류", "부적절한 요청", "정책에 따라", "제공할 수 없습니다"
    ]
    if any(pattern in message for pattern in refusal_patterns):
        return False, "LLM Safety Refusal"
    
    # 2. 구조적 유효성 검사
    clean_msg = message.replace(" ", "")
    if len(clean_msg) < 10:
        return False, "Too Short Message"
        
    return True, "Valid"

def run_pipeline():
    print("\n" + "="*75)
    print("      [SELF-EVOLVING DEFENSE SYSTEM: SMART DATA VALIDATION]")
    print("="*75)

    planner = SmishingPlanner()
    generator = SmishingGenerator()
    intent_analyzer = IntentAnalyzer()
    
    DETECTION_THRESHOLD = 0.8
    EVOLUTION_THRESHOLD = 0.95 
    
    detector = SmishingDetector(threshold=DETECTION_THRESHOLD)
    trainer = SmishingTrainer(detector)
    
    data_path = "data/smishing_context_data.jsonl"
    scenarios_data = load_jsonl(data_path)
    if not scenarios_data: return

    sample_news = random.choice(scenarios_data)
    final_logs = []
    vulnerability_logs = []

    print(f"\n[Step 1] 뉴스 분석: {sample_news['context']['news_title']}")
    attack_strategies = planner.plan_multiple_scenarios(sample_news, count=3)

    for i, strategy in enumerate(attack_strategies):
        print(f"\n[Scenario {i+1}] {strategy['strategy_name']}")
        
        # 1. 문구 생성 (개선된 프롬프트가 적용된 generator 호출)
        attack_msg = generator.generate_attack_message(strategy)
        
        # [추가] 생성된 문구의 유효성 즉시 검증
        is_valid, validation_reason = is_valid_attack_message(attack_msg)
        if not is_valid:
            print(f" ⚠️ 생성 실패: {validation_reason} (문구: {attack_msg[:20]}...)")
            continue

        # 2. 의도 및 위험도 분석
        analysis_res = intent_analyzer.analyze_intent(attack_msg)
        
        # 3. 방어 검증
        detection_res = detector.predict(attack_msg)
        smishing_score = detection_res['smishing_score']
        
        # 4. 구조적 필터링 (품질 검사)
        has_url = any(x in attack_msg.lower() for x in ["http", "bit.ly", "t.me", "/", ".com", ".kr"])
        is_nonsense = smishing_score < 0.25 

        # 5. 자가 진화 판단 로직
        should_train = False
        evolution_reason = ""

        if not detection_res['is_smishing']:
            should_train = True
            evolution_reason = "Detection Failed (Critical)"
        elif smishing_score < EVOLUTION_THRESHOLD:
            should_train = True
            evolution_reason = f"Low Confidence Defense (Score: {smishing_score:.4f})"

        # 최종 적합성 판단 (짧은 문구여도 URL이 있으면 학습 가치 있음)
        if should_train and (is_nonsense or (len(attack_msg.replace(" ","")) < 15 and not has_url)):
            should_train = False
            evolution_reason = "Low Information Density"

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "generated_message": attack_msg,
            "intent_analysis": analysis_res,
            "defense_result": detection_res,
            "evolution_target": should_train,
            "evolution_reason": evolution_reason if should_train else "Hardened"
        }
        final_logs.append(log_entry)

        print(f" > 문구: \"{attack_msg}\"")
        if should_train:
            print(f" 🚨 취약점 감지: {evolution_reason} -> 적대적 재학습 수행")
            vulnerability_logs.append(log_entry)
            
            temp_path = "data/vulnerabilities_temp.json"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump([log_entry], f, indent=4, ensure_ascii=False)
            trainer.train_on_vulnerabilities(temp_path)
            os.remove(temp_path)
        else:
            final_status = "Perfect" if detection_res['is_smishing'] else "Invalid/Noise"
            print(f" 🛡️ 학습 제외 ({final_status})")

    # 7. 결과 저장
    with open("data/final_dataset.json", "w", encoding="utf-8") as f:
        json.dump(final_logs, f, indent=4, ensure_ascii=False)
    
    with open("data/vulnerabilities.json", "w", encoding="utf-8") as f:
        json.dump(vulnerability_logs, f, indent=4, ensure_ascii=False)

    print(f"\n[DONE] 유효 취약점 {len(vulnerability_logs)}건 확보 및 모델 강화 완료.")

if __name__ == "__main__":
    run_pipeline()