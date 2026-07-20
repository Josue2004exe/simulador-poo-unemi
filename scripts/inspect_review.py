import os
import re
import json
import hashlib
import time
from playwright.sync_api import sync_playwright

USERNAME = "fmoralesp3"
PASSWORD = "H4CKER2019f"
REVIEW_URL = "https://aulagradoa.unemi.edu.ec/mod/quiz/review.php?attempt=55126&cmid=61246"
DEBUG_DIR = os.path.join(os.path.dirname(__file__), "..", "debug")

def inspect_review():
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        try:
            print("Navigating to review page (redirects to login)...")
            page.goto(REVIEW_URL)
            page.wait_for_load_state("load")
            
            if "login" in page.url or page.locator("input[name='username']").is_visible():
                print("Logging in...")
                page.fill("input[name='username']", USERNAME)
                page.fill("input[name='password']", PASSWORD)
                page.click("#loginbtn")
                page.wait_for_load_state("load")
                
                if REVIEW_URL not in page.url:
                    print("Navigating back to review URL...")
                    page.goto(REVIEW_URL)
                    page.wait_for_load_state("load")
            
            print(f"Landed on page: {page.url}")
            time.sleep(3)
            
            # Capture debug screenshot of the review page
            page.screenshot(path=os.path.join(DEBUG_DIR, "review_debug.png"))
            print("Captured debug screenshot to 'debug/review_debug.png'")
            
            # Count question elements
            ques = page.locator(".que").all()
            print(f"Number of question elements (.que) found on this page: {len(ques)}")
            
            # Check for pagination in review page
            pagination_links = page.locator(".page-link, .pagination a").all()
            print(f"Number of pagination links found: {len(pagination_links)}")
            for idx, pl in enumerate(pagination_links):
                print(f"  Link {idx}: text='{pl.inner_text()}', href='{pl.get_attribute('href')}'")
                
        except Exception as e:
            print(f"Error during inspection: {e}")
            page.screenshot(path=os.path.join(DEBUG_DIR, "review_error.png"))
        finally:
            browser.close()

if __name__ == "__main__":
    inspect_review()
