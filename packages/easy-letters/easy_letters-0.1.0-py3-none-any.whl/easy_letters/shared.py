import json


def load_openai_api_key(key_file_path: str) -> str:
    with open(key_file_path, "r") as key_file:
        return json.load(key_file)["secret_key"]
