from flask import Flask, render_template, jsonify, request
from google.cloud import speech
from google.cloud import texttospeech
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import base64

# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")

# Load environment variables
load_dotenv()

# Google Gemini API Key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# Get the Google credentials from the environment variable
google_credentials = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
if not google_credentials:
    raise ValueError("Missing GOOGLE_CREDENTIALS environment variable")

# Decode the Base64-encoded credentials
credentials_dict = json.loads(
    base64.b64decode(google_credentials).decode("utf-8")
)

# Initialize the Google Cloud client using the credentials
client = speech.SpeechClient.from_service_account_info(credentials_dict)

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
        # Set up the text-to-speech request
        synthesis_input = texttospeech.SynthesisInput(text=translated_text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        # Call the API to synthesize the speech
        response = tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # Save the audio file to static folder
        with open('static/translated_audio.mp3', 'wb') as out:
            out.write(response.audio_content)

        return jsonify({'message': 'Audio generated successfully'}), 200

    except Exception as e:
        return jsonify({'error': f'Error with speech synthesis: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
