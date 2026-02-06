import os
import json
import random
from openai import OpenAI
from dotenv import load_dotenv

# 환경 변수 로드 (강제 업데이트)
load_dotenv(override=True)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_messages(count, type="spam"):
    print(f"[*] {type.upper()} 메시지 {count}개 생성 중...")
    messages = []
    
    if type == "spam":
        system_prompt = "You are a red team security researcher. Generate sophisticated smishing (SMS phishing) messages in Korean."
        user_prompt = f"""
        Generate {count} unique smishing messages. 
        Focus on high-quality, realistic attacks.
        Include a variety of types:
        1. Government impersonation (Police, Prosecution, KCDC)
        2. Family impersonation (Broken phone, Urgent money request)
        3. Financial scams (Low interest loan, Card approval, Crypto investment)
        4. Lifestyle scams (Delivery, Wedding invitation, Obituary, Traffic fine)
        
        Output MUST be a JSON object with a single key "messages" containing a list of strings.
        Example: {{"messages": ["msg1", "msg2"]}}
        """
    else:
        system_prompt = "You are a helpful assistant generating normal daily SMS messages in Korean."
        user_prompt = f"""
        Generate {count} unique normal, daily life SMS messages. 
        They should look similar to smishing but be legitimate (Ham).
        Include:
        1. Real delivery notifications (Courier arrived)
        2. Authentication codes (2FA)
        3. Real friend/family conversations (Casual greetings, Appointments)
        4. Real Card approval alerts (Samsung Card, Shinhan Card etc)
        5. Booking confirmations (Restaurant, Hospital)
        
        Output MUST be a JSON object with a single key "messages" containing a list of strings.
        Example: {{"messages": ["msg1", "msg2"]}}
        """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.8
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        messages = data.get("messages", [])
        
    except Exception as e:
        print(f"    [!] 생성 중 오류 발생: {e}")
        
    return messages

def main():
    # 데이터 저장 경로
    save_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    save_path = os.path.join(save_dir, "test_dataset.json")

    # 1. Spam 생성 (50개)
    spam_msgs = generate_messages(50, "spam")
    
    # 2. Ham 생성 (50개)
    ham_msgs = generate_messages(50, "ham")

    if not spam_msgs or not ham_msgs:
        print("[!] 데이터 생성 실패. API 키나 네트워크를 확인하세요.")
        return

    # 3. 데이터 통합 및 포맷팅
    final_dataset = []
    
    for msg in spam_msgs:
        final_dataset.append({"text": msg, "label": 1}) # 1 = Smishing
        
    for msg in ham_msgs:
        final_dataset.append({"text": msg, "label": 0}) # 0 = Normal

    # 4. 셔플
    random.shuffle(final_dataset)

    # 5. 저장
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(final_dataset, f, ensure_ascii=False, indent=4)

    print(f"\n[Success] 테스트 데이터셋 생성 완료: {save_path}")
    print(f"    - 총 데이터: {len(final_dataset)}개 (Spam: {len(spam_msgs)}, Ham: {len(ham_msgs)})")
    print(f"    - 예시 (Spam): {spam_msgs[0]}")
    print(f"    - 예시 (Ham): {ham_msgs[0]}")

if __name__ == "__main__":
    main()
