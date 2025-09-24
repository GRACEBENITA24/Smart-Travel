import streamlit as st
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
from gtts.lang import tts_langs
import tempfile
import os
import threading



# playsound import with a fix for Windows (use playsound version 1.2.2)
try:
    from playsound import playsound
except ImportError:
    st.error("Please install playsound: pip install playsound==1.2.2")
    raise

#st.set_page_config(page_title="Speech Translator", page_icon="🎙", layout="centered")

#st.title("🎙 Speech Translator with Auto Language Detection")
#st.markdown("<h1 style='text-align:center; color:#2c3e50;'>🎙 Speech Translator with Auto Language Detection</h1>", unsafe_allow_html=True)



# Get available TTS languages and sort by language name
available_langs = tts_langs()
# invert to list of tuples for dropdown (lang_name, lang_code)
lang_options = sorted([(name.title(), code) for code, name in available_langs.items()])

# ---------------- FUNCTION ----------------
def speech_translator():
    def record_audio():
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("🎙 Listening... Please speak now.")
            audio = recognizer.listen(source)
        st.success("✅ Recording complete")
        return audio

    def transcribe_audio(audio):
        recognizer = sr.Recognizer()
        try:
            text = recognizer.recognize_google(audio)
            st.write(f"📝 Recognized Text: {text}")
            return text
        except sr.UnknownValueError:
            st.error("❌ Could not understand audio")
        except sr.RequestError:
            st.error("❌ Could not request results from Google")
        return ""

    def translate_text(text, target_lang):
        detected = translator.detect(text)
        source_lang = detected.lang
        st.write(f"🔍 Detected source language: {source_lang}")
        translated = translator.translate(text, src=source_lang, dest=target_lang)
        st.write(f"🌐 Translated Text ({target_lang}): {translated.text}")
        return translated.text

    def speak_text(text, lang_code):
        if lang_code not in available_langs:
            st.warning(f"❌ Text-to-speech not supported for language '{lang_code}'")
            return
        
        tts = gTTS(text=text, lang=lang_code)
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)  # Close so gTTS can write
        
        try:
            tts.save(path)
            
            # Play audio in separate thread to avoid blocking Streamlit UI
            def play_audio():
                playsound(path)
                if os.path.exists(path):
                    os.remove(path)
                    
            threading.Thread(target=play_audio, daemon=True).start()
            
        except Exception as e:
            st.error(f"Error playing audio: {e}")

    # UI: language selection dropdown with names, default English
    st.subheader("Select Target Language")
    selected_lang_name = st.selectbox(
        "Choose language", 
        [name for name, code in lang_options], 
        index=[name for name, code in lang_options].index("English")
    )
    target_language = dict(lang_options)[selected_lang_name]

    st.markdown("---")

    if st.button("🎤 Record & Translate"):
        audio = record_audio()
        original_text = transcribe_audio(audio)

        if original_text:
            translated_text = GoogleTranslator(source='auto', target='en').translate("Bonjour")
            speak_text(translated_text, target_language)

# ---------------- MAIN APP ----------------
if __name__ == "__main__":
    speech_translator()
