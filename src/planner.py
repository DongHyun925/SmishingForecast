# planner.py
import openai
import os
import json
from dotenv import load_dotenv

load_dotenv()

class SmishingPlanner:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API Key가 필요합니다.")
        self.client = openai.OpenAI(api_key=self.api_key)

    def plan_multiple_scenarios(self, processed_item, count=3):
        """
        Crawler에서 전처리된 데이터를 바탕으로 N개의 세분화된 시나리오를 설계합니다.
        """
        # Crawler가 만든 데이터 구조 분해
        context = processed_item.get("context", {})
        attack_design = processed_item.get("attack_design", {})
        
        news_title = context.get("news_title", "제목 없음")
        raw_content = processed_item.get("raw_text", "내용 없음")
        
        # Crawler가 주입한 기본 전략 (Baseline)
        base_logic = attack_design.get("strategy_logic", "일반적 유도")
        base_emotion = attack_design.get("target_emotion", "불안/긴박함")
        base_cta = attack_design.get("call_to_action", "링크 클릭")

        prompt = f"""
        당신은 고도로 훈련된 '사회공학적 공격 설계자'입니다. 
        제공된 [뉴스 정보]와 Crawler가 설정한 [기초 전략]을 바탕으로 실행 가능한 구체적 시나리오 {count}개를 설계하십시오.

        [1. 뉴스 정보]
        - 제목: {news_title}
        - 내용 요약: {raw_content[:400]}

        [2. 기초 전략 가이드 (Crawler 분석 결과)]
        - 핵심 공격 논리: {base_logic}
        - 타겟 심리 트리거: {base_emotion}
        - 최종 행동 유도(CTA): {base_cta}

        [3. 설계 지시사항]
        - 위 [기초 전략 가이드]의 본질을 유지하되, 각 시나리오가 서로 다른 '사칭 대상'과 '세부 심리 기제'를 갖도록 분화시키십시오.
        - 시나리오 1 (정석): 가이드라인을 가장 충실히 따르는 전형적인 공격
        - 시나리오 2 (변주): 사칭 대상을 바꾸어 타겟의 경계심을 푸는 우회적 접근
        - 시나리오 3 (심화): 뉴스 속 구체적 디테일을 언급하여 신뢰도를 극대화한 맞춤형 접근

        [응답 형식]
        - JSON 객체로만 응답하십시오.
        {{
            "scenarios": [
                {{
                    "id": "SCN-XX",
                    "strategy_name": "전략 명칭",
                    "impersonation": "구체적 사칭 대상",
                    "trigger": "사용될 핵심 심리 기제 (예: 법적 처벌 공포, 자녀 안위 걱정 등)",
                    "logic": "피해자를 속이기 위한 단계별 설득 논리",
                    "target_emotion_mapped": "{base_emotion}" 
                }}
            ]
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"당신은 {base_emotion} 심리를 정교하게 이용하는 공격 설계자입니다."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" },
                temperature=0.85
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("scenarios", [])

        except Exception as e:
            print(f"[!] 시나리오 설계 중 오류 발생: {e}")
            return []

if __name__ == "__main__":
    # Crawler가 생성했을 법한 가상 데이터로 테스트
    test_processed_item = {
        "context": {"news_title": "국세청 근로장려금 안내", "category": "GOV_IMPERSONATION"},
        "attack_design": {
            "strategy_logic": "공식 문서 번호를 언급하며 법적 불이익 경고",
            "target_emotion": "법적 압박/권위 복종",
            "call_to_action": "전자고지서 확인"
        },
        "raw_text": "국세청은 2025년 상반기 근로장려금 지급 대상을 확정했습니다..."
    }

    planner = SmishingPlanner()
    scenarios = planner.plan_multiple_scenarios(test_processed_item)
    print(json.dumps(scenarios, indent=4, ensure_ascii=False))