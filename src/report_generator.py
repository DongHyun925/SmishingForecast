import openai
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from fpdf import FPDF

load_dotenv(override=True)

class PDFReport(FPDF):
    def header(self):
        # 헤더: 기관명 느낌의 로고 텍스트
        self.set_font('NanumGothic', 'B', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, '자율 대응형 지능형 스미싱 방어 시스템 (AISDS) - 공식 보안 권고문', 0, 1, 'R')
        self.ln(5)

    def footer(self):
        # 푸터: 페이지 번호
        self.set_y(-15)
        self.set_font('NanumGothic', '', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

class SecurityReportGenerator:
    def __init__(self, api_key=None):
        self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self._ensure_font()

    def _ensure_font(self):
        """한글 폰트(나눔고딕)가 없으면 다운로드합니다."""
        font_dir = "assets/fonts"
        if not os.path.exists(font_dir):
            os.makedirs(font_dir)
        
        self.font_path = os.path.join(font_dir, "NanumGothic.ttf")
        if not os.path.exists(self.font_path):
            print("[*] 나눔고딕 폰트 다운로드 중...")
            url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
            response = requests.get(url)
            with open(self.font_path, "wb") as f:
                f.write(response.content)
            print("[*] 폰트 다운로드 완료.")

    def generate_report_content(self, news_item, attack_info, analysis_result):
        """GPT-4o를 이용해 리포트 내용을 생성합니다."""
        news_title = news_item['context'].get('news_title', '제목 미상')
        news_summary = news_item.get('raw_text', '')[:300]
        
        strategy_name = attack_info['strategy'].get('strategy_name', '알 수 없음')
        impersonation = attack_info['strategy'].get('impersonation', '알 수 없음')
        attack_msg = attack_info['message']
        
        risk_score = analysis_result.get('severity_score', 0)
        threat_level = analysis_result.get('threat_level', 'Unknown')
        intent_name = analysis_result.get('intent_name', '미분류')

        prompt = f"""
        당신은 국가 사이버 보안 센터의 수석 분석관입니다.
        아래 제공된 정보를 바탕으로, 대국민 경보를 위한 **[긴급 스미싱 보안 리포트]**를 작성하십시오.
        
        [분석 대상 데이터]
        1. **사회적 맥락(뉴스)**: {news_title}
           - 내용 요약: {news_summary}...
        2. **식별된 공격 수법**:
           - 전략명: {strategy_name}
           - 사칭 대상: {impersonation}
           - 공격 문자 내용: "{attack_msg}"
        3. **위험도 분석 결과**:
           - 분류: {intent_name}
           - 위협 등급: {threat_level} (점수: {risk_score}/5)

        [리포트 작성 지침]
        - **문서 형식**: 정부 기관의 공식 공문 스타일.
        - **섹션 구분**:
           1. **개요 (Executive Summary)**: 뉴스 이슈와 결합된 스미싱 등장 배경을 한 문단으로 요약.
           2. **상세 분석 (Detailed Analysis)**: 공격자가 사용한 심리적 트리거와 문구의 특징 분석.
           3. **위험성 평가 (Risk Assessment)**: 피해 예상 규모 및 위험도.
           4. **대응 수칙 (Action Items)**: 구체적인 예방 및 대응 방법 3~4가지.
        
        결과물은 마크다운이나 특수문자 없이, 섹션 제목과 본문 내용이 명확히 구분되는 **줄글 텍스트**로 작성하십시오.
        (섹션 제목 앞에는 '## ' 같은 마크다운 쓰지 말고, [개요], [상세 분석] 처럼 대괄호를 사용해 구분하세요.)
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "당신은 정보보안 전문 분석가입니다. 공식적이고 전문적인 어조를 사용하십시오."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"리포트 내용 생성 실패: {str(e)}"

    def create_pdf_report(self, content_text):
        """텍스트 내용을 바탕으로 PDF 파일을 생성하고 바이트를 반환합니다."""
        # A4: 210 x 297 mm
        pdf = PDFReport(orientation='P', unit='mm', format='A4')
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_margins(15, 15, 15)  # Left, Top, Right
        
        # fpdf2에서는 uni=True가 default이거나 불필요할 수 있음
        pdf.add_font('NanumGothic', '', self.font_path)
        pdf.add_font('NanumGothic', 'B', self.font_path)
        
        pdf.add_page()
        
        # 1. 문서 제목
        pdf.set_font('NanumGothic', 'B', 24)
        pdf.cell(0, 20, '긴급 사이버 위협 분석 리포트', align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
        
        # 2. 문서 정보 박스
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font('NanumGothic', '', 10)
        today = datetime.now().strftime('%Y년 %m월 %d일')
        pdf.cell(0, 10, f' 발간일: {today}   |   발신: 자율 대응형 방어 시스템 (AISDS)   |   수신: 대한민국 국민 전체', align='C', fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)
        
        # 3. 본문 파싱 및 출력
        lines = content_text.split('\n')
        pdf.set_font('NanumGothic', '', 11)
        
        # 유효 너비 계산 (A4 width 210 - margins 30 = 180)
        effective_width = 180
        
        for line in lines:
            line = line.strip()
            if not line:
                pdf.ln(2)
                continue
            
            # 섹션 제목 감지 (대괄호로 감싸진 경우)
            if line.startswith('[') and line.endswith(']'):
                pdf.ln(5)
                pdf.set_font('NanumGothic', 'B', 14)
                pdf.set_text_color(0, 51, 102) # 남색 계열
                pdf.cell(0, 10, line.replace('[', '').replace(']', ''), align='L', new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(0, 0, 0)
                pdf.set_font('NanumGothic', '', 11)
            else:
                # 일반 본문
                # multi_cell 사용 시 너비 명시
                pdf.multi_cell(effective_width, 6, line, new_x="LMARGIN", new_y="NEXT")
        
        # 4. 하단 경고문
        pdf.ln(10)
        pdf.set_text_color(200, 50, 50) # 붉은색
        pdf.set_font('NanumGothic', 'B', 10)
        pdf.cell(0, 10, '※ 본 리포트는 AI 시뮬레이션 결과이며, 실제 발생한 사건과 다를 수 있습니다.', align='C', new_x="LMARGIN", new_y="NEXT")

        # bytes로 반환
        return bytes(pdf.output())

if __name__ == "__main__":
    gen = SecurityReportGenerator()
    print("[*] PDF 리포트 생성기 준비 완료")
