import os
import re
import json
import hashlib
import time
from playwright.sync_api import sync_playwright

USERNAME = "fmoralesp3"
PASSWORD = "H4CKER2019f"
REVIEW_URL = "https://aulagradoa.unemi.edu.ec/mod/quiz/review.php?attempt=168318&cmid=105494"
DB_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "questions_bank.json")
DEBUG_DIR = os.path.join(os.path.dirname(__file__), "..", "debug")

def clean_text(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = " ".join(text.split())
    return text.strip()

def generate_hash(qtext, options):
    cleaned_options = [clean_text(opt) for opt in options]
    sorted_opts = sorted(cleaned_options)
    hash_input = clean_text(qtext) + "|" + "|".join(sorted_opts)
    return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()

def extract_review_questions():
    print("Loading existing database...")
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
    else:
        db = {"preguntas": []}
        
    existing_hashes = {q["id"] for q in db["preguntas"]}
    print(f"Loaded {len(existing_hashes)} existing questions.")

    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1280, "height": 1000})
        page = context.new_page()

        try:
            print("Navigating to Moodle review page...")
            page.goto(REVIEW_URL)
            page.wait_for_load_state("load")
            
            if "login" in page.url or page.locator("input[name='username']").is_visible():
                print("Logging in...")
                page.fill("input[name='username']", USERNAME)
                page.fill("input[name='password']", PASSWORD)
                page.click("#loginbtn")
                page.wait_for_load_state("load")
                
                if REVIEW_URL not in page.url:
                    page.goto(REVIEW_URL)
                    page.wait_for_load_state("load")
            
            print(f"Landed on: {page.url}")
            time.sleep(3)
            
            # Find all question blocks (.que)
            q_elements = page.locator(".que").all()
            print(f"Found {len(q_elements)} questions to process.")
            
            new_questions_count = 0
            
            for idx, q_el in enumerate(q_elements):
                print(f"\n--- Processing Question {idx + 1} ---")
                
                # 1. Extract Question Text
                qtext_el = q_el.locator(".qtext")
                qtext = qtext_el.inner_text().strip() if qtext_el.count() > 0 else f"Pregunta_{idx + 1}"
                
                # 2. Extract Options
                options = []
                opt_elements = q_el.locator(".answer > div").all()
                for opt_el in opt_elements:
                    # Clean up letter prefix like "a. ", "b. "
                    opt_text = opt_el.inner_text().strip()
                    opt_text = re.sub(r'^[a-z]\.\s+', '', opt_text)
                    options.append(opt_text)
                    
                if not options:
                    print("No options found. Skipping.")
                    continue
                    
                # 3. Determine Unique Hash
                q_hash = generate_hash(qtext, options)
                print(f"Hash: {q_hash}")
                
                if q_hash in existing_hashes:
                    print("Question already exists in DB. Skipping.")
                    continue
                    
                # 4. Determine Correct Answer
                # Check if question is marked correct
                state_el = q_el.locator(".info .state")
                state_text = state_el.inner_text().strip().lower() if state_el.count() > 0 else ""
                
                correct_option_idx = -1
                
                # Let's find the checked option
                checked_idx = -1
                for opt_idx, opt_el in enumerate(opt_elements):
                    # Check if input is checked
                    input_el = opt_el.locator("input[type='radio'], input[type='checkbox']")
                    if input_el.count() > 0:
                        is_checked = input_el.first.is_checked()
                        if is_checked:
                            checked_idx = opt_idx
                            break
                            
                print(f"State: {state_text}, Checked index: {checked_idx}")
                
                if "correcta" in state_text and "incorrecta" not in state_text:
                    # If state is correct, then the checked option is the correct one!
                    correct_option_idx = checked_idx
                else:
                    # If incorrect or partially correct, check the .rightanswer feedback block
                    right_ans_el = q_el.locator(".rightanswer")
                    if right_ans_el.count() > 0:
                        right_text = right_ans_el.inner_text().strip()
                        # e.g., "La respuesta correcta es: Ninguna respuesta es correcta."
                        # Extract the answer text after the colon
                        match = re.search(r'es:\s*(.*)$', right_text, re.IGNORECASE)
                        if match:
                            correct_text_raw = match.group(1).strip()
                            # Clean the prefix if it exists in the correct answer text (e.g. "a. ")
                            correct_text_clean = re.sub(r'^[a-z]\.\s+', '', correct_text_raw)
                            
                            # Find which option matches this correct text
                            for opt_idx, opt_text in enumerate(options):
                                if clean_text(opt_text) == clean_text(correct_text_clean):
                                    correct_option_idx = opt_idx
                                    break
                                    
                print(f"Determined correct option index: {correct_option_idx}")
                if correct_option_idx == -1:
                    print("WARNING: Could not resolve correct answer. Defaulting to 0.")
                    correct_option_idx = 0
                    
                # 5. Take Element Screenshot
                img_dir = os.path.join(os.path.dirname(__file__), "..", "data", "preguntas_img")
                os.makedirs(img_dir, exist_ok=True)
                img_path = f"{img_dir}/pregunta_{q_hash}.png"
                
                # Hide input checkmarks or visual decorations before screenshot to keep it clean (optional)
                # Scroll into view
                q_el.scroll_into_view_if_needed()
                time.sleep(0.5)
                q_el.screenshot(path=img_path)
                print(f"Saved screenshot to {img_path}")
                
                # 6. Add to Database
                db["preguntas"].append({
                    "id": q_hash,
                    "text_snippet": qtext[:150],
                    "image_path": img_path,
                    "options": options,
                    "correct_idx": correct_option_idx
                })
                existing_hashes.add(q_hash)
                new_questions_count += 1
                
            if new_questions_count > 0:
                print(f"\nAdding {new_questions_count} new questions to database...")
                with open(DB_FILE, "w", encoding="utf-8") as f:
                    json.dump(db, f, ensure_ascii=False, indent=2)
                print("Database updated!")
            else:
                print("\nNo new questions were found in this attempt.")
                
        except Exception as e:
            print(f"Error during extraction: {e}")
            page.screenshot(path=os.path.join(DEBUG_DIR, "extract_review_error.png"))
        finally:
            browser.close()

if __name__ == "__main__":
    extract_review_questions()
