import json
import os

def append_new_skill(file_path, new_skill_data):
    # Check if the file exists and is not empty
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        # File exists and contains data
        with open(file_path, 'r', encoding='utf-8') as file:
            # Load the existing data
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                # File is not valid JSON; treat as empty dict
                data = {}
    else:
        # File does not exist or is empty; start with an empty dict
        data = {}

    # Assuming new_skill_data is a dictionary of skills keyed by their unique IDs
    data.update(new_skill_data)

    # Write the updated data back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

# Example usage
file_path = 'buckets\\skills_processed.json'
new_skill_data = {
    "NEW_UNIQUE_KEY": {
        "skill_name": "New Skill",
        "skill_cleaned": "new skill",
        "skill_type": "Hard Skill",
        "skill_lemmed": "new skill",
        "skill_stemmed": "new skill",
        "skill_len": 2,
        "abbreviation": "",
        "unique_token": "",
        "match_on_stemmed": False
    }
}

append_new_skill(file_path, new_skill_data)
