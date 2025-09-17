import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

# ---------------- FUNCTION ----------------
def crime_aware_route_planner():
    #st.set_page_config(page_title="Crime-Aware Route Planner", layout="wide")
    #st.title("🛡 Crime-Aware Route Planner with Voice Assistant")

    # -------------------------------
    # Read tourist spots from CSV
    # -------------------------------
    tourist_df = pd.read_csv("tourist.csv")

    # Generate JS code to add tourist markers (🏛)
    tourist_js = ""
    for _, row in tourist_df.iterrows():
        tourist_js += f"""
        L.marker([{row['lat']}, {row['lng']}], {{
          icon: L.divIcon({{className: 'tourist-icon', html: '🏛', iconSize: [25, 25]}})
        }})
        .bindPopup("<b>{row['name']}</b>")
        .addTo(map);
        """

    # -------------------------------
    # Full HTML + JS code
    # -------------------------------
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
    </div>
    <div id="map"></div>

    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.js"></script>
    <script src="https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.js"></script>

    <script>
    var map = L.map('map').setView([13.0827, 80.2707], 12);
    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
      attribution: '&copy; OpenStreetMap contributors'
    }}).addTo(map);

    var routingControl = null;
    var liveLocation = null;
    var lastRouteInstructions = "";
    var repeatInterval = null;

    // -------------------------------
    // Crime Hotspots
    // -------------------------------
    var hotspots = [
      {{ lat: 13.1208, lng: 80.2296, level: "High" }},
      {{ lat: 13.0500, lng: 80.2824, level: "Medium" }},
      {{ lat: 13.0464, lng: 80.2599, level: "High" }},
      {{ lat: 13.0335, lng: 80.2670, level: "High" }},
      {{ lat: 13.0823, lng: 80.2707, level: "Medium" }},
      {{ lat: 12.9242, lng: 80.1000, level: "Medium" }},
      {{ lat: 12.9675, lng: 80.1508, level: "Medium" }},
      {{ lat: 13.0878, lng: 80.2785, level: "High" }},
      {{ lat: 13.0740, lng: 80.2565, level: "Medium" }},
      {{ lat: 13.0604, lng: 80.2496, level: "High" }},
      {{ lat: 12.9981, lng: 80.1960, level: "High" }},
      {{ lat: 12.9345, lng: 80.1270, level: "Medium" }},
      {{ lat: 13.1167, lng: 80.3017, level: "High" }},
      {{ lat: 13.1548, lng: 80.2312, level: "Medium" }},
      {{ lat: 13.0051, lng: 80.2691, level: "High" }},
      {{ lat: 13.0455, lng: 80.2157, level: "High" }},
      {{ lat: 12.8446, lng: 80.2258, level: "Medium" }}
    ];

    hotspots.forEach(h => {{
      L.circleMarker([h.lat, h.lng], {{
        color: h.level === "High" ? "red" : "orange",
        radius: 8
      }}).bindPopup("Crime Level: " + h.level).addTo(map);
    }});

    // -------------------------------
    // Tourist spots markers (🏛)
    // -------------------------------
    {tourist_js}

    // -------------------------------
    // Hotels from Overpass API (🏨)
    // -------------------------------
    function loadHotels() {{
      var query = `
        [out:json][timeout:25];
        node["tourism"="hotel"](12.8,80.0,13.3,80.4);
        out;
      `;
      fetch("https://overpass-api.de/api/interpreter", {{
        method: "POST",
        body: query
      }})
      .then(res => res.json())
      .then(data => {{
        data.elements.forEach(hotel => {{
          if (hotel.lat && hotel.lon) {{
            L.marker([hotel.lat, hotel.lon], {{
              icon: L.divIcon({{className: 'hotel-icon', html: '🏨', iconSize: [25,25]}})
            }})
            .bindPopup("<b>Hotel</b>")
            .addTo(map);
          }}
        }});
      }});
    }}
    loadHotels();

    // -------------------------------
    // Routing Functions
    // -------------------------------
    function checkHotspot(route) {{
      for (let leg of route.routes[0].coordinates) {{
        for (let hotspot of hotspots) {{
          let distance = map.distance([leg.lat, leg.lng], [hotspot.lat, hotspot.lng]);
          if (distance < 200 && hotspot.level === "High") return hotspot;
        }}
      }}
      return null;
    }}

    function findSafeDetour(startCoords, endCoords, hotspot) {{
      let midLat = (startCoords.lat + endCoords.lat) / 2;
      let midLng = (startCoords.lng + endCoords.lng) / 2;
      return {{ lat: midLat + (hotspot.lat - midLat) * -1, lng: midLng + (hotspot.lng - midLng) * -1 }};
    }}

    function plotRoute(startCoords, endCoords) {{
      if (routingControl) map.removeControl(routingControl);

      routingControl = L.Routing.control({{
        waypoints: [L.latLng(startCoords.lat, startCoords.lng), L.latLng(endCoords.lat, endCoords.lng)],
        routeWhileDragging: false,
        router: L.Routing.osrmv1({{ serviceUrl: "https://router.project-osrm.org/route/v1" }}),
        lineOptions: {{ styles: [{{ color: 'blue', opacity: 0.8, weight: 6 }}] }},
        createMarker: function() {{ return null; }}
      }}).on('routesfound', function(e) {{
        let hotspot = checkHotspot(e);
        if (hotspot) {{
          alert("⚠ Warning! Your route passes through a high-crime area.");
          let safeDetour = findSafeDetour(startCoords, endCoords, hotspot);
          rerouteAvoidingCrime(startCoords, endCoords, safeDetour);
        }} else {{
          lastRouteInstructions = e.routes[0].instructions.map(i => i.text).join(". ");
          speak("Safe route found. " + lastRouteInstructions);
        }}
      }}).addTo(map);
    }}

    function rerouteAvoidingCrime(startCoords, endCoords, safeDetour) {{
      if (routingControl) map.removeControl(routingControl);

      routingControl = L.Routing.control({{
        waypoints: [L.latLng(startCoords.lat, startCoords.lng), L.latLng(safeDetour.lat, safeDetour.lng), L.latLng(endCoords.lat, endCoords.lng)],
        routeWhileDragging: false,
        router: L.Routing.osrmv1({{ serviceUrl: "https://router.project-osrm.org/route/v1" }}),
        lineOptions: {{ styles: [{{ color: 'green', opacity: 0.9, weight: 6 }}] }},
        createMarker: function() {{ return null; }}
      }}).addTo(map);
    }}

    // -------------------------------
    // Voice Assistant
    // -------------------------------
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

    // -------------------------------
    // Location + Voice Input
    // -------------------------------
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
          alert("Unable to fetch GPS location. Please allow location permissions or use HTTPS.");
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

    # Render HTML in Streamlit
    components.html(html_code, height=800, scrolling=True)

# ---------------- MAIN APP ----------------
if __name__ == "__main__":
    crime_aware_route_planner()
