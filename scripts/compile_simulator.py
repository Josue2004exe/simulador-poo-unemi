import os
import re
import json
import base64

# Base directories relative to this script
BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(BASE_DIR, "data")
SRC_DIR = os.path.join(BASE_DIR, "src")

def compile_to_single_file():
    print("Starting compilation of the simulator into a single offline file...")
    
    # 1. Read the questions bank database
    with open(os.path.join(DATA_DIR, "questions_bank.json"), "r", encoding="utf-8") as f:
        db = json.load(f)
        
    print("Encoding images to Base64...")
    # 2. Iterate through each question and convert its image to Base64
    for idx, q in enumerate(db["preguntas"]):
        img_path = q["image_path"]
        # Resolve the image path relative to the src/ directory (where the HTML lives)
        resolved_path = os.path.normpath(os.path.join(SRC_DIR, img_path))
        if os.path.exists(resolved_path):
            with open(resolved_path, "rb") as img_file:
                encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
                # Replace the image path with the Base64 Data URL
                q["image_path"] = f"data:image/png;base64,{encoded_string}"
        else:
            print(f"Warning: Image not found at {resolved_path}")
            
    # Convert the updated database back to a JSON string representation
    db_json = json.dumps(db, ensure_ascii=False, indent=2)
    
    # 3. Read HTML, CSS, and JS source files from src/
    with open(os.path.join(SRC_DIR, "index.html"), "r", encoding="utf-8") as f:
        html = f.read()
        
    with open(os.path.join(SRC_DIR, "style.css"), "r", encoding="utf-8") as f:
        css = f.read()
        
    with open(os.path.join(SRC_DIR, "app.js"), "r", encoding="utf-8") as f:
        js = f.read()
        
    print("Inlining assets...")
    # 4. Inject CSS into the HTML (replace the link stylesheet tag)
    css_inline = f"<style>\n{css}\n</style>"
    html = re.sub(r'<link rel="stylesheet" href="style.css">', css_inline, html)
    
    # 5. Inject the solved questions database and the application logic JS
    js_inline = f"<script>\nconst QUESTIONS_DATA = {db_json};\n\n{js}\n</script>"
    
    # Remove the external script tags in index.html and inject our combined script
    html = re.sub(r'<script src="\.\./data/questions_data\.js"></script>\s*<script src="app\.js"></script>', js_inline, html)
    
    # 6. Save the final compiled file to the project root
    output_filename = os.path.join(BASE_DIR, "simulador_poo_offline.html")
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html)
        
    file_size_mb = os.path.getsize(output_filename) / (1024 * 1024)
    print(f"Compilation finished successfully!")
    print(f"Output file: {output_filename}")
    # Link formatting for final report:
    print(f"File absolute path: {os.path.abspath(output_filename)}")
    print(f"Final file size: {file_size_mb:.2f} MB")

if __name__ == "__main__":
    compile_to_single_file()
