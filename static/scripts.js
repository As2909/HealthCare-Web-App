document.addEventListener('DOMContentLoaded', function () {
    const startSpeechBtn = document.getElementById('startSpeechBtn');
    const speechStatus = document.getElementById('speechStatus');
    const originalTextDisplay = document.getElementById('originalTextDisplay');
    const translatedTextDisplay = document.getElementById('translatedTextDisplay');
    const speakBtn = document.getElementById('speakBtn');
    const audioPlayback = document.getElementById('audioPlayback');

    const sourceLang = document.getElementById('sourceLang');
    const targetLang = document.getElementById('targetLang');

    let recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.continuous = true;
    recognition.interimResults = true;

    // Start Speech Recognition
    startSpeechBtn.addEventListener('click', function () {
        recognition.start();
        speechStatus.textContent = 'Status: Listening...';
    });

    // When speech is recognized, display original text and translate it
    recognition.onresult = function (event) {
        let transcript = event.results[event.results.length - 1][0].transcript;
        originalTextDisplay.textContent = transcript;

        // Translate the speech into the target language
        const sourceLanguage = sourceLang.value;
        const targetLanguage = targetLang.value;

        fetch('/translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: transcript,
                source_lang: sourceLanguage,
                target_lang: targetLanguage
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.translated_text) {
                translatedTextDisplay.textContent = data.translated_text;
                // Enable the speak button
                speakBtn.style.display = 'inline-block';
            } else {
                translatedTextDisplay.textContent = 'Translation failed. Please try again.';
            }
        })
        .catch(error => {
            translatedTextDisplay.textContent = 'Error during translation: ' + error;
        });
    };

    // Speak Translated Text
    speakBtn.addEventListener('click', function () {
        const translatedText = translatedTextDisplay.textContent;
        fetch('/speak', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: translatedText
            })
        })
        .then(response => response.blob()) // Get the audio blob directly
        .then(blob => {
            const audioUrl = URL.createObjectURL(blob); // Create an object URL for the audio blob
            audioPlayback.src = audioUrl; // Set the source to the new audio URL
            audioPlayback.play(); // Play the audio
        })
        .catch(error => {
            console.log('Error during speech synthesis:', error);
        });
    });
