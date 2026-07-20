import json
import os

def convert():
    base_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    db_file = os.path.join(base_dir, "questions_bank.json")
    js_file = os.path.join(base_dir, "questions_data.js")
    
    with open(db_file, "r", encoding="utf-8") as f:
        db = json.load(f)
        
    js_content = f"const QUESTIONS_DATA = {json.dumps(db, ensure_ascii=False, indent=2)};"
    
    with open(js_file, "w", encoding="utf-8") as f:
        f.write(js_content)
        
    print("Successfully converted questions_bank.json to questions_data.js!")

if __name__ == "__main__":
    convert()
