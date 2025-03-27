import json
import os
from ollama import chat  # Ensure Ollama is installed and running

# File paths
input_file_path = "Data/mc-s.json"
output_file_path = "New Data2./mc-s.json"

# Keys to remove
keys_to_remove = {"MaladyId", "Symbol", "MiFts", "Score", "Parent", "Childs", "NumSiblings"}

# List of possible disease categories
CATEGORIES = [
    "Infectious Disease", "Genetic Disorder", "Neurological Disorder",
    "Respiratory Disease", "Cardiovascular Disease", "Endocrine Disorder",
    "Autoimmune Disease", "Skin Disorder", "Gastrointestinal Disease",
    "Musculoskeletal Disorder", "Mental Health Disorder", "Hematologic Disorder",
    "Renal Disease", "Cancer" 
]

def categorize_disease(description):
    """Use AI to determine the category of a disease."""
    try:
        prompt = (
            f"Classify the following disease into ONE of these categories: {', '.join(CATEGORIES)}. "
            f"ONLY return the category name, no explanations.\n\n"
            f"Description: {description}\n\n"
            f"Category:"
        )

        response = chat(model='medllama2', messages=[{'role': 'user', 'content': prompt}])
        ai_response = response['message']['content'].strip()

        # Ensure AI only returns a valid category
        for category in CATEGORIES:
            if category in ai_response:
                print(f"✔ Categorized: {description[:50]}... -> {category}")  # Debugging output
                return category

        print(f"⚠ AI returned unexpected response: {ai_response}. Defaulting to 'Other'.")
        return "Other"

    except Exception as e:
        print(f"⚠ AI Error: {e}")
        return "Unknown"

# Check if input file exists
if os.path.exists(input_file_path):
    print(f"📂 Processing file: {input_file_path}")  # Debugging output

    with open(input_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if "data" in data and isinstance(data["data"], list):
        print(f"✅ Found {len(data['data'])} diseases to categorize.")  # Debugging output

        for entry in data["data"]:
            if "Data" in entry and isinstance(entry["Data"], dict):
                # Remove unwanted keys
                for key in keys_to_remove:
                    entry["Data"].pop(key, None)
                
                # Ensure 'Slug' exists
                if "Slug" not in entry["Data"]:
                    entry["Data"]["Slug"] = ""

                # Categorize disease using AI
                description = entry["Data"].get("Description", "")
                if description:
                    entry["Data"]["Category"] = categorize_disease(description)
                else:
                    entry["Data"]["Category"] = "Unknown"

        # Save the cleaned and categorized data
        with open(output_file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        print(f"✅ Categorized data saved successfully at {output_file_path}!")
    else:
        print("⚠ No valid 'data' list found in JSON file.")
else:
    print(f"⚠ Error: Input file '{input_file_path}' not found!")
