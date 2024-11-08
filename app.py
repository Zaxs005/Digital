import os  
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import time

app = Flask(__name__)

# Set up basic configurations
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True

# Replace with your actual API key
genai.configure(api_key="AIzaSyCkqqY3QB2C7y5hcTfRhVDuGclUgfXWev0")

# Reduced generation configuration for stability
generation_config = {
    "temperature": 0.8,     # Lowered for consistency
    "top_p": 0.85,          # Reduced for less randomness
    "top_k": 40,            # Limits token sampling
    "max_output_tokens": 1024,  # Reduced max tokens
    "response_mime_type": "text/plain",
}

# Model configuration
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
)

# Define system instructions
system_instruction = """
You are a chatbot named ProgMatics Bot Chris or Chris. 
You are only capable of giving information regarding the following subjects:

1. The user can ask about the meanings of basic programming fundamentals and programming languages only in Java, C++, and Python, and the chatbot will give a specific answer, also about its history, who made and discovered it. It must also answer what the program's output and error are.

2. The user can ask about the meanings of Mathematics mainly in Discrete Math and Calculus, and the chatbot will give a specific explanation, including history, who made and discovered it.

The topics in Discrete Math should only answer are mainly the following:
- Relation
- Function
- Sets
- Proposition
- Cardinality
- Sequence and Series
- Permutations
- Combinations

The topics in Calculus should only answer the following topics:
- Functions
- Logarithmic Functions
- Limits
- Derivatives

3. If a user asks a question outside of these topics, reply: "Forgive me, I only answer queries about Programming and Math."

4. Provide responses in a glossary format.

5. When users ask about Discrete Math and Calculus and also Programming, the chatbot should mention if it enhances Logical Thinking, Analytical Thinking, or Critical Thinking.

6. If a user asks for a solution to a problem or how to solve something in Calculus or Discrete Math, the chatbot must answer and also provide links related to the topic.

7. When a user asks for programming code, the chatbot must answer with code examples and provide links.

Thank you for asking, here is your answer:
"""

@app.route('/')
def index():
    return render_template('index.html')

# Function to check if the message contains allowed topics
def is_valid_question(user_input):
    allowed_keywords = ['c++', 'java', 'python', 'discrete math', 'calculus']
    discrete_math_keywords = ['relation', 'function', 'sets', 'proposition', 'cardinality', 
                              'sequence', 'series', 'permutations', 'combinations']
    calculus_keywords = ['functions', 'logarithmic functions', 'limits', 'derivatives']
    basic_programming_questions = [
        "what is programming",
        "what is python",
        "what is c++",
        "what is java",
        "what is discrete math",
        "what is calculus"
    ]
    problem_solving_keywords = ['how to solve', 'solution', 'solve', 'steps to solve']

    user_input = user_input.lower()  # Make the input case-insensitive
    
    # Check for valid topics in programming or math
    if any(keyword in user_input for keyword in allowed_keywords):
        return True
    if any(keyword in user_input for keyword in discrete_math_keywords):
        return True
    if any(keyword in user_input for keyword in calculus_keywords):
        return True
    if any(question in user_input for question in basic_programming_questions):
        return True
    if any(keyword in user_input for keyword in problem_solving_keywords):
        return True

    return False

def call_api_with_retry(chat_session, user_input, retries=3):
    for attempt in range(retries):
        try:
            response = chat_session.send_message(user_input)
            return response
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            time.sleep(2)  # Wait before retrying
    return None

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({"response": "No message received"})

    # Check if the input contains valid keywords or basic programming questions
    if not is_valid_question(user_input):
        return jsonify({"response": "Forgive me, I only answer queries about Programming and Math."})

    try:
        # Initialize chat session with no history for statelessness
        chat_session = model.start_chat(history=[])
        chat_session.set_system_instruction(system_instruction)  # Ensure system instructions are applied
        
        # Use retry function to send the message
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
    response_lines = response_text.split("\n")
    formatted_lines = [f"<p>{line}</p>" for line in response_lines]
    return "".join(formatted_lines)

if __name__ == '__main__':
    app.run(debug=True)
