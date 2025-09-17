import streamlit as st
import os
import base64

# ----------------- PAGE CONFIG -----------------
st.set_page_config(page_title="TravelSmart India", layout="wide")

# ----------------- IMPORT ALL FUNCTION MODULES -----------------
from chatbot import ai_tour_guide
from finalhistoryapp import clip_landmark_detector
from translator import speech_translator
from finalmap import crime_aware_route_planner
from new1 import tourism_recommendation_system

# ----------------- FUNCTION TO LOAD IMAGE AS BASE64 -----------------
def get_base64_of_image(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# ----------------- FUNCTION TO SET BACKGROUND -----------------
def set_background(image_path):
    if os.path.exists(image_path):
        base64_image = get_base64_of_image(image_path)
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{base64_image}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.error(f"⚠️ {image_path} not found. Please place it in the same folder as your app.")

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

# ----------------- DISPLAY SELECTED PAGE -----------------
if menu_choice == "🏠 Home":
    set_background("background.jpg")   # Home background
    st.markdown(
        """
        <style>
        .overlay-container {
            text-align: center;
            padding-top: 20%;
        }
        .overlay-title {
            font-size: 3.5rem;
            font-weight: bold;
            text-shadow: 2px 2px 8px black;
            color: white;
            margin-bottom: 15px;
        }
        .overlay-subtext {
            font-size: 1.8rem;
            font-weight: normal;
            text-shadow: 1px 1px 6px black;
            color: #f0f0f0;
        }
        </style>

        <div class="overlay-container">
            <div class="overlay-title">Welcome to TravelSmart India!!</div>
            <div class="overlay-subtext">Your Smart Companion for Safe and Fun Travel ✈️</div>
        </div>
        """,
        unsafe_allow_html=True
    )

elif menu_choice == "🤖 Smart Tour Guide":
    set_background("background_features1.jpg")   # Features background
    st.markdown('<div class="feature-container">', unsafe_allow_html=True)
    st.header("🤖 Smart Tour Guide")
    ai_tour_guide()
    st.markdown('</div>', unsafe_allow_html=True)

elif menu_choice == "📍 Landmark Lens":
    set_background("background_features1.jpg")   # Features background
    st.markdown('<div class="feature-container">', unsafe_allow_html=True)
    st.header("🗺️ Landmark Lens")
    clip_landmark_detector()
    st.markdown('</div>', unsafe_allow_html=True)

elif menu_choice == "🌐 Voice-to-Voice Translator":
    set_background("background_features1.jpg")   # Features background
    st.markdown('<div class="feature-container">', unsafe_allow_html=True)
    st.header("🎙 Voice-to-Voice Translator")
    speech_translator()
    st.markdown('</div>', unsafe_allow_html=True)

elif menu_choice == "🛡️ Safe Route Planner":
    set_background("background_features1.jpg")   # Features background
    st.markdown('<div class="feature-container">', unsafe_allow_html=True)
    st.header("🛡 Safe Route Planner")
    crime_aware_route_planner()
    st.markdown('</div>', unsafe_allow_html=True)

elif menu_choice == "✨ TravelSmart Recommendations":
    set_background("background_features1.jpg")   # Features background
    st.markdown('<div class="feature-container">', unsafe_allow_html=True)
    st.header("🏨 TravelSmart Recommendations")
    tourism_recommendation_system()
    st.markdown('</div>', unsafe_allow_html=True)
