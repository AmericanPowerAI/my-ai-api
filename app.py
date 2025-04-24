from flask import Flask, request, jsonify
from model import ai_model

app = Flask(__name__)

@app.route("/")
def index():
    return "🤖 AI API is running."

@app.route("/learn", methods=["POST"])
def learn():
    data = request.get_json()
    api_key = data.get("api_key")
    fact = data.get("fact")

    if not api_key or not fact:
        return jsonify({"error": "Missing api_key or fact"}), 400

    ai_model.learn(api_key, fact)
    return jsonify({"message": "Fact learned."})

@app.route("/train", methods=["POST"])
def train():
    data = request.get_json()
    api_key = data.get("api_key")
    text = data.get("text")

    if not api_key or not text:
        return jsonify({"error": "Missing api_key or text"}), 400

    ai_model.train(api_key, text)
    return jsonify({"message": "Text trained."})

@app.route("/answer", methods=["POST"])
def answer():
    data = request.get_json()
    api_key = data.get("api_key")
    question = data.get("question")

    if not api_key or not question:
        return jsonify({"error": "Missing api_key or question"}), 400

    answer = ai_model.answer(api_key, question)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
