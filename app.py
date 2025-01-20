import os
import base64
import tempfile
import logging
from flask import Flask, render_template, jsonify, request
from google.cloud import speech, texttospeech
from google.oauth2 import service_account
import google.generativeai as genai
from dotenv import load_dotenv

# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Decode the Base64-encoded GEMINI API key
encoded_key = os.getenv("GEMINI_API_KEY_BASE64")
if not encoded_key:
    raise ValueError("Missing GEMINI_API_KEY_BASE64 environment variable")

try:
    decoded_api_key = base64.b64decode(encoded_key).decode()
except Exception as e:
    logging.error(f"Failed to decode API key: {e}")
    raise
    
# Google Decoded Gemini API Key
genai.configure(api_key=decoded_api_key)

# Load Google Credentials
try:
    google_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not google_credentials:
        raise ValueError("Missing GOOGLE_APPLICATION_CREDENTIALS environment variable")

    decoded_credentials = base64.b64decode(google_credentials).decode("utf-8")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
        temp_file.write(decoded_credentials.encode("utf-8"))
        temp_credentials_path = temp_file.name

    credentials = service_account.Credentials.from_service_account_file(temp_credentials_path)
    speech_client = speech.SpeechClient(credentials=credentials)
    tts_client = texttospeech.TextToSpeechClient(credentials=credentials)
    logging.info("Google Cloud clients initialized successfully.")
finally:
    if temp_credentials_path and os.path.exists(temp_credentials_path):
        os.remove(temp_credentials_path)

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
    prompt = (
        f"You are a medical translator facilitating communication between patients and healthcare providers. "
        f"Your task is to provide accurate, context-sensitive translations of medical phrases, ensuring clarity and precision. "
        f"Translate the following text from {source_language} to {target_language}, ensuring only the translated content is provided. "
        f"Do not include explanations, notes, or any additional text in the response: \"{text}\""
    )
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logging.error(f"Error translating text: {str(e)}")
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
        logging.error(f"Error during translation: {str(e)}")
        return jsonify({'error': f'Error during translation: {str(e)}'}), 500

@app.route('/speak', methods=['POST'])
def speak_text():
    translated_text = request.json.get('text')

    if not translated_text:
        return jsonify({'error': 'No text provided for speech synthesis'}), 400

    try:
        synthesis_input = texttospeech.SynthesisInput(text=translated_text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        audio_file_path = 'static/translated_audio.mp3'
        with open(audio_file_path, 'wb') as out:
            out.write(response.audio_content)

        return jsonify({'message': 'Audio generated successfully', 'audio_url': audio_file_path}), 200
    except Exception as e:
        logging.error(f"Error with speech synthesis: {str(e)}")
        return jsonify({'error': f'Error with speech synthesis: {str(e)}'}), 500

logging.info(f"Running in environment: {os.getenv('VERCEL_ENV')}")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
