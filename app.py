import os
import base64
import tempfile
import logging
import io
import google.generativeai as genai
from flask import Flask, render_template, jsonify, request
from flask import send_file
from google.cloud import speech, texttospeech
from google.oauth2 import service_account
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
    # Decode the API key for use with the generative AI model
    decoded_api_key = base64.b64decode(encoded_key).decode()
except Exception as e:
    logging.error(f"Failed to decode API key: {e}")
    raise

# Configure the generative AI model with the decoded API key
genai.configure(api_key=decoded_api_key)

# Load Google Cloud credentials
try:
    google_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not google_credentials:
        raise ValueError("Missing GOOGLE_APPLICATION_CREDENTIALS environment variable")

    # Decode the credentials and write them to a temporary file
    decoded_credentials = base64.b64decode(google_credentials).decode("utf-8")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
        temp_file.write(decoded_credentials.encode("utf-8"))
        temp_credentials_path = temp_file.name

    # Initialize Google Cloud clients for speech and text-to-speech
    credentials = service_account.Credentials.from_service_account_file(temp_credentials_path)
    speech_client = speech.SpeechClient(credentials=credentials)
    tts_client = texttospeech.TextToSpeechClient(credentials=credentials)
    logging.info("Google Cloud clients initialized successfully.")
finally:
    # Clean up the temporary credentials file
    if temp_credentials_path and os.path.exists(temp_credentials_path):
        os.remove(temp_credentials_path)

# Set up the model for content generation and translation
generation_config = {
    "temperature": 0.2,
    "top_p": 0.8,
    "top_k": 64,
    "max_output_tokens": 8192,
}

# Initialize the generative AI model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",  # Specify the model name
    generation_config=generation_config,
)

def translate_text(text, source_language, target_language):
    """
    Translate text from a source language to a target language using a generative AI model.

    Args:
        text (str): The text to be translated.
        source_language (str): The language code of the source text.
        target_language (str): The language code of the target text.

    Returns:
        str: The translated text, or None if an error occurs.
    """
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
    """
    Render the main HTML page.

    Returns:
        Response: The rendered HTML page.
    """
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    """
    Handle translation requests.

    Expects JSON data with 'text', 'source_lang', and 'target_lang' keys.

    Returns:
        Response: JSON response with translated text or an error message.
    """
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
    """
    Convert translated text to speech and return an audio file.

    Expects JSON data with 'text' key.

    Returns:
        Response: Audio file or an error message.
    """
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
        # Serve audio file directly
        audio_stream = io.BytesIO(response.audio_content)
        audio_stream.seek(0)
        return send_file(
            audio_stream,
            mimetype="audio/mpeg",
            as_attachment=False,
            download_name="translated_audio.mp3"
        )
    except Exception as e:
        logging.error(f"Error with speech synthesis: {str(e)}")
        return jsonify({'error': f'Error with speech synthesis: {str(e)}'}), 500

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, host="0.0.0.0", port=5000)
