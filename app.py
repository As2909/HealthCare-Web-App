from flask import Flask, render_template, jsonify, request
from google.cloud import speech
import pyttsx3
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
load_dotenv()

# Google Gemini API Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Google Speech API Key
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Speech to Text API client setup (Google)
client = speech.SpeechClient()

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Set up the model for content generation and translation
generation_config = {
    "temperature": 0.2,
    "top_p": 0.8,
    "top_k": 64,
    "max_output_tokens": 8192,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",  # Set the model 
    generation_config=generation_config,
)

# Function to translate text
def translate_text(text, source_language, target_language):
    prompt = f"Translate the following medical context text from {source_language} to {target_language}: \"{text}\""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()  # Get the translated text
    except Exception as e:
        print(f"Error translating text: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    text = request.json.get('text')
    source_lang = request.json.get('source_lang')
    target_lang = request.json.get('target_lang')

    if not text:
        return jsonify({'error': 'No text provided for translation'}), 400

    if not source_lang or not target_lang:
        return jsonify({'error': 'Source or target language missing'}), 400

    try:
        translated_text = translate_text(text, source_lang, target_lang)
        
        if translated_text:
            return jsonify({'translated_text': translated_text}), 200
        else:
            return jsonify({'error': 'Translation failed, please try again.'}), 500
    except Exception as e:
        return jsonify({'error': f'Error during translation: {str(e)}'}), 500

@app.route('/speak', methods=['POST'])
def speak_text():
    translated_text = request.json.get('text')

    if not translated_text:
        return jsonify({'error': 'No text provided for speech synthesis'}), 400

    try:
        engine.save_to_file(translated_text, 'static/translated_audio.mp3')
        engine.runAndWait()
        return jsonify({'message': 'Audio generated successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Error with speech synthesis: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
