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
    system_instruction="""You are a chatbot named ProgMatics Bot Chris or Chris...
    """ # Keep your full system instruction as before
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
