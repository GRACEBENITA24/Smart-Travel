import streamlit as st
import pandas as pd
import requests
from geopy.geocoders import Nominatim

def travel_assistant_app(csv_file="recommend.csv"):
    # ------------------ Load CSV ------------------
    df = pd.read_csv(csv_file)

    # ------------------ Step 1: Get Approx Location from IP ------------------
    def get_location_from_ip():
        try:
            res = requests.get("https://ipinfo.io/json", timeout=5).json()
            loc = res["loc"].split(",")
            lat, lon = float(loc[0]), float(loc[1])
            state = res.get("region", None)
            return lat, lon, state
        except Exception:
            return None, None, None

    # ------------------ Step 2: Reverse Geocode ------------------
    def get_state_from_coords(lat, lon, fallback_state=None):
        try:
            geolocator = Nominatim(user_agent="tourist_app")
            location = geolocator.reverse((lat, lon), exactly_one=True, language="en", timeout=10)
            if location and "address" in location.raw:
                state = location.raw["address"].get("state", fallback_state)
                return state
        except Exception:
            return fallback_state
        return fallback_state

    # ------------------ Helper to show apps neatly ------------------
    def render_app_list(title, apps, links, icon="📱", color="#f8f9fa"):
        st.markdown(
            f"""
            <div style="background:{color}; padding:15px; border-radius:12px; margin-bottom:15px; box-shadow:0 2px 6px rgba(0,0,0,0.1);">
                <h4 style="margin-bottom:10px;">{icon} {title}</h4>
            """,
            unsafe_allow_html=True,
        )
        if pd.notna(apps) and pd.notna(links):
            app_list = [app.strip() for app in str(apps).split(",")]
            link_list = [lnk.strip() for lnk in str(links).split("|")]
            for i, (app, lnk) in enumerate(zip(app_list, link_list), start=1):
                st.markdown(f"{i}. 👉 [{app}]({lnk})")
        else:
            st.write("❌ No apps available.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ------------------ MAIN ------------------
    #st.set_page_config(page_title="Travel Assistant", layout="wide")
    st.markdown("<h1 style='text-align:center; color:#2c3e50;'>🧳 Travel Assistant – Smart Recommendations</h1>", unsafe_allow_html=True)

    # Sidebar
    st.sidebar.header("⚙️ Options")
    use_live_location = st.sidebar.checkbox("Use Live Location")
    if use_live_location:
        lat, lon, fallback_state = get_location_from_ip()
        if lat and lon:
            state = get_state_from_coords(lat, lon, fallback_state)
        else:
            st.sidebar.error("❌ Could not fetch live location.")
            state = None
    else:
        state = st.sidebar.selectbox("Select State/UT", df["State/UT"].unique())

    # ------------------ Show Recommendations ------------------
    if state:
        st.markdown(f"<h2>✨ Recommendations for <span style='color:#16a085'>{state}</span></h2>", unsafe_allow_html=True)
        row = df[df["State/UT"].str.lower() == state.lower()].iloc[0]

        col1, col2 = st.columns(2)
        with col1:
            render_app_list("Taxi Apps", row["Taxi Apps"], row["Taxi App Links"], "🚕", "#eafaf1")
            render_app_list("Hotel Apps", row["Hotel Apps"], row["Hotel App Links"], "🏨", "#fef9e7")
            render_app_list("Emergency Apps", row["Emergency Apps"], row["Emergency App Links"], "🚨", "#fdecea")
        with col2:
            render_app_list("Tourism Apps", row["Tourism Apps"], row["Tourism App Links"], "🏝", "#e8f4fd")
            render_app_list("Food Apps", row["Food Apps"], row["Food App Links"], "🍔", "#f4ecf7")

        # Famous Foods
        st.markdown(
            f"""
            <div style="background:#fdf2e9; padding:15px; border-radius:12px; margin-bottom:15px; box-shadow:0 2px 6px rgba(0,0,0,0.1);">
                <h4>🍲 Famous Foods</h4>
                ✅ {row['Famous Food 1']} <br> 
                ✅ {row['Famous Food 2']} <br> 
                ✅ {row['Famous Food 3']} 
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Famous Purchases
        st.markdown(
            f"""
            <div style="background:#f5eef8; padding:15px; border-radius:12px; margin-bottom:15px; box-shadow:0 2px 6px rgba(0,0,0,0.1);">
                <h4>🛍 Famous Purchases</h4>
                🛒 {row['🛍 Famous Purchases']}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Special Features
        st.markdown("### 🌟 Special Features")
        cols = st.columns(3)
        features = [row["Special Feature 1"], row["Special Feature 2"], row["Special Feature 3"]]
        for col, feat in zip(cols, features):
            col.markdown(f"<div style='background:#d6eaf8; padding:12px; border-radius:10px; text-align:center; font-weight:600;'>{feat}</div>", unsafe_allow_html=True)
# ------------------ CALL THE FUNCTION ------------------
if __name__ == "__main__":
    travel_assistant_app("recommend.csv")