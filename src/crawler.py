import os
import requests
import json
import time
import re
import random
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import feedparser
import urllib.parse

# 환경 변수 로드
load_dotenv()

class GoogleNewsRssCrawler:
    """구글 뉴스 RSS를 통해 위협 정보를 수집합니다. (시스템 아키텍처 사양)"""
    def __init__(self):
        # [개선] 데이터 파일 저장 경로를 절대 경로로 고정 (Persistence 보장)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.save_dir = os.path.abspath(os.path.join(current_dir, "..", "data"))
        # 구글 뉴스 섹션별 RSS URL
        self.sections = {
            "TOP_STORIES": "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko",
            "BUSINESS": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ko&gl=KR&ceid=KR:ko",
            "SOCIETY": "https://news.google.com/rss/headlines/section/topic/SOCIETY?hl=ko&gl=KR&ceid=KR:ko"
        }

    def fetch_section(self, section_key):
        url = self.sections.get(section_key)
        if not url: return []
        
        try:
            feed = feedparser.parse(url)
            results = []
            for entry in feed.entries:
                # RSS 데이터 정규화
                item = {
                    "title": entry.title,
                    "link": entry.link,
                    "description": entry.get('summary', ''),
                    "pubDate": entry.get('published', datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0900'))
                }
                results.append(item)
            return results
        except Exception as e:
            print(f"    [!] Google RSS ({section_key}) 에러: {e}")
            return []

    def fetch_news(self, keyword):
        # 기존 키워드 검색기능 (하위 호환성 유지)
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(keyword)}&hl=ko&gl=KR&ceid=KR:ko"

class NaverApiCrawler:
    def __init__(self):
        # API 인증 정보 (환경 변수)
        self.client_id = os.getenv("NAVER_CLIENT_ID")
        self.client_secret = os.getenv("NAVER_CLIENT_SECRET")
        
        if not self.client_id or not self.client_secret:
            raise ValueError(".env 파일에 NAVER_CLIENT_ID와 SECRET을 설정해주세요.")

        self.base_url = "https://openapi.naver.com/v1/search/news.json"
        
        # [개선] 데이터 파일 저장 경로를 절대 경로로 고정 (Persistence 보장)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.save_dir = os.path.abspath(os.path.join(current_dir, "..", "data"))
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)


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

    def _fetch_full_content(self, url):
        """기사 링크에서 전문을 크롤링합니다."""
        if not url or url.startswith("javascript:"):
            return None
            
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            # allow_redirects=True는 구글 뉴스 RSS 등 리다이렉트 링크 해결을 위함
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            if response.status_code != 200:
                return None
            
            # 리다이렉트된 최종 URL로 업데이트 (셀렉터 판별용)
            final_url = response.url
                
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 1. 사이트별 최적화 셀렉터
            if "news.naver.com" in final_url:
                content = soup.select_one("#dic_area") or soup.select_one("#articleBodyContents")
            elif "chosun.com" in final_url:
                content = soup.select_one(".article-body") or soup.select_one("#news_body_id")
            elif "joins.com" in final_url or "joongang.co.kr" in final_url:
                content = soup.select_one("#article_body") or soup.select_one(".article_body")
            else:
                # 2. 범용 기사 본문 셀렉터 (Heuristics 강화)
                content = (soup.find('article') or 
                          soup.find('div', class_=re.compile(r'article_body|news_end|view_content|art_body|news_text|viewer|news_body')) or
                          soup.find('div', id=re.compile(r'articleBody|news_content|art_body|news_text|viewer')))
            
            # 3. 스마트 폴백: 위 셀렉터로 못찾았을 경우 모든 p 태그 수집
            if not content:
                p_tags = soup.find_all('p')
                if len(p_tags) > 3: # 최소 3개 이상의 문단이 있어야 기사로 간주
                    text = " ".join([p.get_text().strip() for p in p_tags if len(p.get_text().strip()) > 20])
                    if len(text) > 200:
                        return self._sanitize_text(text)

            if content:
                # 불필요한 요소 제거
                for s in content(['script', 'style', 'iframe', 'header', 'footer', 'button', 'nav']):
                    s.decompose()
                
                text = content.get_text(separator=' ', strip=True)
                return self._sanitize_text(text)
            
            return None
        except Exception as e:
            return None

    def _sanitize_text(self, text):
        """저장용 텍스트 정제 (줄바꿈 제거 등)"""
        if not text: return None
        # 모든 줄바꿈 및 연속 공백 정제 (JSONL 안정성 확보)
        text = re.sub(r'[\r\n\t]+', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text if len(text) > 100 else None

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

    def run_crawling(self, target_keywords, fetch_full=False):
        all_results = []
        print(f"[*] 네이버 API 기반 데이터 수집 시작 (Full-Text: {fetch_full})...")

        for kw in target_keywords:
            print(f"    -> 키워드 '{kw}' 수집 중...", end=" ")
            items = self.fetch_news(kw)
            
            for idx, item in enumerate(items):
                # HTML 태그 제거
                title = re.sub('<[^>]*>', '', item['title'])
                description = re.sub('<[^>]*>', '', item['description'])
                link = item['originallink'] or item['link']
                
                # [고도화] 하이브리드: 필요시에만 전문 크롤링 (기본은 API 요약만)
                content = description
                if fetch_full:
                    full_content = self._fetch_full_content(link)
                    if full_content:
                        content = full_content
                
                processed_item = {
                    "id": f"CTX-API-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
                    "type": self._determine_type(title, content),
                    "title": title,
                    "source": "Naver News API" + (" + Full Text" if fetch_full else ""),
                    "link": link,
                    "content": content,
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

        # [수정] 증분 저장 로직 (Incremental Merge) - 중복 체크 강화
        existing_data = []
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            existing_data.append(json.loads(line))
            except Exception as e:
                print(f"[!] 기존 데이터 로드 중 오류: {e}")

        # 기존 데이터의 URL과 제목(정규화)을 집합으로 관리
        def normalize_title(title):
            return re.sub(r'\s+', '', title).strip()

        existing_urls = {entry['context'].get('link') for entry in existing_data if entry['context'].get('link')}
        existing_titles = {normalize_title(entry['context']['news_title']) for entry in existing_data}
        
        all_entries = existing_data
        new_count = 0
        
        for item in data:
            norm_title = normalize_title(item['title'])
            # URL 또는 제목이 이미 존재하면 스킵
            if item['link'] in existing_urls or norm_title in existing_titles:
                continue
                
            strat = attack_strategies.get(item['type'], {
                "logic": "1. 긴급한 상황 설정 2. 심리적 압박 3. 클릭 유도",
                "target_emotion": "일반적 호기심/불안",
                "cta": "확인 링크"
            })

            training_entry = {
                "context": {
                    "news_title": item['title'],
                    "category": item['type'],
                    "source_date": item['timestamp'],
                    "link": item['link']
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
            all_entries.append(training_entry)
            existing_urls.add(item['link'])
            existing_titles.add(norm_title)
            new_count += 1

        # 최종 저장 (시간순 정렬 시도 - 선택사항)
        try:
            # pubDate 파싱이 까다로우면 생략 가능하지만, 가독성을 위해 정렬 권장
            from email.utils import parsedate_to_datetime
            def get_dt(x):
                try: return parsedate_to_datetime(x['context']['source_date'])
                except: return datetime.min
            all_entries.sort(key=get_dt, reverse=True)
        except:
            pass

        with open(file_path, "w", encoding="utf-8") as f:
            for entry in all_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        
        print(f"[*] 데이터 동기화 완료: 신규 {new_count}건 추가 (총 {len(all_entries)}건)")
        return new_count

def run_crawling(fetch_full=False):
    """앱 대시보드 및 서비스에서 호출할 공용 크롤링 진입점"""
    # 1. 아키텍처 표준: Google News RSS (Section-based Trending)
    google_crawler = GoogleNewsRssCrawler()
    # 2. 보조 소스: Naver API (Keyword-based)
    naver_crawler = NaverApiCrawler()
    
    # 사회적 맥락 파악을 위한 주요 토픽 (RSS가 메인이며, 이들은 보조 검색용)
    social_context_keywords = [
        "민생회복지원금", "2026년 달라지는 정책", "건강보험 환급금", 
        "국민연금 개혁", "아파트 청약 일정", "소상공인 지원 사업"
    ]

    total_gathered = []

    # [Priority 1] Google News TRENDING 섹션 수집
    print(f"[*] [Google News RSS] 트렌드 데이터 수집 시작...")
    for section in ["TOP_STORIES", "BUSINESS", "SOCIETY"]:
        print(f"    -> 섹션 '{section}' 수집 중...", end=" ")
        items = google_crawler.fetch_section(section)
        
        for item in items:
            title = re.sub('<[^>]*>', '', item['title']).replace("\n", " ").replace("\r", " ").strip()
            description = re.sub('<[^>]*>', '', item['description']).replace("\n", " ").replace("\r", " ").strip()
            link = item['link']
            
            content = description
            if fetch_full:
                full_text = naver_crawler._fetch_full_content(link)
                if full_text: content = full_text

            processed = {
                "id": f"CTX-GSS-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
                "type": naver_crawler._determine_type(title, content),
                "title": title,
                "source": f"Google News RSS ({section})" + (" + Full Text" if fetch_full else ""),
                "link": link,
                "content": content,
                "timestamp": item['pubDate']
            }
            total_gathered.append(processed)
        print(f"({len(items)}건 완료)")

    # [Priority 2] Naver API 보조 수집
    print(f"[*] [Naver News API] 보조 수집 시작...")
    naver_results = naver_crawler.run_crawling(social_context_keywords, fetch_full=fetch_full)
    total_gathered.extend(naver_results)

    # 링크 기준 중복 제거
    unique_dict = {v['link']: v for v in total_gathered}
    final_gathered = list(unique_dict.values())

    # 분석 및 저장 (Incremental Merge 포함)
    new_count = naver_crawler.save_for_scenario_generation(final_gathered)
    
    # Raw JSON 저장 (최신 기준)
    raw_path = os.path.join(naver_crawler.save_dir, "scam_news_api_raw.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(final_gathered, f, ensure_ascii=False, indent=4)
        
    return new_count, len(final_gathered)

def fetch_full_content(url):
    """단일 기사의 전문을 수집하는 전역 함수 (On-Demand)"""
    crawler = NaverApiCrawler()
    return crawler._fetch_full_content(url)

if __name__ == "__main__":
    results = run_crawling(fetch_full=True) # 로컬 실행 시에는 전문 수집
    print(f"\n[Success] 데이터 수집 및 증분 저장이 완료되었습니다.")