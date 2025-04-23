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

    def learn(self, fact):
        self.memory.append({"fact": fact})
        self.save_memory()

    def answer(self, question):
        for item in reversed(self.memory):
            if "fact" in item and question.lower() in item["fact"].lower():
                return item["fact"]
        return "I don't know yet, but I'm learning."

ai_model = SimpleAI()
