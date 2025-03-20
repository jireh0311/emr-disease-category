import json
import os


input_file_path = "Data/mc-x.json"  
output_file_path = "New Data/mc-x.json"


keys_to_remove = {"MaladyId","Symbol", "MiFts", "Score", "Parent", "Childs", "NumSiblings"}


if os.path.exists(input_file_path):
    with open(input_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)


    if "data" in data and isinstance(data["data"], list):
        for entry in data["data"]:  
            if "Data" in entry and isinstance(entry["Data"], dict):
                for key in keys_to_remove:
                    entry["Data"].pop(key, None)  

    
    with open(output_file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    print(f"Cleaned data saved successfully at {output_file_path}!")
else:
    print("Error: Input file not found!")
