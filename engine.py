import json
import os
import random
from src.generator import SmishingGenerator
from src.detector import SmishingDetector
from src.utils import load_jsonl

class AdversarialEngine:
    def __init__(self):
        # 1. 공격자와 방어자 초기화
        self.generator = SmishingGenerator()
        self.detector = SmishingDetector()
        self.vulnerabilities = []

    def run_simulation(self, data_path, num_samples=5):
        """
        데이터셋에서 뉴스를 뽑아 공격 시뮬레이션을 실행
        """
        print(f"\n[*] 적대적 시뮬레이션 시작 (샘플 수: {num_samples})")
        
        # 2. 크롤링된 뉴스 데이터 로드
        try:
            scenarios = load_jsonl(data_path)
            # 전체 데이터 중 랜덤하게 샘플링
            samples = random.sample(scenarios, min(num_samples, len(scenarios)))
        except Exception as e:
            print(f"[!] 데이터 로드 실패: {e}")
            return

        for i, sample in enumerate(samples):
            title = sample['context']['news_title']
            content = sample.get('raw_text', "")
            
            print(f"\n[{i+1}/{num_samples}] 뉴스 맥락 분석 중: {title}")
            
            # 3. 공격자(LLM): 스미싱 문구 생성
            attack_msg = self.generator.generate_attack_message(title, content)
            
            # 4. 방어자(BERT): 탐지 시도
            result = self.detector.predict(attack_msg)
            
            # 5. 적대적 학습 데이터 선별: 방어자가 '정상'으로 오판(False Negative)한 경우
            if not result['is_smishing']:
                print(f"🚨 [방어 실패] 정교한 공격이 탐지망을 통과했습니다!")
                self.vulnerabilities.append({
                    "news_context": title,
                    "attack_message": attack_msg,
                    "confidence": result['confidence'],
                    "status": "FAILED_TO_DETECT"
                })
            else:
                print(f"🛡️ [방어 성공] 스미싱 문구를 차단했습니다. (신뢰도: {result['confidence']:.2f})")

        # 6. 결과 저장
        self.save_results()

    def save_results(self):
        save_path = os.path.join("data", "vulnerabilities.json")
        
        # 기존 데이터가 있다면 불러와서 합치기 (데이터 누적)
        existing_data = []
        if os.path.exists(save_path):
            with open(save_path, "r", encoding="utf-8") as f:
                try:
                    existing_data = json.load(f)
                except:
                    existing_data = []
        
        combined_data = existing_data + self.vulnerabilities
        
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(combined_data, f, ensure_ascii=False, indent=4)
            
        print(f"\n" + "="*50)
        print(f"[*] 시뮬레이션 완료!")
        print(f"[*] 새로 발견된 취약점: {len(self.vulnerabilities)}건")
        print(f"[*] 전체 누적 취약점: {len(combined_data)}건")
        print(f"[*] 결과 저장 위치: {save_path}")
        print("="*50)

if __name__ == "__main__":
    engine = AdversarialEngine()
    # data 폴더의 jsonl 파일을 읽어 5개의 뉴스로 테스트
    data_file = os.path.join("data", "smishing_context_data.jsonl")
    engine.run_simulation(data_file, num_samples=5)