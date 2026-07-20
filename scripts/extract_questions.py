import os
import re
import json
import hashlib
import time
from playwright.sync_api import sync_playwright

USERNAME = "fmoralesp3"
PASSWORD = "H4CKER2019f"
QUIZ_URL = "https://aulagradoa.unemi.edu.ec/mod/quiz/view.php?id=75918"
DB_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "questions_bank.json")
IMG_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "preguntas_img")
DEBUG_DIR = os.path.join(os.path.dirname(__file__), "..", "debug")

# Ensure directories exist
os.makedirs(IMG_DIR, exist_ok=True)

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading existing database: {e}")
    return {"total_preguntas": 0, "preguntas": []}

def save_db(db):
    db["total_preguntas"] = len(db["preguntas"])
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

def clean_text(text):
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def clean_option(opt_text):
    # Remove option letter like "a. ", "b. ", "A. ", etc.
    opt_text = re.sub(r'^[a-d]\.\s*', '', opt_text, flags=re.IGNORECASE)
    return clean_text(opt_text)

def generate_hash(qtext, options):
    cleaned_options = [clean_option(opt) for opt in options]
    cleaned_options.sort()  # Sort to ignore shuffling
    combined = clean_text(qtext) + "|" + "|".join(cleaned_options)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()

def submit_attempt(page):
    print("Executing JavaScript submit on summary page...")
    # Click the first "Enviar todo y terminar" button on the summary page
    page.evaluate("""
        const buttons = Array.from(document.querySelectorAll('button, input[type=submit], input[type=button]'));
        const btn = buttons.find(b => {
            const text = (b.innerText || '').trim();
            const val = (b.value || '').trim();
            return text.includes('Enviar todo y terminar') || val.includes('Enviar todo y terminar');
        });
        if (btn) {
            btn.click();
        }
    """)
    
    # Wait for the modal dialog to appear
    time.sleep(2.5)
    
    # Click the confirmation button inside the modal dialog
    page.evaluate("""
        const buttons = Array.from(document.querySelectorAll('.modal-content button, .modal-dialog button, #confirm_submit, input[value*="Enviar todo y terminar"]'));
        const btn = buttons.find(b => {
            const text = (b.innerText || '').trim();
            const val = (b.value || '').trim();
            return text.includes('Enviar todo y terminar') || val.includes('Enviar todo y terminar');
        });
        if (btn) {
            btn.click();
        }
    """)
    time.sleep(2)

def run_extraction():
    db = load_db()
    existing_hashes = {q["id"] for q in db["preguntas"]}
    print(f"Loaded database: {len(existing_hashes)} existing questions.")

    with sync_playwright() as p:
        # Launch browser in headful mode so the user can watch the progress
        print("Launching browser...")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        try:
            print("Navigating to quiz page...")
            page.goto(QUIZ_URL)
            page.wait_for_load_state("load")
            
            # Check login
            if "login" in page.url or page.locator("input[name='username']").is_visible():
                print("Logging in...")
                page.fill("input[name='username']", USERNAME)
                page.fill("input[name='password']", PASSWORD)
                page.click("#loginbtn")
                page.wait_for_load_state("load")
                
                # Make sure we are on the quiz page
                if QUIZ_URL not in page.url:
                    page.goto(QUIZ_URL)
                    page.wait_for_load_state("load")

            attempt_count = 0
            consecutive_no_new = 0

            while True:
                attempt_count += 1
                print(f"\n--- Starting Attempt {attempt_count} ---")
                
                # Look for button to start attempt
                start_btn = None
                for selector in ["text='Reintentar el cuestionario'", "text='Intentar resolver el cuestionario ahora'", "text='Continuar el último intento'"]:
                    locator = page.locator(selector)
                    if locator.is_visible():
                        start_btn = locator
                        break
                
                if not start_btn:
                    print("Could not find start button. Check page screenshot:")
                    page.screenshot(path=os.path.join(DEBUG_DIR, "debug_start_error.png"))
                    break
                    
                btn_text = start_btn.inner_text()
                print(f"Clicking: '{btn_text}'")
                start_btn.click()
                page.wait_for_load_state("load")
                
                # Check for confirmation modal dialog
                time.sleep(2)  # Wait for dialog modal to load if any
                dialog_start = page.locator("input[type='submit']#id_submitbutton, input[value='Comenzar intento'], button:has-text('Comenzar intento'), .modal-footer button.btn-primary")
                if dialog_start.is_visible():
                    print("Confirming attempt start...")
                    dialog_start.click()
                    page.wait_for_load_state("load")

                # Check if we landed on the summary page directly
                time.sleep(2.5)
                if "summary.php" in page.url:
                    print("Landed on summary page at the start. Submitting attempt to start fresh...")
                    submit_attempt(page)
                    print("Resumed attempt submitted.")
                    page.goto(QUIZ_URL)
                    page.wait_for_load_state("load")
                    continue

                # Ensure we navigate to page 1 of the attempt (page=0)
                try:
                    # Look for the button pointing to page 0 (which is question 1)
                    first_page_link = page.locator("a[href*='page=0'], a[href*='&page=0']").first
                    first_page_link.wait_for(state="visible", timeout=5000)
                    print("Navigating to page 1 via navigation panel (page=0)...")
                    first_page_link.click()
                    page.wait_for_load_state("load")
                    time.sleep(2)
                except Exception as ne:
                    print(f"Could not navigate to page 1 via panel link: {ne}. Trying URL fallback...")
                    current_url = page.url
                    current_url = current_url.replace("summary.php", "attempt.php")
                    if "page=" in current_url:
                        current_url = re.sub(r'page=\d+', 'page=0', current_url)
                    else:
                        current_url = current_url + "&page=0"
                    print(f"Navigating to page 1 URL fallback: {current_url}")
                    page.goto(current_url)
                    page.wait_for_load_state("load")
                    time.sleep(2)

                # Final URL check to guarantee we are on page 1 (if Moodle redirected us, it's sequential lock)
                if "page=0" not in page.url:
                    print("URL verification failed: Moodle redirected us away from page 1.")
                    print("This attempt is locked due to Sequential Navigation. Submitting it to start fresh...")
                    
                    # Navigate to summary to submit
                    summary_url = page.url.replace("attempt.php", "summary.php").split("&page=")[0]
                    page.goto(summary_url)
                    page.wait_for_load_state("load")
                    time.sleep(2.5)
                    
                    submit_attempt(page)
                    print("Locked attempt submitted.")
                    page.goto(QUIZ_URL)
                    page.wait_for_load_state("load")
                    continue

                # Process the 10 questions (1 per page)
                new_questions_this_attempt = 0
                
                for page_num in range(1, 11):
                    print(f"Processing page {page_num}/10...")
                    # Wait for question container to load
                    page.wait_for_selector(".que", timeout=15000)
                    
                    que_el = page.locator(".que").first
                    
                    # Get question text
                    qtext_el = que_el.locator(".qtext")
                    qtext = qtext_el.inner_text() if qtext_el.count() > 0 else ""
                    
                    # Get option texts
                    option_els = que_el.locator(".answer > div")
                    options = []
                    for i in range(option_els.count()):
                        opt_text = option_els.nth(i).inner_text()
                        options.append(opt_text)
                    
                    # Clean options list
                    options = [o for o in options if o.strip()]
                    
                    # Generate unique ID
                    q_id = generate_hash(qtext, options)
                    
                    if q_id not in existing_hashes:
                        new_questions_this_attempt += 1
                        existing_hashes.add(q_id)
                        print(f"  [NEW] Question found! Hash: {q_id[:8]}...")
                        
                        # Capture screenshot of the question element
                        img_path = os.path.join(IMG_DIR, f"pregunta_{q_id}.png")
                        que_el.screenshot(path=img_path)
                        
                        # Append metadata to database
                        db["preguntas"].append({
                            "id": q_id,
                            "image_path": img_path,
                            "text_snippet": qtext[:150],
                            "options": [clean_option(o) for o in options]
                        })
                        save_db(db)
                    else:
                        print(f"  [DUP] Question already exists. Hash: {q_id[:8]}...")
                    
                    # Click next page
                    if page_num < 10:
                        next_btn = page.locator("input[name='next'], #mod_quiz-next-nav").first
                        if next_btn.is_visible():
                            print("  Clicking next page button...")
                            next_btn.click()
                            page.wait_for_load_state("load")
                            time.sleep(1.5)
                        else:
                            print(f"  [WARN] Next button not visible on page {page_num}")
                            page.screenshot(path=os.path.join(DEBUG_DIR, f"debug_next_error_page_{page_num}.png"))
                            break
                    else:
                        # Final page, click next to go to summary
                        next_btn = page.locator("input[name='next'], #mod_quiz-next-nav").first
                        if next_btn.is_visible():
                            print("  Clicking next page button (to summary)...")
                            next_btn.click()
                            page.wait_for_load_state("load")
                            time.sleep(1.5)
                        else:
                            print("  [WARN] Final next button not visible")
                            page.screenshot(path=os.path.join(DEBUG_DIR, "debug_final_next_error.png"))
                
                # We are now on summary page, let's submit and finish
                print("On summary page, submitting attempt...")
                submit_attempt(page)
                print("Attempt submitted successfully!")
                
                # Wait and go back to quiz URL
                print(f"Attempt finished. New questions found in this attempt: {new_questions_this_attempt}")
                page.goto(QUIZ_URL)
                page.wait_for_load_state("load")
                
                if new_questions_this_attempt == 0:
                    consecutive_no_new += 1
                    print(f"No new questions found. Consecutive attempts with 0 new questions: {consecutive_no_new}")
                else:
                    consecutive_no_new = 0
                
                # Stop condition: if we hit 5 attempts in a row with 0 new questions, we stop
                if consecutive_no_new >= 5:
                    print("\nNo new questions discovered in the last 5 attempts. Stopping.")
                    break
                    
                # Limit total attempts to prevent infinite loop
                if attempt_count >= 50:
                    print("\nReached max limit of 50 attempts. Stopping.")
                    break
                    
                time.sleep(2)

        except Exception as e:
            print(f"\n[CRASH] Script crashed with error: {e}")
            try:
                page.screenshot(path=os.path.join(DEBUG_DIR, "debug_crash.png"))
                print(f"Captured debug screenshot to debug/debug_crash.png. Current URL: {page.url}")
            except Exception as se:
                print(f"Failed to capture crash screenshot: {se}")
            raise e
        finally:
            browser.close()

    print(f"\nExtraction completed! Total unique questions in DB: {db['total_preguntas']}")

if __name__ == "__main__":
    run_extraction()
