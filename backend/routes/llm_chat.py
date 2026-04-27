import openai
from flask import Blueprint, request, jsonify
import os
llm_chat_bp = Blueprint('llm_chat', __name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@llm_chat_bp.route('/api/llm_chat', methods=['POST'])
def llm_chat():
    data = request.get_json()
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        client = openai.OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for students."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150,
            temperature=0.7
        )
        bot_reply = response.choices[0].message.content
        return jsonify({'reply': bot_reply})
    except Exception as e:
        print("OpenAI API error:", e)
        return jsonify({'error': str(e)}), 500