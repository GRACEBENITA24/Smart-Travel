import streamlit as st
import os
import base64

# ----------------- PAGE CONFIG -----------------
st.set_page_config(page_title="TravelSmart India", layout="wide")

# ----------------- IMPORT FUNCTION MODULES -----------------
from chatbot2 import ai_tour_guide
from finalhistoryapp import clip_landmark_detector
from translator import speech_translator
from maplegend import crime_aware_route_planner
from recommendapp import travel_assistant_app

# ----------------- HELPER FUNCTIONS -----------------
def get_base64_of_image(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(image_path):
    if os.path.exists(image_path):
        base64_image = get_base64_of_image(image_path)
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{base64_image}");
                background-size: cover;      /* 🔹 fills entire screen */
                background-position: center; /* 🔹 keeps it centered */
                background-repeat: no-repeat;
                background-attachment: fixed;
                background-color: #000;      /* 🔹 fallback color */
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.error(f"⚠ {image_path} not found!")

def inject_css():
    st.markdown("""
    <style>
    /* General text styling */
    .overlay-title {
        font-size: 3rem;
        font-weight: bold;
        text-shadow: 2px 2px 8px black;
        color: white;
        margin-bottom: 10px;
        animation: fadeIn 1.5s ease-in-out;
    }
    .overlay-subtext {
        font-size: 1.5rem;
        text-shadow: 1px 1px 6px black;
        color: #f0f0f0;
        animation: fadeIn 2s ease-in-out;
    }
    /* Cards */
    .card {
        background: rgba(255,255,255,0.85);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        transition: transform 0.3s;
    }
    .card:hover { transform: scale(1.05); }
    /* Animations */
    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(20px);}
        to {opacity: 1; transform: translateY(0);}
    }
    </style>
    """, unsafe_allow_html=True)

# ----------------- SIDEBAR MENU -----------------
st.sidebar.title("🌏 TravelSmart India")
menu_choice = st.sidebar.radio(
    "Explore Features:",
    [
        "🏠 Home",
        "🤖 Smart Tour Guide",
        "📍 Landmark Lens",
        "🌐 Voice-to-Voice Translator",
        "🛡️ Safe Route Planner",
        "✨ TravelSmart Recommendations"
    ]
)

inject_css()

# ----------------- PAGES -----------------
if menu_choice == "🏠 Home":
    set_background("sky.jpg")
    st.markdown(
        """
        <div class="overlay-container" style="text-align:center; padding-top:15%;">
            <div class="overlay-title">Welcome to TravelSmart India!!</div>
            <div class="overlay-subtext">Your Smart Companion for Safe and Fun Travel ✈️</div>
        </div>
        """,
        unsafe_allow_html=True
    )

elif menu_choice == "🤖 Smart Tour Guide":
    set_background("background_features1.jpg")
    #st.header("🤖 Smart Tour Guide")
    with st.spinner("Loading AI Tour Guide..."):
        ai_tour_guide()

elif menu_choice == "📍 Landmark Lens":
    set_background("background_features2.jpg")
    #st.header("📍 Landmark Lens")
    clip_landmark_detector()

elif menu_choice == "🌐 Voice-to-Voice Translator":
    set_background("background_features3.jpg")
    st.markdown("<h1 style='text-align:center; color:#2c3e50;'>🎙 Speech Translator with Auto Language Detection</h1>", unsafe_allow_html=True)
    #st.header("🌐 Voice-to-Voice Translator")
    speech_translator()

elif menu_choice == "🛡️ Safe Route Planner":
    set_background("background_features4.jpg")
    #st.header("🛡️ Safe Route Planner")
    crime_aware_route_planner()

elif menu_choice == "✨ TravelSmart Recommendations":
    set_background("background_features5.jpg")
    #st.header("✨ TravelSmart Recommendations")
    travel_assistant_app("recommend.csv")
