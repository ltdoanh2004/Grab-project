import json
def save_data_to_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_data_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
