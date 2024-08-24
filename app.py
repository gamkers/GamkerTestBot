from flask import Flask, request, jsonify, session
from flask_cors import CORS
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import secrets 
from datetime import timedelta 

app = Flask(__name__)
app.secret_key = secrets.token_hex(16) # Necessary for session management
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
# Initialize CORS
CORS(app)


def get_model():
    """Lazy initialization of the ChatGroq model."""
    if 'model' not in session:
        llm = ChatGroq(
            model="llama3-70b-8192",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            groq_api_key="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"

        )
        session['model'] = True
    return llm



@app.route('/chat', methods=['POST'])
def chat():
    try:
        input_message = request.json.get('message')
        if not input_message:
            return jsonify({"error": "No message provided"}), 400

        # Initialize or retrieve conversation history
        if 'history' not in session:
            session['history'] = []

        # Append the new message to the history
        session['history'].append(("human", input_message))

        if len(session['history']) > 4:
            session['history'] = session['history'][-4:]

        # Create the prompt template with dynamic variables
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful teacher for your students. You will explain the questions whatever students ask. You will also remember the {previous_context}, but you don't need to mention the history every time."),
                ("human", "{input_message}"),
            ]
        )
        
        llm = get_model()
        # Combine prompt and model
        chain = prompt | llm

        # Invoke the chain with the input message and history
        result = chain.invoke({"input_message": input_message, "previous_context": session['history']})
        result_content = result.content

        # Append the model's response to the history
        session['history'].append(("ai", result_content))

        if len(session['history']) > 4:
            session['history'] = session['history'][-4:]

        # Log the result for debugging
        print(result_content)

        # Return the result as JSON response
        return jsonify({"reply": result_content})

    except Exception as e:
        # Handle any errors that occur
        print(f"Error: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)
