import os
import requests
import json
import time
import re
import random
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class NaverApiCrawler:
    def __init__(self):
        # API 인증 정보 (환경 변수)
        self.client_id = os.getenv("NAVER_CLIENT_ID")
        self.client_secret = os.getenv("NAVER_CLIENT_SECRET")
        
        if not self.client_id or not self.client_secret:
            raise ValueError(".env 파일에 NAVER_CLIENT_ID와 SECRET을 설정해주세요.")

        self.base_url = "https://openapi.naver.com/v1/search/news.json"
        
        # 저장 경로 설정 (src 기준 상위의 data 폴더)
        self.save_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

        # 트렌드 분석용 키워드
        self.trend_keywords = {
            "method": ["부고", "청첩장", "택배", "건강검진", "해외결제", "카드개설", "대출", "투자", "알바", "납치", "영상통화", "딥페이크"],
            "target": ["자녀", "딸", "아들", "엄마", "아빠", "친구", "직장상사", "검찰", "경찰", "금융감독원", "은행"],
            "channel": ["카카오톡", "텔레그램", "문자", "SMS", "페이스북", "인스타", "DM"]
        }

    def _get_headers(self):
        return {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
            "Content-Type": "application/json"
        }

    def _determine_type(self, title, content):
        text = (title + " " + content).lower()
        
        # 1. 카테고리별 가중치 키워드 정의
        # 중요도가 높은 단어는 점수를 더 높게 배정할 수 있습니다.
        categories = {
            "DEEPFAKE_AI_SCAM": {
                "keywords": ['딥페이크', '합성', '영상통화', '목소리', '얼굴', '페이스스왑', '생성형 ai'],
                "weight": 1.5
            },
            "GOV_IMPERSONATION": {
                "keywords": ['검찰', '경찰', '금감원', '수사관', '계좌동결', '구속영장', '범죄연루', '검사'],
                "weight": 1.2
            },
            "FAMILY_IMPERSONATION": {
                "keywords": ['가족', '자녀', '딸', '아들', '엄마', '아빠', '납치', '액정파손', '지인사칭'],
                "weight": 1.0
            },
            "INVESTMENT_SCAM": {
                "keywords": ['투자', '코인', '리딩방', '고수익', '공모주', '상장', '수익률', '재테크'],
                "weight": 1.0
            },
            # [신규] 사회/정책적 맥락 (Social Context)
            "POLICY_NEWS": {
                "keywords": ['정책', '지원금', '환급금', '연말정산', '청약', '보조금', '개정', '시행'],
                "weight": 1.1 
            },
            "ECONOMIC_ISSUE": {
                "keywords": ['금리', '물가', '환율', '주식', '비트코인', '폭락', '급등', '경제 위기'],
                "weight": 1.0
            },
            "SOCIAL_EVENT": {
                "keywords": ['명절', '추석', '설날', '블랙프라이데이', '할인', '택배', '휴가', '올림픽', '월드컵'],
                "weight": 1.0
            },
            "LIFESTYLE_SMISHING": {
                "keywords": ['부고', '청첩장', '택배', '건강검진', '배송지', '미납', '과태료'],
                "weight": 0.8
            }
        }

        # 2. 카테고리별 점수 계산
        category_scores = {}
        for cat, info in categories.items():
            # 문장에 포함된 키워드 개수 * 가중치
            score = sum(text.count(kw) for kw in info["keywords"]) * info["weight"]
            category_scores[cat] = score

        # 3. 최상위 카테고리 결정
        max_score = max(category_scores.values())
        
        # 만약 점수가 0이거나 너무 낮으면 일반형으로 분류
        if max_score < 0.5:
            return "GENERAL_CONTEXT" # SCAM이 아닌 일반 Context일 수 있으므로 변경
        
        # 가장 높은 점수를 받은 카테고리 반환
        return max(category_scores, key=category_scores.get)
    
    def analyze_trends(self, data_list):
        analysis_result = {"methods": [], "targets": [], "channels": []}
        all_text = " ".join([d['title'] + " " + (d['content'] if d['content'] else "") for d in data_list])
        for category, keywords in self.trend_keywords.items():
            found_words = []
            for kw in keywords:
                count = all_text.count(kw)
                if count > 0:
                    found_words.append((kw, count))
            analysis_result[category + "s"] = sorted(found_words, key=lambda x: x[1], reverse=True)
        return analysis_result

    def fetch_news(self, keyword, display=100):
        """네이버 OpenAPI를 통해 뉴스 리스트를 가져옵니다."""
        params = {
            "query": keyword,
            "display": display,
            "sort": "date"  # 최신순
        }
        try:
            response = requests.get(self.base_url, headers=self._get_headers(), params=params)
            if response.status_code == 200:
                return response.json().get('items', [])
            else:
                print(f"    [!] API 에러 (상태코드: {response.status_code})")
                return []
        except Exception as e:
            print(f"    [!] 요청 실패: {e}")
            return []

    def run_crawling(self, target_keywords):
        all_results = []
        print(f"[*] 네이버 API 기반 데이터 수집 시작...")

        for kw in target_keywords:
            print(f"    -> 키워드 '{kw}' 수집 중...", end=" ")
            items = self.fetch_news(kw)
            
            for idx, item in enumerate(items):
                # HTML 태그 제거
                title = re.sub('<[^>]*>', '', item['title'])
                description = re.sub('<[^>]*>', '', item['description'])
                
                processed_item = {
                    "id": f"CTX-API-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
                    "type": self._determine_type(title, description),
                    "title": title,
                    "source": "Naver News API",
                    "link": item['originallink'] or item['link'],
                    "content": description,
                    "timestamp": item['pubDate']
                }
                all_results.append(processed_item)
            
            print(f"({len(items)}건 완료)")
            time.sleep(0.1) # API 쿼터 보호

        # 링크 기준 중복 제거
        unique_dict = {v['link']: v for v in all_results}
        return list(unique_dict.values())

    def save_for_scenario_generation(self, data, filename="smishing_context_data.jsonl"):
        file_path = os.path.join(self.save_dir, filename)
        
        # 카테고리별 전문 공격 전략 정의
        attack_strategies = {
            "DEEPFAKE_AI_SCAM": {
                "logic": "1. 지인의 음성/얼굴 특징 언급 2. 확인 불가능한 긴급 상황 설정 3. 송금이나 개인정보 탈취가 아닌 '앱 설치' 유도",
                "target_emotion": "극심한 당혹감/공포",
                "cta": "가족 확인용 앱 설치"
            },
            "GOV_IMPERSONATION": {
                "logic": "1. 실제 법령/공문서 번호 언급 2. 법적 불이익(구속, 압류) 경고 3. 공식 웹사이트와 흡사한 피싱 도메인 활용",
                "target_emotion": "법적 압박/권위에 대한 복종",
                "cta": "전자고지서 확인"
            },
            "FAMILY_IMPERSONATION": {
                "logic": "1. 액정 파손/분실 등 일상적 사고 설정 2. 전화 통화가 불가능한 상황(회의 중 등) 강조 3. 원격 제어 앱 설치 유도",
                "target_emotion": "가족에 대한 걱정/안도감 유도",
                "cta": "원격 지원 링크 클릭"
            },
            "INVESTMENT_SCAM": {
                "logic": "1. 유명 투자 전문가 사칭 2. 손실 복구 제안 또는 선착순 정보 강조 3. 텔레그램/카카오톡 오픈채팅방 유입",
                "target_emotion": "조급함/보상 기대(탐욕)",
                "cta": "비공개 정보방 입장"
            },
            "LIFESTYLE_SMISHING": {
                "logic": "1. 생활 밀착형(택배, 부고, 범칙금) 키워드 활용 2. 마감 임박 또는 반송 예정 등 행동 촉구 3. 본인 인증 절차 위장",
                "target_emotion": "일상적 불편함 해결 욕구/호기심",
                "cta": "상세 주소지 확인"
            },
            # [신규 전략] 사회적 맥락 악용
            "POLICY_NEWS": {
                "logic": "1. '신청 마감' 또는 '지급 대상 선정' 강조 2. 복잡한 정책을 쉽게 해결해주는 척 접근 3. 가짜 정부 신청 페이지 유도",
                "target_emotion": "혜택 상실에 대한 불안/기대감",
                "cta": "지원금 조회/신청하기"
            },
            "ECONOMIC_ISSUE": {
                "logic": "1. 경제 위기/하락장을 틈탄 '안전 자산' 또는 '손실 만회' 제안 2. '긴급 정보'라며 희소성 강조",
                "target_emotion": "경제적 불안감/손실 회피 본능",
                "cta": "긴급 대응 리포트 확인"
            },
            "SOCIAL_EVENT": {
                "logic": "1. 시즌 특수(명절 선물, 할인 등)를 가장한 배송/이벤트 당첨 문자 2. '물량 소진 임박' 등 시간 제한 설정",
                "target_emotion": "들뜬 분위기 속의 방심/호기심",
                "cta": "배송지 입력/쿠폰 받기"
            }
        }

        with open(file_path, "w", encoding="utf-8") as f:
            for item in data:
                # 분류된 타입에 맞는 전략 선택 (없으면 일반형)
                strat = attack_strategies.get(item['type'], {
                    "logic": "1. 긴급한 상황 설정 2. 심리적 압박 3. 클릭 유도",
                    "target_emotion": "일반적 호기심/불안",
                    "cta": "확인 링크"
                })

                training_entry = {
                    "context": {
                        "news_title": item['title'],
                        "category": item['type'],
                        "source_date": item['timestamp']
                    },
                    "attack_design": {
                        "instruction": f"제공된 '{item['type']}' 기사(사회적 맥락)를 분석하여, 이를 악용하는 지능형 스미싱 시나리오를 설계하라.",
                        "strategy_logic": strat["logic"],
                        "target_emotion": strat["target_emotion"],
                        "call_to_action": strat["cta"],
                        "scenario_rules": [
                            "최대한 정중하거나 공식적인 말투를 사용할 것",
                            "피해자가 의심할 틈을 주지 않는 구체적인 상황을 설정할 것",
                            "가짜 URL은 식별이 어렵도록 단축 URL이나 유사 도메인을 사용할 것"
                        ]
                    },
                    "raw_text": item['content']
                }
                f.write(json.dumps(training_entry, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    crawler = NaverApiCrawler()
    
    target_keywords = [
        # 1. 기존 범죄 키워드
        "스미싱 부고장", "택배 주소지 확인 문자", "건강검진 결과 조회 사기",
        "민생회복지원금 사기문자", "교통범칙금 과태료 스미싱", "국세청 환급금 문자",
        "해외결제 승인 스미싱", "카드 발급 확인 문자 사기", "저금리 대환대출 스미싱",
        "딥페이크 지인 합성 사기", "영상통화 몸캠 피싱", "AI 목소리 사칭 피싱",
        "자녀 사칭 메신저 피싱", "부모님 휴대폰 파손 사기",
        
        # 2. [신규] 사회 중립적 키워드 (잠재적 공격 재료)
        "2025년 달라지는 정책", "소상공인 지원금 신청 방법", "청년 월세 지원 대상",
        "건강보험료 환급금 조회", "연말정산 미리보기 서비스", "아파트 청약 일정",
        "명절 기차표 예매 일정", "블랙프라이데이 세일 정보"
    ]

    # 데이터 수집 실행
    final_list = crawler.run_crawling(target_keywords)

    # 분석 보고서
    trend_report = crawler.analyze_trends(final_list)
    print("\n" + "="*50)
    print(f"총 수집 데이터: {len(final_list)}건")
    print(f"주요 수법 트렌드 (TOP 5): {trend_report['methods'][:5]}")
    print("="*50)

    # Raw Data 저장
    raw_path = os.path.join(crawler.save_dir, "scam_news_api_raw.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(final_list, f, ensure_ascii=False, indent=4)
    
    # 시나리오 생성용 JSONL 저장
    crawler.save_for_scenario_generation(final_list)
    print(f"\n[Success] 모든 데이터가 {crawler.save_dir} 폴더에 저장되었습니다.")