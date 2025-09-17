import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
from langdetect import detect
from googletrans import Translator

# ---------------- CONFIG -----------------
#st.set_page_config(page_title="AI Tour Guide", layout="wide")

# Gemini API setup
GOOGLE_API_KEY = "AIzaSyDjmgfJZIePzZNPm8z2seSI-R-ihH6liro"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------------- LANGUAGES ----------------
languages = {
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

translator = Translator()

# ---------------- FUNCTION ----------------
def ai_tour_guide():
    #st.sidebar.title("🎙 AI Tour Guide (Gemini Multi-language + Q&A)")
    #st.title("🏰 AI Tour Guide (Voice + Multi-language + Q&A)")
    st.write("🎤 Speak or type a place name, get a tourist-friendly description, and ask doubts!")

    selected_lang = st.selectbox("🌍 Select reply language:", list(languages.keys()))
    lang_code = languages[selected_lang]

    if "last_place" not in st.session_state:
        st.session_state.last_place = None

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
            input_lang = detect(spoken_text)
            st.success(f"✅ You said: {spoken_text} (Detected language: {input_lang})")

            # Translate to English if needed
            spoken_text_en = translator.translate(spoken_text, src=input_lang, dest='en').text if input_lang != "en" else spoken_text
            st.session_state.last_place = spoken_text_en

            # Gemini prompt
            prompt = (
                f"Explain about {spoken_text_en} as a tourist guide. "
                f"Make it short, crisp, easy to understand, and engaging. "
                f"Reply in {selected_lang}."
            )
            response = model.generate_content(prompt)
            explanation = response.text

            st.markdown(f"### 📖 {selected_lang} Description")
            st.write(explanation)

            tts = gTTS(text=explanation, lang=lang_code)
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
                input_lang = detect(doubt_text)
                doubt_text_en = translator.translate(doubt_text, src=input_lang, dest='en').text if input_lang != "en" else doubt_text
                st.success(f"✅ You asked: {doubt_text} (Detected language: {input_lang})")

                prompt = (
                    f"The user is learning about {st.session_state.last_place}. "
                    f"They asked this doubt: {doubt_text_en}. "
                    f"Answer clearly in {selected_lang}, keeping it simple."
                )
                response = model.generate_content(prompt)
                answer = response.text

                st.markdown(f"### 💡 Answer in {selected_lang}")
                st.write(answer)

                tts = gTTS(text=answer, lang=lang_code)
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
            place_text_en = translator.translate(place_text, src=input_lang, dest='en').text if input_lang != "en" else place_text
            st.session_state.last_place = place_text_en

            prompt = (
                f"Explain about {place_text_en} as a tourist guide. "
                f"Make it short, crisp, easy to understand, and engaging. "
                f"Reply in {selected_lang}."
            )
            response = model.generate_content(prompt)
            explanation = response.text

            st.markdown(f"### 📖 {selected_lang} Description")
            st.write(explanation)

            tts = gTTS(text=explanation, lang=lang_code)
            tts.save("tour_guide.mp3")
            st.audio("tour_guide.mp3", format="audio/mp3")
        else:
            st.warning("⚠ Please enter a place before submitting.")

# ---------------- MAIN APP ----------------
if __name__ == "__main__":
    ai_tour_guide()

