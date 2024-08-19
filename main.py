from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import openai

app = Flask(__name__)

# Initialize CORS
CORS(app)

# Initialize your OpenAI API key or any other model you are using
openai.api_key = 'your-openai-api-key'

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Get the input message from the request
        input_message = request.json.get('message')
        if not input_message:
            return jsonify({"error": "No message provided"}), 400

        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful teacher for your students. You will explain the questions whatever students ask."),
                ("human", "{input_message}")
            ]
        )

        # Initialize the ChatGroq model
        llm = ChatGroq(
            model="llama3-70b-8192",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            groq_api_key="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"
        )

        # Combine prompt and model
        chain = prompt | llm

        # Get the result from the model
        result = chain.invoke({"input_message": input_message})
        result_content = result.content

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
