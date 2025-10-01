from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
import google.generativeai as genai
import requests
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configure APIs from environment variables
try:
    openai_api_key = os.getenv('OPENAI_API_KEY')
    google_api_key = os.getenv('GOOGLE_AI_KEY')
    hugging_face_token = os.getenv('HUGGING_FACE_TOKEN')
    
    if openai_api_key:
        openai.api_key = openai_api_key
        logger.info("OpenAI API configured")
    
    if google_api_key:
        genai.configure(api_key=google_api_key)
        logger.info("Google AI configured")
        
    if hugging_face_token:
        logger.info("Hugging Face token loaded")
        
except Exception as e:
    logger.error(f"Error configuring APIs: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_content():
    try:
        user_input = request.json.get('prompt', '')
        logger.info(f"Received request: {user_input[:50]}...")
        
        if not user_input:
            return jsonify({"success": False, "error": "No prompt provided"})
        
        result = "AI service temporarily unavailable. Please check API configuration."
        engine_used = "none"
        
        # Try AI services in order
        if openai_api_key:
            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": f"Act as AuraSEO AI - a professional SEO expert. {user_input}"}],
                    max_tokens=500
                )
                result = response.choices[0].message.content
                engine_used = "openai"
                logger.info("OpenAI request successful")
                
            except Exception as e:
                logger.error(f"OpenAI error: {e}")
                # Fall through to next service
        
        if engine_used == "none" and google_api_key:
            try:
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(f"Act as AuraSEO AI - a professional SEO expert. {user_input}")
                result = response.text
                engine_used = "google"
                logger.info("Google AI request successful")
                
            except Exception as e:
                logger.error(f"Google AI error: {e}")
                # Fall through to next service
        
        if engine_used == "none" and hugging_face_token:
            try:
                API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
                headers = {"Authorization": f"Bearer {hugging_face_token}"}
                payload = {"inputs": f"Act as AuraSEO AI - a professional SEO expert. {user_input}"}
                response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()[0]['generated_text']
                    engine_used = "huggingface"
                    logger.info("Hugging Face request successful")
                else:
                    logger.error(f"Hugging Face API error: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Hugging Face error: {e}")
        
        return jsonify({
            "success": True, 
            "result": result, 
            "engine_used": engine_used,
            "message": "AuraSEO AI completed your request"
        })
        
    except Exception as e:
        logger.error(f"General error: {e}")
        return jsonify({
            "success": False, 
            "error": f"Service temporarily unavailable: {str(e)}"
        })

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "message": "AuraSEO AI is running"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
