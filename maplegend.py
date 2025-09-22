import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import random
import threading
import time
import requests

# ---------------- AI Agent Layer ----------------
def simulate_ai_updates(hotspots_file="hotspots.csv"):
    while True:
        try:
            df = pd.read_csv(hotspots_file)
            if "risk_level" not in df.columns:
                df["risk_level"] = [random.randint(1, 5) for _ in range(len(df))]
            else:
                for i in range(len(df)):
                    change = random.choice([-1, 0, 1])
                    new_level = max(1, min(5, df.at[i, "risk_level"] + change))
                    df.at[i, "risk_level"] = new_level
            df.to_csv(hotspots_file, index=False)
        except Exception as e:
            print("AI Agent error:", e)
        time.sleep(30)  # update every 30s

# Start AI simulation in background ONLY ONCE
if "ai_thread_started" not in st.session_state:
    threading.Thread(target=simulate_ai_updates, daemon=True).start()
    st.session_state["ai_thread_started"] = True

# ---------------- IP-based Location Fallback ----------------
def get_location_from_ip():
    try:
        res = requests.get("https://ipinfo.io/json", timeout=5).json()
        loc = res["loc"].split(",")
        lat, lon = float(loc[0]), float(loc[1])
        return lat, lon
    except Exception as e:
        print("Error fetching IP location:", e)
        return None, None

# ---------------- FUNCTION ----------------
def crime_aware_route_planner():
    #st.title("🛡 Crime-Aware Route Planner with AI Agent Layer")
    st.markdown("<h1 style='text-align:center; color:#2c3e50;'>🛡 Crime-Aware Route Planner</h1>", unsafe_allow_html=True)


    # Load datasets
    tourist_df = pd.read_csv("landmarks.csv")
    hotspot_df = pd.read_csv("hotspots.csv")

    # Tourist category icons
    category_icons = {
        "Monuments & Heritage Sites": "🏛",
        "Forts & Palaces": "🏰",
        "Temples & Religious Sites": "🛕",
        "Caves & Ancient Sites": "⛰",
        "Natural Wonders & Scenic Spots": "🌄",
        "Wildlife & National Parks": "🐅",
        "Modern Attractions": "🎡"
    }

    # Risk color mapping
    risk_colors = {1: "green", 2: "yellow", 3: "orange", 4: "red", 5: "black"}

    # Generate JS code for tourist spots
    tourist_js = ""
    for _, row in tourist_df.iterrows():
        icon = category_icons.get(row["Category"], "📍")
        tourist_js += f"""
        L.marker([{row['Lat']}, {row['Lng']}], {{
          icon: L.divIcon({{className: 'tourist-icon', html: '{icon}', iconSize: [25, 25]}})
        }}).bindPopup("<b>{row['Name']}</b><br>Category: {row['Category']}").addTo(touristLayer);
        """

    # Generate JS code for hotspots (initial load)
    hotspot_js = ""
    for _, row in hotspot_df.iterrows():
        risk = int(row.get("risk_level", 3))
        color = risk_colors.get(risk, "red")
        hotspot_js += f"""
        var marker_{_} = L.circleMarker([{row['lat']}, {row['lng']}], {{
          color: "{color}",
          radius: 8,
          fillOpacity: 0.7
        }}).bindPopup("⚠ Crime Hotspot<br>Risk Level: {risk}").addTo(hotspotLayer);
        hotspotMarkers.push({{marker: marker_{_}, lat: {row['lat']}, lng: {row['lng']}}});
        """

    # Get IP location fallback
    ip_lat, ip_lon = get_location_from_ip()
    ip_lat = ip_lat or 13.0827
    ip_lon = ip_lon or 80.2707

    # ------------------------------- HTML + JS -------------------------------
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crime-Aware Route Planner</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.css" />
    <style>
      #map {{ height: 85vh; width: 100%; margin-top: 10px; }}
      #controls {{
        padding: 10px;
        background: #f9f9f9;
        display: flex;
        gap: 8px;
        align-items: center;
        flex-wrap: wrap;
        border-radius: 8px;
      }}
      input {{ padding: 6px; width: 200px; border-radius: 4px; border: 1px solid #ccc; }}
      button {{ padding: 6px 10px; cursor: pointer; border: none; border-radius: 4px; }}
      button.voice {{ background: #007bff; color: white; }}
      button.action {{ background: #28a745; color: white; }}
      button.loc {{ background: #ff5722; color: white; }}
      button.assist {{ background: #6f42c1; color: white; }}
      button.stop {{ background: #dc3545; color: white; }}
      button.toggle {{ background: #ffc107; color: black; }}
      .legend {{ background:white; padding:10px; line-height:1.5; border-radius:5px; }}
    </style>
    </head>
    <body>
    <div id="controls">
      <input type="text" id="startLocation" placeholder="Enter Start Location">
      <button class="voice" onclick="startVoiceInput('startLocation')">🎤 Start</button>
      
      <input type="text" id="endLocation" placeholder="Enter End Location">
      <button class="voice" onclick="startVoiceInput('endLocation')">🎤 End</button>
      
      <button class="action" onclick="calculateRoute()">Find Route</button>
      <button class="loc" onclick="useLiveLocation()">📍 Use Live Location</button>
      
      <button class="assist" onclick="startRepeatingAssistant()">🔊 Start Assistant</button>
      <button class="stop" onclick="stopRepeatingAssistant()">⏹ Stop Assistant</button>
      
      <button class="toggle" onclick="toggleHotspots()">👮 Toggle Hotspots</button>
    </div>
    <div id="map"></div>

    <div class="legend" id="legend">
      <b>Crime Risk Levels (Hotspots):</b><br>
      🟢 1 Safe<br>
      🟡 2 Caution<br>
      🟠 3 Risky<br>
      🔴 4 Dangerous<br>
      ⚫ 5 Extreme
    </div>

    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.js"></script>
    <script src="https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.js"></script>

    <script>
    var map = L.map('map').setView([{ip_lat}, {ip_lon}], 12);
    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
      attribution: '&copy; OpenStreetMap contributors'
    }}).addTo(map);

    var routingControl = null;
    var liveLocation = null;
    var lastRouteInstructions = "";
    var repeatInterval = null;

    var touristLayer = L.layerGroup().addTo(map);
    var hotspotLayer = L.layerGroup();
    var hotspotMarkers = [];

    // Tourist spots
    {tourist_js}

    // Hotspots (initial load)
    {hotspot_js}

    // Smooth color transition for hotspot risk updates
    async function refreshHotspots() {{
      try {{
        const res = await fetch("hotspots.csv");
        const data = await res.text();
        const rows = data.split("\\n").slice(1);
        rows.forEach((row, idx) => {{
          if (!hotspotMarkers[idx]) return;
          const cols = row.split(",");
          const risk = parseInt(cols[3] || 3);
          const colorMap = {{1:"green",2:"yellow",3:"orange",4:"red",5:"black"}};
          let currentColor = hotspotMarkers[idx].marker.options.color;
          let newColor = colorMap[risk];
          if(currentColor !== newColor) {{
            // Animate color change smoothly
            hotspotMarkers[idx].marker.setStyle({{color: newColor, fillColor: newColor}});
            hotspotMarkers[idx].marker.bindPopup("⚠ Crime Hotspot<br>Risk Level: " + risk);
          }}
        }});
      }} catch(err) {{
        console.log("Hotspot refresh error:", err);
      }}
    }}

    setInterval(refreshHotspots, 30000); // Refresh every 30s

    // Toggle hotspots
    var hotspotsVisible = false;
    function toggleHotspots() {{
      if (hotspotsVisible) {{
        map.removeLayer(hotspotLayer);
        hotspotsVisible = false;
      }} else {{
        map.addLayer(hotspotLayer);
        hotspotsVisible = true;
      }}
    }}

    // Routing & voice assistant functions (unchanged)
    function plotRoute(startCoords, endCoords) {{
      if (routingControl) map.removeControl(routingControl);
      routingControl = L.Routing.control({{
        waypoints: [L.latLng(startCoords.lat, startCoords.lng), L.latLng(endCoords.lat, endCoords.lng)],
        routeWhileDragging: false,
        router: L.Routing.osrmv1({{ serviceUrl: "https://router.project-osrm.org/route/v1" }}),
        lineOptions: {{ styles: [{{ color: 'blue', opacity: 0.8, weight: 6 }}] }},
        createMarker: function() {{ return null; }}
      }}).on('routesfound', function(e) {{
        lastRouteInstructions = e.routes[0].instructions.map(i => i.text).join(". ");
        speak("Route found. " + lastRouteInstructions);
      }}).addTo(map);
    }}

    function speak(text) {{
      window.speechSynthesis.cancel();
      var msg = new SpeechSynthesisUtterance(text);
      msg.lang = "en-IN";
      window.speechSynthesis.speak(msg);
    }}
    function startRepeatingAssistant() {{
      if (!lastRouteInstructions) {{ alert("No route available yet!"); return; }}
      if (repeatInterval) clearInterval(repeatInterval);
      speak(lastRouteInstructions);
      repeatInterval = setInterval(() => speak(lastRouteInstructions), 30000);
    }}
    function stopRepeatingAssistant() {{
      if (repeatInterval) {{ clearInterval(repeatInterval); repeatInterval = null; }}
      window.speechSynthesis.cancel();
      alert("Voice assistant stopped.");
    }}

    function getCoordinates(address, callback) {{
      fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${{address}}`)
        .then(res => res.json())
        .then(data => {{
          if (data.length > 0) callback({{ lat: parseFloat(data[0].lat), lng: parseFloat(data[0].lon) }});
          else alert("Location not found!");
        }});
    }}
    function calculateRoute() {{
      let startInput = document.getElementById("startLocation").value;
      let endInput = document.getElementById("endLocation").value;
      if (!endInput) {{ alert("Please enter destination!"); return; }}
      getCoordinates(startInput, startCoords => {{
        getCoordinates(endInput, endCoords => {{
          plotRoute(startCoords, endCoords);
        }});
      }});
    }}
    function useLiveLocation() {{
      if (navigator.geolocation) {{
        navigator.geolocation.getCurrentPosition(pos => {{
          liveLocation = {{ lat: pos.coords.latitude, lng: pos.coords.longitude }};
          map.setView([liveLocation.lat, liveLocation.lng], 14);
          L.marker([liveLocation.lat, liveLocation.lng]).bindPopup("You are here").addTo(map);
          document.getElementById("startLocation").value = liveLocation.lat + "," + liveLocation.lng;
        }}, () => {{
          liveLocation = {{ lat: {ip_lat}, lng: {ip_lon} }};
          map.setView([liveLocation.lat, liveLocation.lng], 12);
          L.marker([liveLocation.lat, liveLocation.lng]).bindPopup("Approximate location").addTo(map);
          document.getElementById("startLocation").value = liveLocation.lat + "," + liveLocation.lng;
          alert("GPS blocked. Using approximate location based on IP.");
        }});
      }} else {{
        alert("Geolocation is not supported by your browser.");
      }}
    }}
    function startVoiceInput(fieldId) {{
      const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
      recognition.lang = "en-IN";
      recognition.start();
      recognition.onresult = function(event) {{
        const transcript = event.results[0][0].transcript;
        document.getElementById(fieldId).value = transcript;
      }};
    }}
    </script>
    </body>
    </html>
    """

    # Render in Streamlit
    components.html(html_code, height=850, scrolling=True)

# ---------------- MAIN APP ----------------
if __name__ == "__main__":
    crime_aware_route_planner()
