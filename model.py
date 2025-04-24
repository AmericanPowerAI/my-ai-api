import json
import os
import base64
import requests

class SimpleAI:
    def __init__(self, base_path="memory"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def get_memory_path(self, api_key):
        return os.path.join(self.base_path, f"{api_key}_learned.json")

    def load_memory(self, api_key):
        path = self.get_memory_path(api_key)
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return []

    def save_memory(self, api_key, memory):
        path = self.get_memory_path(api_key)
        with open(path, "w") as f:
            json.dump(memory, f, indent=2)
        save_to_github(api_key, memory)

    def learn(self, api_key, fact):
        memory = self.load_memory(api_key)
        memory.append({"fact": fact})
        self.save_memory(api_key, memory)

    def train(self, api_key, text):
        memory = self.load_memory(api_key)
        memory.append({"text": text})
        self.save_memory(api_key, memory)

    def answer(self, api_key, question):
        memory = self.load_memory(api_key)
        for item in reversed(memory):
            if "fact" in item and question.lower() in item["fact"].lower():
                return item["fact"]
        return "I don't know yet, but I'm learning."

ai_model = SimpleAI()

# GitHub saving function
def save_to_github(api_key, memory_data):
    token = os.getenv("GITHUB_TOKEN")  # Set in Render later
    repo = "your-username/my-ai-api"  # 🔁 CHANGE this to your actual GitHub repo name
    file_path = f"memory/{api_key}_learned.json"
    api_url = f"https://api.github.com/repos/{repo}/contents/{file_path}"

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(api_url, headers=headers)
    sha = response.json().get("sha") if response.status_code == 200 else None

    encoded_content = base64.b64encode(
        json.dumps(memory_data, indent=2).encode()
    ).decode()

    data = {
        "message": f"Update memory for {api_key}",
        "content": encoded_content,
        "sha": sha,
    }

    update = requests.put(api_url, headers=headers, json=data)
    return update.status_code, update.json()
