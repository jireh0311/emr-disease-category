import os
import json
from ollama import chat

# Folder Paths
INPUT_FOLDER = "New Data"
OUTPUT_FOLDER = "Categorized-Diseases 0.2"

# Ensure folders exist
os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ✅ Updated Disease Categories
CATEGORIES = [
    "Sexually Transmitted Infections (STIs)", 
    "Cardiovascular Diseases",
    "Respiratory Diseases", 
    "Neurological Diseases", 
    "Digestive Diseases", 
    "Endocrine Diseases", 
    "Musculoskeletal Diseases", 
    "Skin Diseases", 
    "Urinary & Reproductive System Diseases", 
    "Unknown"
]

def read_json(file_path):
    """Reads a JSON file and returns its content."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return None

def extract_description(data):
    """Extracts disease description from JSON structure."""
    if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
        first_entry = data["data"][0]  # Get the first disease entry
        return first_entry.get("Data", {}).get("Description", "").strip()
    return ""

def categorize_disease(description):
    """Uses AI to classify the disease based on description."""
    if not description or len(description) < 10:
        print("⚠️ Insufficient text, defaulting to 'Unknown'.")
        return "Unknown"

    prompt = f"""
    You are an AI trained to classify medical conditions.

    **TASK:**
    - Categorize the following disease into one of these categories:
      {', '.join(CATEGORIES)}.
    - **STRICT RULES:**
      - Return **ONLY** one category name.
      - No explanations.
      - No extra words.
      - No follow-up questions.

    **Disease Description:**
    {json.dumps(description, ensure_ascii=False)}

    **RESPONSE FORMAT (IMPORTANT!):**
    - Reply with only one of these categories: {', '.join(CATEGORIES)}
    - Do NOT return anything else, just the category name.
    - Example Correct Output: "Neurological Diseases"
    """

    try:
        response = chat(model="medllama2", messages=[{"role": "user", "content": prompt}])
        category = response["message"]["content"].strip().strip('"')

        # Force clean response by extracting only a valid category
        category = next((c for c in CATEGORIES if c.lower() in category.lower()), "Unknown")

        return category

    except Exception as e:
        print(f"❌ Error categorizing disease: {e}")
        return "Unknown"

def save_categorized_data(category, data, file_name):
    """Saves categorized data into the corresponding category folder."""
    category_folder = os.path.join(OUTPUT_FOLDER, category)
    os.makedirs(category_folder, exist_ok=True)

    output_file = os.path.join(category_folder, file_name)
    try:
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
        print(f"✅ Successfully saved {file_name} to {category}/")
    except Exception as e:
        print(f"❌ Error saving {file_name}: {e}")

def process_files():
    """Scans the input folder, categorizes each disease, and saves it."""
    files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".json")]

    if not files:
        print("📂 No JSON files found in the input folder.")
        return

    for file_name in files:
        file_path = os.path.join(INPUT_FOLDER, file_name)
        data = read_json(file_path)

        if not data:
            print(f"⚠️ Skipping file {file_name} due to read error.")
            continue

        description = extract_description(data)
        category = categorize_disease(description)
        save_categorized_data(category, data, file_name)

if __name__ == "__main__":
    process_files()
