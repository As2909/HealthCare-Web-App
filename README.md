# Healthcare Translation Web App with Generative AI  

A **web-based prototype** that enables **real-time, multilingual translation** between patients and healthcare providers. It includes functionalities such as voice-to-text conversion, real-time translation, and audio playback, tailored specifically for medical interactions.  

---

## **Features**
- **Voice-to-Text Conversion:** Converts spoken input into text using Google Cloud Speech-to-Text API, optimized for medical terminology.
- **Real-Time Translation:** Translates input text into the desired language with context-specific accuracy using Google Generative AI.
- **Audio Playback:** Provides translated text as audio playback using the `pyttsx3` library.
- **Mobile-First Design:** Fully responsive web application for use on mobile and desktop devices.

---

## **Technologies Used**
- **Frontend:**
  - HTML5, CSS3, JavaScript
- **Backend:**
  - Python (Flask framework)
- **APIs:**
  - Google Cloud Speech-to-Text API
  - Google Generative AI (Gemini)
- **Other Tools:**
  - `pyttsx3` for text-to-speech synthesis
  - `.env` for secure API key management

---

1. **Install Dependencies**  
   Run the following command to install all required Python packages:  

   ```bash
   pip install -r requirements.txt
