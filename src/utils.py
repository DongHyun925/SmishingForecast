import json
import os

def load_jsonl(file_path):
    """
    JSONL 파일을 읽어서 딕셔너리 리스트로 반환합니다.
    """
    data = []
    if not os.path.exists(file_path):
        print(f"[!] 파일을 찾을 수 없습니다: {file_path}")
        return data

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return data

def save_json(data, file_path):
    """
    데이터를 JSON 형식으로 저장합니다.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)