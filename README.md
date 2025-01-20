# Healthcare Translation Web App with Generative AI

This is a Flask-based web application designed to facilitate real-time multilingual communication between patients and healthcare providers. The app enables text translation, text-to-speech (TTS) synthesis, and real-time interaction using Generative AI and Google Cloud services.

---

## Features

- **Text Translation:** Real-time, context-sensitive translations using Google Gemini AI.
- **Text-to-Speech (TTS):** Converts translated text to speech, ensuring accessibility and ease of understanding.
- **Multilingual Support:** Supports multiple languages for seamless communication.
- **Web-Based Interface:** User-friendly interface with mobile-first design.
- **Secure API Integration:** All keys and credentials are securely managed via environment variables.

---

## Technology Stack

- **Backend:**
  - Python 3.9+
  - Flask
  - Google Generative AI (`google.generativeai`)
  - Google Cloud Text-to-Speech API
  - Google Cloud Speech-to-Text API

- **Frontend:**
  - HTML/CSS/JavaScript (Static files served via Flask)

- **Deployment:**
  - Compatible with platforms like Vercel, Heroku, or any server supporting Flask.

---

## Installation and Setup

### Prerequisites
- Python 3.9 or higher
- A Google Cloud project with enabled Speech-to-Text and Text-to-Speech APIs
- Environment variables:
  - `GEMINI_API_KEY_BASE64`: Base64-encoded Google Gemini API key
  - `GOOGLE_APPLICATION_CREDENTIALS`: Base64-encoded Google service account key JSON

---

1. **Install Dependencies**  
   Run the following command to install all required Python packages:  

   ```bash
   pip install -r requirements.txt
