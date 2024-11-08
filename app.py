import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import time
import re

app = Flask(__name__)

# Set up basic configurations
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True

# Replace with your actual API key
genai.configure(api_key="AIzaSyCkqqY3QB2C7y5hcTfRhVDuGclUgfXWev0")

# Reduced generation configuration for stability
generation_config = {
    "temperature": 0.8,
    "top_p": 0.85,
    "top_k": 40,
    "max_output_tokens": 1024,
    "response_mime_type": "text/plain",
}

# System Instruction as per user specifications
system_instruction = """You are a chatbot named ProgMatics Bot Chris or Chris. You are only capable of providing information regarding the following subjects:

1. **Programming Fundamentals and Languages**:
   - Users can ask about the meanings of basic programming fundamentals and programming languages only in **Java**, **JavaScript**, **C++**, and **Python**.
   - Provide specific answers including the history of these programming languages, who created them, and when they were discovered.
   - When asked about code output or error explanation, provide clear, concise responses about the code behavior or debugging guidance.

2. **Mathematics Topics**:
   - Users can ask about the meanings of Mathematics, mainly in **Discrete Math** and **Calculus**.
   - For **Discrete Math**, only answer the following topics:
     - Relation, Function, Sets, Proposition, Cardinality, Sequence and Series, Permutations, Combinations.
   - For **Calculus**, only answer the following topics:
     - Functions, Logarithmic Functions, Limits, Derivatives.
   - For any other topics, reply: "It's not part of my topic."

3. **Problem-Solving Queries**:
   - When asked for code solutions or math problem-solving, provide explanations with example code or steps as needed, along with a relevant link for further reading if available.

4. **Handling Unrelated Queries**:
   - If a user asks about topics outside the specified areas, reply: "Forgive me, I only answer queries about Programming and Math."
"""

# Model configuration with the system_instruction
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    system_instruction=system_instruction
)

@app.route('/')
def index():
    return render_template('index.html')

def is_valid_question(user_input):
    """
    Determines if the user's input is within the allowed topics.
    """
    programming_keywords = ['java', 'javascript', 'c++', 'python', 'output of this code', 'error in this code']
    discrete_math_keywords = ['relation', 'function', 'sets', 'proposition', 'cardinality', 'sequence and series', 'permutations', 'combinations']
    calculus_keywords = ['functions', 'logarithmic functions', 'limits', 'derivatives']
    problem_solving_keywords = ['solve', 'evaluate', 'calculate', 'find', 'determine']

    user_input_lower = user_input.lower()

    if any(keyword in user_input_lower for keyword in programming_keywords):
        return True
    if any(keyword in user_input_lower for keyword in discrete_math_keywords):
        return True
    if any(keyword in user_input_lower for keyword in calculus_keywords):
        return True
    if any(keyword in user_input_lower for keyword in problem_solving_keywords) and \
       (any(math_topic in user_input_lower for math_topic in discrete_math_keywords + calculus_keywords)):
        return True

    return False

def call_api_with_retry(chat_session, user_input, retries=3):
    for attempt in range(retries):
        try:
            response = chat_session.send_message(user_input)
            return response
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            time.sleep(2)
    return None

@app.route('/chat', methods=['POST'])
def chat(): 
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({"response": "No message received"})

    # Validate the user's question
    if not is_valid_question(user_input):
        return jsonify({"response": "Forgive me, I only answer queries about Programming and Math."})

    try:
        chat_session = model.start_chat(history=[])
        response = call_api_with_retry(chat_session, user_input)

        if response:
            formatted_response = format_response(response.text)
            return jsonify({"response": formatted_response})
        else:
            return jsonify({"response": "No response from the chatbot."})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"response": "An error occurred while processing your request. Please try again later."})

def format_response(response_text):
    """
    Formats the chatbot's response into a clean HTML structure without extra symbols like *.
    """
    response_text = response_text.replace('*', '')
    response_text = re.sub(r'```(\w+)?\n([\s\S]*?)```', r'<pre><code>\2</code></pre>', response_text)
    response_text = re.sub(r'`([^`]+)`', r'<code>\1</code>', response_text)
    response_lines = response_text.split("\n\n")
    formatted_lines = [f"<p>{line}</p>" for line in response_lines]
    return "".join(formatted_lines)

if __name__ == '__main__':
    app.run(debug=True)
