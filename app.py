from flask import Flask, request, jsonify
import os
import openai  # Modified import statement

app = Flask(__name__)

# Initialize OpenAI client with the API key
openai.api_key = os.getenv("OPENAI_API_KEY")  # Ensure to set this in your environment variables

# User management with passwords
users = {
    "user1@example.com": {"budget": 10, "tokens_used": 0, "password": "securepassword1"},
    "user2@example.com": {"budget": 10, "tokens_used": 0, "password": "securepassword2"},
    # Add more users as needed
}

# Update this list based on the models you want to support
VALID_MODELS = ["gpt-3.5-turbo", "gpt-4"]  # Add other valid model names here

@app.route('/api/request', methods=['POST'])
def handle_request():
    data = request.json
    email = data.get('user')
    tokens = data.get('tokens', 1)  # Default to 1 token if not provided
    password = data.get('password')
    model = data.get('model')

    # Check if user exists and validate password
    if email in users:
        user_data = users[email]
        if user_data['password'] != password:
            return jsonify({"error": "Invalid password."}), 403
    else:
        return jsonify({"error": "User not found."}), 404

    # Validate model ID
    if model not in VALID_MODELS:
        return jsonify({"error": "Invalid model ID."}), 400

    # Continue with token usage and budget logic
    estimated_cost = calculate_cost(tokens, model)
    if estimated_cost <= user_data["budget"]:
        user_data["tokens_used"] += tokens
        user_data["budget"] -= estimated_cost
        try:
            # Call OpenAI API with the specified model using the client
            response = openai.ChatCompletion.create(  # Modified the OpenAI API call
                model=model,
                messages=[{"role": "user", "content": "Hello!"}],  # Replace with dynamic content if needed
                max_tokens=tokens
            )
            return jsonify({
                "message": "Request allowed.",
                "response": response.choices[0].message['content'].strip(),
                "estimated_cost": estimated_cost
            }), 200
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    else:
        return jsonify({"error": "Budget exceeded."}), 403

def calculate_cost(tokens, model):
    cost_per_token = get_cost_per_token(model)  # Get the cost per token for the selected model
    return tokens * cost_per_token

def get_cost_per_token(model):
    model_costs = {
        "gpt-3.5-turbo": 0.002,  # Example cost for GPT-3.5 Turbo
        "gpt-4": 0.03,           # Example cost for GPT-4
        # Add other models and their costs as needed
    }
    return model_costs.get(model, 0.002)  # Default cost for unknown models

if __name__ == '__main__':
    app.run(debug=True)
