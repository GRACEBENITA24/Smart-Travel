import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
from langdetect import detect
from googletrans import Translator
import re

# ---------------- CONFIG -----------------
# st.set_page_config(page_title="AI Tour Guide", layout="wide")

# Load Gemini API key from secrets.toml
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", "")
if not GOOGLE_API_KEY:
    st.error("⚠ GOOGLE_API_KEY not found in secrets.toml")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------------- LANGUAGES ----------------
indian_languages = {
    "English": "en",
    "Hindi": "hi",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Bengali": "bn",
    "Gujarati": "gu",
    "Marathi": "mr",
    "Punjabi": "pa",
}

foreign_languages = {
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    "Italian": "it",
    "Russian": "ru",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese (Mandarin)": "zh-cn",
    "Arabic": "ar",
}

languages = {**indian_languages, **foreign_languages}

translator = Translator()

# ---------------- UTILITY FUNCTIONS ----------------
def clean_text_for_audio(text):
    """Remove emojis, markdown, and extra symbols for TTS"""
    text = re.sub(r"[*#\n]", " ", text)
    text = re.sub(r"[^\w\s.,!?]", "", text)  # remove remaining emojis/special chars
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# ---------------- CACHED GEMINI CALL ----------------
@st.cache_data
def get_place_info(place, lang):
    prompt = f"""
    Imagine you are a lively tourist guide explaining {place}.
    Reply in {lang}. Keep it simple, fun, and engaging.
    Structure your answer as:

    📖 Introduction: 4–5 lines, friendly & detailed
    ⭐ Attractions: 5–6 bullet points with short descriptions
    💡 Travel Tips: 3–4 practical tips for tourists

    Avoid reading emojis in audio. Make it informative and enjoyable.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠ Error fetching Gemini response: {e}"

@st.cache_data
def get_doubt_answer(place, doubt, lang):
    prompt = f"""
    You are guiding a tourist about {place}.
    They asked: "{doubt}".
    Reply in {lang}, keep it clear, detailed, and friendly.
    Add 1 fun fact or travel tip if relevant. Avoid emojis for audio.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠ Error fetching Gemini response: {e}"

# ---------------- MAIN FUNCTION ----------------
def ai_tour_guide():
    st.title("🏰 AI Tour Guide (Voice + Multi-language + Q&A)")
    st.write("🎤 Speak or type a place name, get detailed tourist-friendly info, and ask doubts!")

    if "last_place" not in st.session_state:
        st.session_state.last_place = None

    # ---------------- LANGUAGE SELECTION ----------------
    st.subheader("🌍 Select reply language")
    lang_group = st.radio("Choose Language Group:", ["Indian Languages", "Foreign Languages"])
    if lang_group == "Indian Languages":
        selected_lang = st.selectbox("Select Language:", list(indian_languages.keys()))
        lang_code = indian_languages[selected_lang]
    else:
        selected_lang = st.selectbox("Select Language:", list(foreign_languages.keys()))
        lang_code = foreign_languages[selected_lang]

    # ---------- VOICE INPUT ----------
    st.subheader("🎤 Speak a Place Name")
    if st.button("Start Listening"):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:
            st.info("🎙 Listening... Please say the place name clearly.")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            spoken_text = recognizer.recognize_google(audio)
            st.success(f"✅ You said: {spoken_text}")

            # Translate to English if needed for Gemini
            input_lang = detect(spoken_text)
            place_en = translator.translate(spoken_text, src=input_lang, dest='en').text if input_lang != "en" else spoken_text
            st.session_state.last_place = place_en

            explanation = get_place_info(place_en, selected_lang)

            st.markdown(f"### 📖 Description")
            st.write(explanation)

            # Clean text for TTS
            clean_explanation = clean_text_for_audio(explanation)
            tts = gTTS(text=clean_explanation, lang=lang_code)
            tts.save("tour_guide.mp3")
            st.audio("tour_guide.mp3", format="audio/mp3")

        except Exception as e:
            st.error(f"⚠ Voice recognition error: {e}")

    # ---------- DOUBT CLEARING ----------
    st.subheader("❓ Ask a Doubt about the Place")
    if st.button("Ask Doubt (Voice)"):
        if not st.session_state.last_place:
            st.warning("⚠ First select a place before asking doubts.")
        else:
            recognizer = sr.Recognizer()
            mic = sr.Microphone()
            with mic as source:
                st.info("🎙 Listening for your doubt...")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

            try:
                doubt_text = recognizer.recognize_google(audio)
                st.success(f"✅ You asked: {doubt_text}")

                input_lang = detect(doubt_text)
                doubt_en = translator.translate(doubt_text, src=input_lang, dest='en').text if input_lang != "en" else doubt_text

                answer = get_doubt_answer(st.session_state.last_place, doubt_en, selected_lang)

                st.markdown(f"### 💡 Answer")
                st.write(answer)

                clean_answer = clean_text_for_audio(answer)
                tts = gTTS(text=clean_answer, lang=lang_code)
                tts.save("doubt_answer.mp3")
                st.audio("doubt_answer.mp3", format="audio/mp3")

            except Exception as e:
                st.error(f"⚠ Error while recognizing doubt: {e}")

    # ---------- TEXT INPUT ----------
    st.subheader("⌨ Type a Place Name")
    place_text = st.text_input("Enter a place name:")
    if st.button("Submit Place"):
        if place_text.strip():
            input_lang = detect(place_text)
            place_en = translator.translate(place_text, src=input_lang, dest='en').text if input_lang != "en" else place_text
            st.session_state.last_place = place_en

            explanation = get_place_info(place_en, selected_lang)

            st.markdown(f"### 📖 Description")
            st.write(explanation)

            clean_explanation = clean_text_for_audio(explanation)
            tts = gTTS(text=clean_explanation, lang=lang_code)
            tts.save("tour_guide.mp3")
            st.audio("tour_guide.mp3", format="audio/mp3")
        else:
            st.warning("⚠ Please enter a place before submitting.")

# ---------------- MAIN APP ----------------
if __name__ == "__main__":
    ai_tour_guide()
