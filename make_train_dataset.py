import os
import json
import random
from openai import OpenAI
from dotenv import load_dotenv

# 환경 변수 로드 (강제 업데이트)
load_dotenv(override=True)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_messages(count, type="spam"):
    print(f"[*] {type.upper()} 학습 데이터 {count}개 생성 중... (다소 시간이 걸릴 수 있습니다)")
    messages = []
    
    if type == "spam":
        system_prompt = "You are a red team security researcher. Generate diverse and realistic smishing (SMS phishing) messages in Korean."
        user_prompt = f"""
        Generate {count} unique smishing messages. 
        Focus on various scenarios:
        - Impersonation (Gov, Family, Friend, Bank)
        - Urgency (Payment, Accident, Lawsuit)
        - Greed (Crypto, Stock, Lotto, Subsidy)
        - Curiosity (Delivery, Wedding, Obituary)
        
        Output MUST be a JSON object with a single key "messages" containing a list of strings.
        """
    else:
        system_prompt = "You are a helpful assistant generating normal daily SMS messages in Korean."
        user_prompt = f"""
        Generate {count} unique normal SMS messages. 
        They should look natural and safe.
        - Daily coords, Greetings, Appointments
        - Real verification codes, Bank notifications (Real)
        - Delivery updates (Real)
        
        Output MUST be a JSON object with a single key "messages" containing a list of strings.
        """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.9
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
    save_path = os.path.join(save_dir, "train_dataset.json")

    # 1. Spam 생성 (100개)
    spam_msgs = generate_messages(100, "spam")
    
    # 2. Ham 생성 (100개)
    ham_msgs = generate_messages(100, "ham")

    if not spam_msgs or not ham_msgs:
        print("[!] 데이터 생성 실패. API 키를 확인하세요.")
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

    print(f"\n[Success] 학습 데이터셋 생성 완료: {save_path}")
    print(f"    - 총 데이터: {len(final_dataset)}개")

if __name__ == "__main__":
    main()
