from flask import Flask, request, jsonify, render_template_string
import json
from difflib import get_close_matches
from flask_compress import Compress  

app = Flask(__name__)
Compress(app) 

# Load the knowledge base once when the server starts
knowledge_base_file = 'knowledge_base.json'

def load_knowledge_base(file_path: str) -> dict:
    try:
        with open(file_path, 'r') as file:
            data: dict = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return {"questions": []}
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} contains invalid JSON.")
        return {"questions": []}

def save_knowledge_base(file_path: str, data: dict):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)
    except IOError as e:
        print(f"Error saving knowledge base: {e}")

def find_best_match(user_input: str, questions: list[str]) -> str | None:
    user_input = user_input.lower().strip()
    matches = get_close_matches(user_input, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None

def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    question_dict = {q["question"].lower(): q["answer"] for q in knowledge_base["questions"]}
    return question_dict.get(question)

# Load the knowledge base initially
knowledge_base = load_knowledge_base(knowledge_base_file)
questions = [q["question"].lower() for q in knowledge_base["questions"]]

@app.route('/')
def home():
    return render_template_string(open('Frontend.html').read())

@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.form.get('user_input', '').strip().lower()
    
    if not user_input:
        return "Please ask a question."

    best_match = find_best_match(user_input, questions)
    
    if best_match:
        answer = get_answer_for_question(best_match, knowledge_base)
        if answer:
            answer = answer.replace('\n', '<br>')
            return answer
        else:
            return "I don't know the answer."
    else:
        return "I don't know the answer. Can you teach me?"

@app.route('/save_response', methods=['POST'])
def save_response():
    user_input = request.form.get('user_input', '').strip().lower()
    new_answer = request.form.get('new_answer', '').strip()

    if user_input and new_answer:
        knowledge_base["questions"].append({"question": user_input, "answer": new_answer})
        save_knowledge_base(knowledge_base_file, knowledge_base)
        questions.append(user_input)
        return "Thank you! I learned a new response!"
    return "Error: Missing user input or answer."

if __name__ == '__main__':
    app.run(debug=True)

