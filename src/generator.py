# generator.py
import openai
import os
import re
import json
from dotenv import load_dotenv

load_dotenv()

class SmishingGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API Key가 설정되지 않았습니다.")
        
        self.client = openai.OpenAI(api_key=self.api_key)

    def generate_attack_message(self, strategy_report):
        """
        Planner의 전략 리포트를 바탕으로 적대적 스미싱 문구를 생성합니다.
        """
        # Planner로부터 전달받은 세부 전략 데이터 추출
        intent = strategy_report.get("strategy_name", "미분류 전략")
        impersonation = strategy_report.get("impersonation", "알 수 없는 발신자")
        trigger = strategy_report.get("trigger", "일반적 유도")
        logic = strategy_report.get("logic", "링크 클릭 유도")
        
        # [수정] Crawler/Planner로부터 연계된 핵심 지표 추가
        target_emotion = strategy_report.get("target_emotion_mapped", "불안/긴박함")
        cta = strategy_report.get("call_to_action", "가짜 링크 클릭")

        prompt = f"""
        당신은 보안 시스템을 우회하여 목표를 달성하는 '적대적 메시지 설계자(Adversarial Message Designer)'입니다.
        아래 [공격 설계도]를 바탕으로, 실제 전송될 문자 메시지 내용을 단 하나만 생성하세요.

        [공격 설계도]
        1. 전략: {intent}
        2. 사칭: {impersonation}
        3. 심리적 트리거: {trigger} (핵심 감정: {target_emotion})
        4. 논리: {logic}
        5. 최종 목적(CTA): {cta}

        [실행 가이드라인]
        - **적대적 우회(Adversarial Evasion)**: KcBERT 등 인공지능 탐지 모델의 키워드 필터링을 무력화하기 위해, 주요 키워드에 특수문자나 의도적 오타를 섞으세요. (예: [부.고], [검_찰], [지/원/금])
        - **언어적 일관성**: {impersonation}의 권위나 성격에 맞는 완벽한 문체를 구사하세요. 
        - **현실적인 링크**: 시나리오에 어울리는 현실적인 형태의 가짜 URL을 포함하세요.
        - **무결성**: 인사말부터 링크까지 스미싱 문구 외의 다른 설명은 일절 배제하세요.
        """
        
        try:
            # [수정] 시스템 역할에 감정 기반 페르소나 주입
            response = self.client.chat.completions.create(
                model="gpt-4o", 
                messages=[
                    {"role": "system", "content": f"당신은 상대방의 {target_emotion}을 자극하여 행동을 유도하는 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8
            )
            
            message = response.choices[0].message.content.strip()
            
            # 클리닝 로직
            message = re.sub(r'^["\'\s]*|["\'\s]*$', '', message)
            message = re.sub(r'^(문자 내용|메시지|시나리오)[:\s]*', '', message)
            
            return message
            
        except Exception as e:
            return f"Error: {str(e)}"
        

if __name__ == "__main__":
    generator = SmishingGenerator()

    # Planner가 생성했을 법한 고도화된 전략 데이터 예시
    test_strategies = [
        {
            "strategy_name": "고압적 공공기관 사칭",
            "impersonation": "대검찰청 수사과",
            "trigger": "법적 처벌에 대한 공포",
            "logic": "개인정보 도용으로 인한 범죄 연루 알림 및 사건 번호 부여",
            "target_emotion_mapped": "법적 압박/권위 복종",
            "call_to_action": "공식 전자서류 확인"
        },
        {
            "strategy_name": "긴급 지인 사칭",
            "impersonation": "피해자의 딸",
            "trigger": "가족 안위에 대한 걱정",
            "logic": "휴대폰 액정 파손으로 통화 불가 상황에서 급한 결제 요청",
            "target_emotion_mapped": "걱정/긴박함",
            "call_to_action": "원격 제어 앱 설치"
        }
    ]

    print("[*] 적대적 문구 생성 테스트 시작...")
    print("-" * 50)

    for i, strategy in enumerate(test_strategies):
        print(f"[{i+1}] 적용 전략: {strategy['strategy_name']}")
        print(f"    사칭 대상: {strategy['impersonation']}")
        
        result = generator.generate_attack_message(strategy)
        
        print(f"\n[!] 생성된 적대적 메시지:")
        print(f"\"\"\"\n{result}\n\"\"\"")
        print("-" * 50)