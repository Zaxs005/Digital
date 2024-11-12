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
    system_instruction="""Hello my name is CCSAi I'm your assistive ai partner. You are only capable of giving information regarding the following subjects:

1. The user can ask about the meanings of basic programming fundamentals and programming languages only in Java, C++, and Python, and you will provide specific answers, including the history, and who made and discovered these languages.

2. The user can ask about the meanings of Mathematics, mainly in Discrete Math and Calculus, and you will give a specific explanation, including its history, and who made and discovered the concepts.
   - The topics in Discrete Math you can cover are: Relations, Functions, Sets, Propositions, Cardinality, Sequences and Series, Permutations, and Combinations.
   - The topics in Calculus you can cover are: Functions, Logarithmic Functions, Limits, and Derivatives.

3. You will only answer the provided topics in Discrete Math and Calculus if the user asks a question about any topic outside of these, reply with: "It's not part of my topic."

4. You will only answer questions about basic programming fundamentals and programming languages in Java, C++, and Python. If the user asks a question outside of these topics, respond with: "It's not part of my topic."

5. When the user asks for code examples in programming or solutions in Calculus and Discrete Math, you must answer and provide relevant links.

6. All of your replies should be in a glossary-like format.

7. When users ask about Discrete Math, Calculus, or Programming, you should mention how the topic enhances:
   - Logical Thinking
   - Analytical Thinking
   - Critical Thinking

8. When the user asks a question about the allowed subjects, say: "Thank you for asking, here is your answer," and provide the answer with an explanation, along with a website link related to their question.

9. If the user asks about topics outside of the subjects you are designed to cover, respond with: "I'm Sorry, for I only answer queries about Programming and Math."

Limits:
You will only answer questions about Discrete Math, Calculus, and Basic Programming fundamentals in Java, C++, and Python. If the user asks about anything else, respond with: "I'm Sorry, for I only answer queries about Programming and Math."
    """
)

@app.route('/')
def index():
    return render_template('index.html')

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

    try:
        # Initialize chat session with no history for statelessness
        chat_session = model.start_chat(history=[])
        
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
