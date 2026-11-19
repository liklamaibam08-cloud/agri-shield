import io
import requests
import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="AgriShield — Crop Disease & Weather Monitor",
    page_icon="🌿",
    layout="wide",
)

# WMO weather code descriptions for Open-Meteo
WMO_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

# Sample crop knowledge base (Rice excluded)
DISEASE_GUIDES = {
    "Tomato": {
        "Early Blight": {
            "severity": "Moderate",
            "symptoms": "Concentric dark rings ('target spots') on older lower leaves, yellowing around spots.",
            "action": "Prune affected lower leaves, avoid overhead watering, and apply an approved copper or mancozeb fungicide.",
        },
        "Late Blight": {
            "severity": "High",
            "symptoms": "Water-soaked dark lesions on leaves/stems with white mold growth in humid weather.",
            "action": "Isolate and remove infected plants immediately to limit spore spread; consult local extension guidance.",
        },
        "Healthy Leaf": {
            "severity": "None",
            "symptoms": "Uniform green foliage without lesions, curling, or discoloration.",
            "action": "Continue regular monitoring, drip/base irrigation, and field scouting.",
        },
    },
    "Potato": {
        "Early Blight": {
            "severity": "Moderate",
            "symptoms": "Dark brown angular/concentric spots on foliage, premature leaf drop.",
            "action": "Maintain balanced soil nutrition, rotate crops, and use labeled protectant fungicides if needed.",
        },
        "Late Blight": {
            "severity": "High",
            "symptoms": "Pale green to dark brown water-soaked blotches on leaf tips and margins, rapid collapse in wet conditions.",
            "action": "Destroy infected foliage promptly, avoid working in wet fields, and follow local blight advisories.",
        },
        "Healthy Leaf": {
            "severity": "None",
            "symptoms": "Uniform green foliage without lesions, curling, or discoloration.",
            "action": "Continue regular monitoring, drip/base irrigation, and field scouting.",
        },
    },
}


@st.cache_data(ttl=600)
def fetch_weather(city: str) -> dict | None:
    """Fetch live weather, temperature, and relative humidity via Open-Meteo."""
    try:
        geo_res = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "en"},
            timeout=10,
        )
        geo_res.raise_for_status()
        results = geo_res.json().get("results")
        if not results:
            return None

        place = results[0]
        weather_res = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": "temperature_2m,relative_humidity_2m,weather_code",
                "timezone": "auto",
            },
            timeout=10,
        )
        weather_res.raise_for_status()
        current = weather_res.json().get("current", {})

        code = current.get("weather_code")
        return {
            "location": f"{place.get('name')}, {place.get('country', '')}".strip(", "),
            "condition": WMO_WEATHER_CODES.get(code, f"Weather code {code}"),
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "time": current.get("time"),
        }
    except requests.RequestException:
        return None


def assess_fungal_risk(temp_c: float | None, humidity: float | None) -> str:
    """Simple advisory banner based on ambient temperature and humidity."""
    if temp_c is None or humidity is None:
        return "Weather metrics unavailable for risk estimation."
    if humidity >= 80 and 15 <= temp_c <= 28:
        return "High fungal pressure: warm temperatures and >=80% humidity favor blight spread."
    if humidity >= 65:
        return "Moderate moisture: monitor lower canopy leaves and avoid late-evening overhead watering."
    return "Lower foliar fungal pressure under current temperature and humidity."


def run_diagnosis(image: Image.Image, crop: str) -> tuple[str, float, dict]:
    """Placeholder inference function; replace with your trained model."""
    candidates = list(DISEASE_GUIDES.get(crop, {}).items())
    width, height = image.size
    idx = (width + height) % len(candidates)
    condition, details = candidates[idx]
    confidence = min(0.78 + ((width * height) % 18) / 100.0, 0.96)
    return condition, confidence, details


st.title("🌿 AgriShield")
st.caption("Crop leaf diagnosis paired with live field weather, temperature, and humidity conditions.")

with st.sidebar:
    st.header("Field & Scan Settings")
    location_input = st.text_input("Farm / City Location", value="Hyderabad")
    crop = st.selectbox("Crop Type", ["Tomato", "Potato"])
    field_note = st.text_input("Plot / Field Note (optional)", placeholder="e.g., North plot, Row 4")

# Live Weather Section
st.subheader("Live Field Weather Conditions")
weather = fetch_weather(location_input.strip()) if location_input.strip() else None

if weather:
    st.caption(f"Location: **{weather['location']}** (Updated: {weather['time']})")
    w1, w2, w3 = st.columns(3)
    w1.metric("Weather Condition", weather["condition"])
    w2.metric("Temperature", f"{weather['temperature']} °C")
    w3.metric("Humidity", f"{weather['humidity']} %")
    st.info(assess_fungal_risk(weather["temperature"], weather["humidity"]))
else:
    st.warning("Could not load weather data for that location. Check the city name in the sidebar.")

st.divider()

# Image Upload & Diagnosis Section
col_upload, col_result = st.columns([1, 1.2], gap="large")

with col_upload:
    st.subheader("1. Upload Leaf Image")
    uploaded_file = st.file_uploader(
        "Choose a JPG, JPEG, or PNG image",
        type=["jpg", "jpeg", "png"],
    )

    if uploaded_file is not None:
        raw_bytes = uploaded_file.getvalue()
        pil_image = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
        st.image(
            pil_image,
            caption=f"{uploaded_file.name} ({pil_image.size[0]}×{pil_image.size[1]}px)",
            use_container_width=True,
        )
    else:
        pil_image = None
        st.write("No image uploaded yet.")

with col_result:
    st.subheader("2. Diagnosis & Guidance")
    analyze_clicked = st.button(
        "Run Diagnosis",
        type="primary",
        disabled=(pil_image is None),
        use_container_width=True,
    )

    if analyze_clicked and pil_image is not None:
        with st.spinner("Analyzing leaf image..."):
            condition, confidence, details = run_diagnosis(pil_image, crop)

        st.success(f"**Detected Condition:** {condition}")
        m1, m2 = st.columns(2)
        m1.metric("Confidence (Demo)", f"{confidence * 100:.1f}%")
        m2.metric("Severity", details["severity"])

        if field_note.strip():
            st.caption(f"Field note: {field_note.strip()}")

        st.markdown("**Observed Symptoms**")
        st.write(details["symptoms"])

        st.markdown("**Recommended Next Steps**")
        st.write(details["action"])
