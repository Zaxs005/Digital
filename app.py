import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import time
import logging

# Initialize Flask app
app = Flask(__name__)

# Basic configurations
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure the API key
genai.configure(api_key="AIzaSyCkqqY3QB2C7y5hcTfRhVDuGclUgfXWev0")

# Generation configuration
generation_config = {
    "temperature": 0.6,
    "top_p": 0.7,
    "top_k": 30,
    "max_output_tokens": 512,
    "response_mime_type": "text/plain",
}

# Model configuration with updated instruction
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    system_instruction="""My name is CCSai I'm your assistive ai partner, your assistive AI partner. You are only capable of giving information regarding the following subjects:

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

9. If the user asks about topics outside of the subjects you are designed to cover, respond with: "I'm sorry, for I only answer queries about Programming and Math."

Limits:
You will only answer questions about Discrete Math, Calculus, and Basic Programming fundamentals in Java, C++, and Python. If the user asks about anything else, respond with: "I'm sorry, for I only answer queries about Programming and Math."
"""
)

@app.route('/')
def index():
    return render_template('index.html')

def call_api_with_retry(user_input, retries=3):
    backoff = 2  # Start with a 2-second delay for backoff
    for attempt in range(retries):
        try:
            logging.debug(f"Attempt {attempt + 1}: Sending message to API - {user_input}")
            # Start a new chat session for each request to ensure fresh context
            chat_session = model.start_chat(history=[])
            response = chat_session.send_message(user_input)
            if response:
                logging.info(f"Response received on attempt {attempt + 1}: {response.text}")
                return response
        except Exception as e:
            logging.error(f"Attempt {attempt + 1} failed with error: {e}")
            if '429' in str(e):  # Check for rate-limiting error (429)
                logging.warning(f"Rate limit exceeded. Retrying after {backoff} seconds...")
                time.sleep(backoff)
                backoff *= 2
            else:
                logging.error(f"Non-retryable error encountered: {e}")
                break  # Exit loop for non-retryable errors
    logging.error("Failed to get a response after all retries.")
    return None

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({"response": "No message received"})

    try:
        response = call_api_with_retry(user_input)
        
        if response:
            formatted_response = format_response(response.text)
            return jsonify({"response": formatted_response})
        else:
            logging.warning("No response received from chatbot.")
            return jsonify({"response": "I'm sorry, but I couldn't process your request at the moment. Please try again later."})
    except Exception as e:
        logging.error(f"API Error: {e}")
        return jsonify({"response": "An error occurred while processing your request. Please try again later."})

def format_response(response_text):
    """Format the chatbot's response as HTML."""
    return "".join(f"<p>{line.strip()}</p>" for line in response_text.split("\n") if line.strip())

if __name__ == '__main__':
    app.run(debug=True)
