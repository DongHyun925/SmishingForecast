import json
import csv
import os

def convert_to_csv():
    json_path = os.path.join("data", "test_dataset.json")
    csv_path = os.path.join("data", "test_dataset.csv")

    if not os.path.exists(json_path):
        print(f"[!] Error: File not found {json_path}")
        return

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"[*] Loaded {len(data)} items from JSON.")

        # Write to CSV with utf-8-sig for Excel compatibility in Korea
        with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            # Header
            writer.writerow(["label", "text"])
            
            for item in data:
                # Map label to readable string if desired, or keep as int. 
                # User asked for "sentences", let's provide clear labels.
                label_str = "smishing" if item['label'] == 1 else "normal"
                writer.writerow([label_str, item['text']])
                
        print(f"[Success] Converted to CSV: {csv_path}")

    except Exception as e:
        print(f"[!] Conversion failed: {e}")

if __name__ == "__main__":
    convert_to_csv()
