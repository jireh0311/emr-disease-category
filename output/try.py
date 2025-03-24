import os
import json
import requests
import re

# Folder Paths
INPUT_FOLDER = "New Data"
OUTPUT_FOLDER = "Categorized-Diseases"
MODEL_NAME = "medllama2"

# Ensure folders exist
os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Function to read JSON files
def read_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return None

# Function to extract disease name & description
def extract_disease_info(data):
    """Extracts disease name and description."""
    if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
        first_entry = data["data"][0]
        name = first_entry.get("Data", {}).get("TitleCaseName", "Unknown Disease")
        description = first_entry.get("Data", {}).get("Description", "").strip()
        return name, description
    return "Unknown Disease", ""

# Function to clean AI response
def clean_category(response):
    response = response.strip().strip('"')
    response = re.sub(r'[^a-zA-Z0-9\s]', '', response)  # Remove special characters
    response = "_".join(response.split()[:3])  # Keep only first three words
    return response

# Function to categorize disease using AI
def categorize_disease(disease_name, description):
    if not description or len(description) < 10:
        print(f"⚠️ Skipping {disease_name}: Insufficient text for categorization.")
        return "Unclassified"

    prompt = f"""
    You are an AI trained to analyze and categorize diseases.
    Given the following disease information, determine its most appropriate category.

    TASK:
    - Read the disease name and description.
    - Determine the most relevant category from standard medical classification.
    - Reply with ONLY the category name in a valid format (e.g., "Neurological Diseases", "Respiratory Diseases").
    - No explanations, extra words, or follow-up questions.
    - If uncertain, return "Unclassified".

    Disease Name: {disease_name}
    Disease Description: {description}
    """

    payload = {"model": MODEL_NAME, "prompt": prompt, "stream": False}

    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        if response.status_code == 200:
            try:
                response_json = response.json()
                category = response_json.get("response", "").strip()
                return clean_category(category) if category else "Unclassified"
            except json.JSONDecodeError:
                print(f"⚠ AI Response is not valid JSON: {response.text}")
        else:
            print(f"⚠ AI Response Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠ AI Error: {e}")
    return "Unclassified"

# Function to save categorized data
def save_categorized_data(category, disease_name, data, file_name):
    category_folder = os.path.join(OUTPUT_FOLDER, category)
    os.makedirs(category_folder, exist_ok=True)
    output_file = os.path.join(category_folder, file_name)

    try:
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
        print(f"✅ {disease_name} categorized as {category} -> Saved to {category}/")
    except Exception as e:
        print(f"❌ Error saving {file_name}: {e}")

# Function to process all files
def process_files():
    if not os.path.exists(INPUT_FOLDER):
        print("❌ Input folder not found.")
        return
    
    for file_name in os.listdir(INPUT_FOLDER):
        file_path = os.path.join(INPUT_FOLDER, file_name)
        if os.path.isfile(file_path) and file_name.endswith(".json"):
            process_file(file_path)

# Function to process a single file
def process_file(file_path):
    data = read_json(file_path)
    if not data:
        return
    
    disease_name, description = extract_disease_info(data)
    category = categorize_disease(disease_name, description)
    
    if category:
        save_categorized_data(category, disease_name, data, os.path.basename(file_path))
    else:
        print(f"⚠ No valid category found for {disease_name}")

if __name__ == "__main__":
    process_files()