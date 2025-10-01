from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
import google.generativeai as genai
import requests
import os

app = Flask(__name__)
CORS(app)

# Configure APIs from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')
google_api_key = os.getenv('GOOGLE_AI_KEY')
hugging_face_token = os.getenv('HUGGING_FACE_TOKEN')

if google_api_key:
    genai.configure(api_key=google_api_key)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_content():
    try:
        user_input = request.json.get('prompt')
        
        # Try AI services in order
        if openai.api_key:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"Act as AuraSEO AI - a professional SEO expert. {user_input}"}],
                max_tokens=1000
            )
            result = response.choices[0].message.content
            engine_used = "openai"
            
        elif google_api_key:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(f"Act as AuraSEO AI - a professional SEO expert. {user_input}")
            result = response.text
            engine_used = "google"
            
        elif hugging_face_token:
            API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
            headers = {"Authorization": f"Bearer {hugging_face_token}"}
            payload = {"inputs": f"Act as AuraSEO AI - a professional SEO expert. {user_input}"}
            response = requests.post(API_URL, headers=headers, json=payload)
            result = response.json()[0]['generated_text']
            engine_used = "huggingface"
            
        else:
            result = "Please configure AI API keys in environment variables."
            engine_used = "none"
            
        return jsonify({"success": True, "result": result, "engine_used": engine_used})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
