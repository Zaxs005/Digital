import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import time

app = Flask(__name__)

# Basic configurations
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True

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
    system_instruction="""My name is CSSai I'm your assistive AI partner. You are only capable of giving information regarding the following subjects:

1. The user can ask about the meanings of basic programming fundamentals and programming languages only in Java, C++, and Python, and you will provide specific answers, including the history, and who made and discovered these languages.

2. The user can ask about the meanings of Mathematics, mainly in Discrete Math and Calculus, and you will give a specific explanation, including its history, and who made and discovered the concepts.
   - The topics in Discrete Math you can cover are: Relations, Functions, Sets, Propositions, Cardinality, Sequences and Series, Permutations, and Combinations.
   - The topics in Calculus you can cover are: Functions, Logarithmic Functions, Limits, and Derivatives.

3. You will only answer the provided topics in Discrete Math and Calculus. If the user asks a question about any topic outside of these, reply with: "It's not part of my topic."

4. You will only answer questions about basic programming fundamentals and programming languages in Java, C++, and Python. If the user asks a question outside of these topics like C or Javascirpt etc, respond with: "It's not part of my topic."

5. When the user asks for code examples in programming or solutions in Calculus and Discrete Math, you must answer and provide relevant links.

6. All of your replies should be in a glossary-like format.

7. When users ask about Discrete Math, Calculus, or Programming, you should mention how the topic enhances:
   - Logical Thinking
   - Analytical Thinking
   - Critical Thinking

8. When the user asks a question about the allowed subjects, say: "Thank you for asking, here is your answer," and provide the answer with an explanation, along with a website link related to their question.

9. If the user asks about topics outside of the subjects you are designed to cover, respond with: "I'm sorry, I can only answer queries regarding Programming such as python, c++ and java and mathematics such as calculus and discrete math. Is there any queries that I can help you?"

Limits:
You will only answer questions about Discrete Math, Calculus, and Basic Programming fundamentals in Java, C++, and Python. If the user asks about anything else, respond with: "I'm sorry, for I only answer queries regarding Programming such as python, c++ and java and mathematics such as calculus and discrete math.Is there any queries that I can help you."
    """
)

@app.route('/')
def index():
    return render_template('index.html')

def call_api_with_retry(user_input, retries=3):
    backoff = 2  # Start with a 2-second delay for backoff
    for attempt in range(retries):
        try:
            # Start a new chat session for each request to ensure fresh context
            chat_session = model.start_chat(history=[])
            response = chat_session.send_message(user_input)
            if response:
                print(f"Response received on attempt {attempt + 1}")
                return response
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            if '429' in str(e):  # Check for rate-limiting error (429)
                print(f"Rate limit exceeded. Retrying after {backoff} seconds...")
            time.sleep(backoff)  # Delay before retrying
            backoff *= 2  # Double the delay each attempt
    print("Failed to get response after retries")
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
            print("No response received from chatbot.")
            return jsonify({"response": "No response from the chatbot."})
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({"response": "An error occurred while processing your request. Please try again later."})

def format_response(response_text):
    """
    Format the response to preserve code block indentation.
    """
    formatted_text = ""
    in_code_block = False

    for line in response_text.split("\n"):
        if line.strip().startswith("```"):  # Detect code block boundaries
            if not in_code_block:
                formatted_text += "<pre><code>"  # Start code block
                in_code_block = True
            else:
                formatted_text += "</code></pre>"  # End code block
                in_code_block = False
        else:
            if in_code_block:
                formatted_text += f"{line}\n"  # Preserve indentation in code
            else:
                formatted_text += f"<p>{line.strip()}</p>"  # Regular text

    if in_code_block:  # Close any unclosed code block
        formatted_text += "</code></pre>"

    return formatted_text

if __name__ == '__main__':
    app.run(debug=True)
