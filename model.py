import json
import os

class SimpleAI:
    def __init__(self, memory_path="memory/learned.json"):
        self.memory_path = memory_path
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        self.memory = self.load_memory()

    def load_memory(self):
        if os.path.exists(self.memory_path):
            with open(self.memory_path, "r") as f:
                return json.load(f)
        return []

    def save_memory(self):
        with open(self.memory_path, "w") as f:
            json.dump(self.memory, f, indent=2)

    def train(self, text):
    self.memory.append({"text": text})
    self.save_memory()
    save_to_github(self.memory) 

    def learn(self, fact):
    self.memory.append({"fact": fact})
    self.save_memory()
    save_to_github(self.memory) 

    def answer(self, question):
        for item in reversed(self.memory):
            if "fact" in item and question.lower() in item["fact"].lower():
                return item["fact"]
        return "I don't know yet, but I'm learning."

ai_model = SimpleAI()
import base64
import requests

def save_to_github(memory_data):
    token = os.getenv("GITHUB_TOKEN")  # Set in Render later
    repo = "your-username/my-ai-api"  # 🔁 CHANGE this to your actual GitHub repo name
    file_path = "memory/learned.json"
    api_url = f"https://api.github.com/repos/{repo}/contents/{file_path}"

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(api_url, headers=headers)
    sha = response.json().get("sha")

    encoded_content = base64.b64encode(
        json.dumps(memory_data, indent=2).encode()
    ).decode()

    data = {
        "message": "Update AI memory",
        "content": encoded_content,
        "sha": sha,
    }

    update = requests.put(api_url, headers=headers, json=data)
    return update.status_code, update.json()

