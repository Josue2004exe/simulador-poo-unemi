import json
import os
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def check_duplicates():
    db_file = os.path.join(os.path.dirname(__file__), "..", "data", "questions_bank.json")
    with open(db_file, "r", encoding="utf-8") as f:
        db = json.load(f)
        
    questions = db["preguntas"]
    print(f"Total questions to check: {len(questions)}")
    
    # 1. Check exact matches in text snippet (ignoring spaces/case)
    exact_duplicates = {}
    for idx, q in enumerate(questions):
        text_clean = "".join(q["text_snippet"].split()).lower()
        if text_clean in exact_duplicates:
            exact_duplicates[text_clean].append(idx)
        else:
            exact_duplicates[text_clean] = [idx]
            
    exact_dup_count = 0
    for text, indices in exact_duplicates.items():
        if len(indices) > 1:
            exact_dup_count += 1
            print(f"\n[EXACT DUP DETECTED] {len(indices)} questions have the exact same text:")
            for idx in indices:
                print(f"  - Index {idx}, ID: {questions[idx]['id'][:8]}..., Snippet: {questions[idx]['text_snippet'][:100]}")
                
    # 2. Check high similarity fuzzy matching (threshold > 85% similarity)
    print("\nRunning fuzzy matching check (similarity > 85%)...")
    fuzzy_dup_count = 0
    for i in range(len(questions)):
        for j in range(i + 1, len(questions)):
            sim = similarity(questions[i]["text_snippet"], questions[j]["text_snippet"])
            if sim > 0.85:
                # Also verify options are similar
                opt_sim = similarity(" ".join(questions[i]["options"]), " ".join(questions[j]["options"]))
                if opt_sim > 0.80:
                    fuzzy_dup_count += 1
                    print(f"\n[FUZZY DUP DETECTED] Similarity: {sim*100:.1f}%, Options Similarity: {opt_sim*100:.1f}%")
                    print(f"  - Q1 (Index {i}, ID {questions[i]['id'][:8]}...): {questions[i]['text_snippet'][:120]}")
                    print(f"  - Q2 (Index {j}, ID {questions[j]['id'][:8]}...): {questions[j]['text_snippet'][:120]}")

    print(f"\nScan complete. Exact duplicates groups found: {exact_dup_count}. Fuzzy duplicates pairs found: {fuzzy_dup_count}.")

if __name__ == "__main__":
    check_duplicates()
