# planner.py
import openai
import os
import json
from dotenv import load_dotenv

load_dotenv(override=True)

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
        당신은 상위 0.1%의 '사회공학적 공격 설계자'이자 '행동심리학자'입니다.
        제공된 [뉴스 정보]와 Crawler가 설정한 [기초 전략]을 바탕으로, 피해자가 전혀 예상치 못할 만큼 예리하고 치명적인 시나리오 {count}개를 설계하십시오.

        [1. 분석 대상: 뉴스 정보]
        - 제목: {news_title}
        - 내용 요약: {raw_content[:400]}

        [2. 기초 전략 가이드 (Crawler 분석 결과)]
        - 핵심 공격 논리: {base_logic}
        - 타겟 심리 트리거: {base_emotion}
        - 최종 행동 유도(CTA): {base_cta}

        [3. **고도화 설계 지시사항 (가장 중요)**]
        단순히 정보를 전달하는 수준을 넘어, 인간의 **인지적 편향(Cognitive Bias)**과 **방심하는 틈(Blind Spot)**을 정밀하게 타격해야 합니다.
        다음의 3가지 차원에서 시나리오를 전개하십시오:

        - **시나리오 1 [역발상적 접근]**: 
          사람들은 보통 '혜택'이나 '경고'를 예상합니다. 하지만 **"도움을 요청"하거나 "사소한 실수를 가장"**하여 타겟의 선의나 호기심을 악용하는 전혀 다른 각도를 설계하십시오.
          (예: "택배 기사인데 주소가 지워져서요..." / "이거 부장님이 보내신 자료 맞나요?")

        - **시나리오 2 [권위의 미묘한 변주]**: 
          단순한 기관 사칭(경찰, 검찰)은 이미 식상합니다. 
          뉴스 내용과 관련된 **제3의 협력 업체, 하청 기관, 혹은 내부 고발자** 등을 사칭하여 의심을 피해가십시오.
          (예: "질병청 역학조사 지원단" 대신 "방역 물품 배송 기사", "금융감독원" 대신 "피해 보상 접수 센터 상담원 김미영")

        - **시나리오 3 [매체 변주 (No-Link Attack)]**: 
          **URL 링크를 포함하지 않는** 스미싱을 설계하십시오. 
          URL이 없으면 사람들은 스미싱이 아니라고 착각합니다. 이를 역이용하여 **"이 번호로 전화나 문자를 달라"**고 유도하거나, 단순히 **"신뢰를 쌓는 1차 미끼 문자"**를 보내십시오.
          (예: "엄마 나 폰 액정 나갔어. 이걸로 답장 줘", "02-1234-5678 (담당자 직통)로 문의 바랍니다")

        - **시나리오 4 [맥락의 재구성 (Hyper-Contextual)]**: 
          뉴스 기사의 아주 구체적인 **"단어(키워드)"나 "숫자", "날짜"**를 인용하여, 마치 해당 사건의 **직접적인 후속 조치**인 것처럼 위장하십시오.
          피해자가 "설마 이것까지 알고 있겠어?"라고 생각하는 순간을 노리십시오.

        [응답 형식]
        - JSON 객체로만 응답하십시오.
        {{
            "scenarios": [
                {{
                    "id": "High-Impact-SCN-XX",
                    "strategy_name": "전략의 핵심을 꿰뚫는 매력적인 이름",
                    "impersonation": "구체적 사칭 대상 (단순 기관명 X, 역할/직급 포함)",
                    "trigger": "사용될 핵심 심리 기제 (예: 인지 부조화, 권위 복종, 희소성 원리 등)",
                    "logic": "피해자의 의심을 무장해제 시키는 치밀한 논리 구조",
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