import openai
import json
import os
from dotenv import load_dotenv

load_dotenv()

class IntentAnalyzer:
    def __init__(self, api_key=None):
        self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.bank_path = os.path.join(os.path.dirname(__file__), "../data/scenario_bank.json")
        self._load_bank()

    def _load_bank(self):
        with open(self.bank_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
            self.scenario_bank = self.data["scenarios"]

    def _update_bank(self, new_scenario):
        """새로운 시나리오를 JSON 파일에 영구적으로 추가합니다."""
        self.scenario_bank.append(new_scenario)
        with open(self.bank_path, "w", encoding="utf-8") as f:
            json.dump({"scenarios": self.scenario_bank}, f, indent=4, ensure_ascii=False)
        print(f"[*] 신규 공격 의도 등록 완료: {new_scenario['intent_name']}")

    def analyze_intent(self, attack_message):
        bank_info = "\n".join([f"- {s['intent_id']}: {s['intent_name']} ({s['description']})" for s in self.scenario_bank])

        prompt = f"""
        당신은 사이버 범죄 심리 및 법률 전문가로 구성된 '지능형 위협 프로파일링 엔진'입니다. 
        입력된 스미싱 문자를 분석하여 기존 시나리오 뱅크와 대조하고, 해당 공격의 위협 수위를 다각도로 평가하십시오.

        [1. 기존 시나리오 뱅크]
        {bank_info}

        [2. 분석 대상 문자]
        "{attack_message}"

        [3. 프로파일링 지시 사항]
        - **의도 식별**: 기존 뱅크에 매칭되는 항목이 없다면 'NEW'로 표시하고 신규 정의하십시오.
        - **위협 등급(Severity)**: 피해 규모, 개인정보 탈취 정도, 심리적 압박 강도를 고려하여 1(낮음)~5(치명적)점으로 평가하십시오.
        - **법적 위험성(Legal Risk)**: 해당 공격이 성립될 경우 적용 가능한 실제 법률(예: 정보통신망법, 형법상 사기, 공무원자격사칭 등)을 명시하십시오.
        - **기술적 특징**: 가짜 URL, 악성 앱 설치 유도, 원격 제어 등 사용된 기술적 수법을 요약하십시오.

        [4. 응답 형식 (JSON 전용)]
        {{
            "matched_intent_id": "ID 또는 NEW",
            "intent_name": "수법 명칭",
            "description": "수법 상세 설명",
            "severity_score": 1~5,
            "legal_risks": ["적용 법률 1", "적용 법률 2"],
            "threat_level": "Low/Medium/High/Critical",
            "reason": "프로파일링 근거"
        }}
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 디지털 포렌식 및 사이버 범죄 수사 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        
        result = json.loads(response.choices[0].message.content)

        # 신종 수법 등록 시 새로운 필드들도 함께 저장되도록 보완
        if result['matched_intent_id'] == "NEW":
            new_id = f"NEW-{len(self.scenario_bank) + 1:02d}"
            new_entry = {
                "intent_id": new_id,
                "intent_name": result['intent_name'],
                "description": result['description'],
                "severity_score": result['severity_score'],
                "legal_risks": result['legal_risks'],
                "registered_at": "2026-02-02" # 동적 날짜 권장
            }
            self._update_bank(new_entry)
            result['matched_intent_id'] = new_id
            
        return result
    

if __name__ == "__main__":
    # 1. 초기화
    analyzer = IntentAnalyzer()

    # 테스트용 데이터 세트
    test_messages = [
        # 케이스 1: 기존 수법과 유사한 메시지 (예: 공공기관 사칭)
        "[대검찰청] 귀하의 명의가 도용된 사건번호(2025-고단1234)와 관련하여 공문서를 확인바랍니다. bit.ly/prosecutor-check",
        
        # 케이스 2: 새로운 수법 (예: 최근 유행하는 부고장/청첩장 스미싱 등 뱅크에 없다면)
        "[모바일부고] 장례식장 안내 및 마음 전하실 곳 조회하기: https://funeral-info.co.kr/1239"
    ]

    print("[*] 지능형 위협 프로파일링 테스트 시작...")
    print("=" * 60)

    for i, msg in enumerate(test_messages):
        print(f"\n[Test {i+1}] 분석 대상 문자: {msg}")
        
        # 분석 실행
        analysis_result = analyzer.analyze_intent(msg)
        
        # 결과 출력
        print(f" ▸ 매칭된 ID: {analysis_result['matched_intent_id']}")
        print(f" ▸ 수법 명칭: {analysis_result['intent_name']}")
        print(f" ▸ 수법 상세설명: {analysis_result['description']}")
        print(f" ▸ 위협 등급: {analysis_result['threat_level']} (Score: {analysis_result['severity_score']}/5)")
        print(f" ▸ 적용 법률: {', '.join(analysis_result['legal_risks'])}")
        print(f" ▸ 분석 근거: {analysis_result['reason']}")
        print("-" * 60)

    print("\n[*] 모든 테스트 및 시나리오 뱅크 업데이트가 완료되었습니다.")