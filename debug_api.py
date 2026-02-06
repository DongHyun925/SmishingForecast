import os
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

print("=== DEBUG START ===")

# 1. 실제 파일 내용 확인
try:
    with open(".env", "r", encoding="utf-8") as f:
        content = f.read()
        print(f"[File Content Preview]:\n{content}")
except Exception as e:
    print(f"[!] Error reading .env file: {e}")

# 2. 환경 변수 로드 (강제 오버라이드)
# 기존 환경 변수에 잘못된 키가 캐싱되어 있을 수 있으므로 override=True 필수
load_dotenv(override=True)

# 3. API Key 확인
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("\n[!] Error: OPENAI_API_KEY env var is Empty.")
else:
    # 키의 앞뒤만 출력
    masked_key = api_key[:10] + "..." + api_key[-10:]
    print(f"\n[Loaded Key]: {masked_key}")
    print(f"[Key Length]: {len(api_key)}")

# 4. API 호출 테스트
print("\n[API Test] Connecting to OpenAI...")
try:
    client = OpenAI(api_key=api_key)
    client.models.list()
    print("   [Success] API connection verified!")
except Exception as e:
    print(f"   [Fail] API connection failed: {e}")

print("=== DEBUG END ===")
