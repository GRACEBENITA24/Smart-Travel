import streamlit as st
import json
import pandas as pd

# ------------------------- FUNCTION -------------------------
def tourism_recommendation_system(json_path="new.json"):
    # Load JSON Data
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert list of dicts into dict with states as keys
    data_dict = {entry['state']: entry for entry in data}

    # Page Config
    #st.set_page_config(page_title="Tourism Recommendation System", page_icon="🛡", layout="wide")

    # Header
    #st.title("🛡 Tourism Recommendation System for India")
    st.markdown("Helping tourists explore India safely with verified **apps, food, and travel tips** 🌏✨")

    # Sidebar Filters
    with st.sidebar:
        st.header("🔍 Filters")
        state = st.selectbox("Select a State/UT", list(data_dict.keys()))

    # Main Content
    st.subheader(f"📍 Recommendations for {state}")
    entry = data_dict[state]

    # Mapping JSON keys to display categories with emojis
    categories = {
        "🚖 Taxi Apps": "taxi_apps",
        "🏨 Hotel Apps": "hotel_apps",
        "📱 Emergency Apps": "emergency_apps",
        "🗺️ Tourism Apps": "tourism_apps",
        "🍽️ Food Apps": "food_apps",
        "🍛 Famous Foods": "famous_foods",
        "✨ Special Features": "special_features",
        "🌐 Official Tourism Website": "official_website"
    }

    for cat_name, cat_key in categories.items():
        items = entry.get(cat_key, [])

        # Handle single website string separately
        if cat_name == "🌐 Official Tourism Website":
            if items:
                st.markdown(f"### {cat_name}")
                st.markdown(f"[Visit Here]({items})", unsafe_allow_html=True)
            continue

        if items:
            st.markdown(f"### {cat_name}")

            # If apps (dict with link) → clickable link column
            if isinstance(items[0], dict) and "app_name" in items[0]:
                df = pd.DataFrame([
                    {"App Name": app["app_name"], "Open Link": f"[🔗 Open]({app.get('app_link', '#')})"}
                    for app in items
                ])
                st.table(df)
            else:
                # Foods, features, or plain app names → enhanced table
                df = pd.DataFrame(items, columns=[cat_name])
                st.table(df)
        else:
            st.warning(f"⚠️ No items found in {cat_name}.")
