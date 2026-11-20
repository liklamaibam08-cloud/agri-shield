import io
import requests
import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="AgriShield — Crop Disease & Weather Monitor",
    page_icon="🌿",
    layout="wide",
)

LANGUAGES = {
    "English": "en",
    "हिन्दी (Hindi)": "hi",
    "తెలుగు (Telugu)": "te",
    "Français (French)": "fr",
}

UI_TEXT = {
    "en": {
        "subtitle": "Crop leaf diagnosis paired with live field weather, temperature, and humidity conditions.",
        "sidebar_header": "Field & Scan Settings",
        "language_label": "Language",
        "location_label": "Farm / City Location",
        "crop_label": "Crop Type",
        "note_label": "Plot / Field Note (optional)",
        "note_placeholder": "e.g., North plot, Row 4",
        "weather_header": "Live Field Weather Conditions",
        "location_caption": "Location",
        "updated_caption": "Updated",
        "weather_metric": "Weather Condition",
        "temp_metric": "Temperature",
        "humidity_metric": "Humidity",
        "weather_error": "Could not load weather data for that location. Check the city name in the sidebar.",
        "risk_unavailable": "Weather metrics unavailable for risk estimation.",
        "risk_high": "High fungal pressure: warm temperatures and >=80% humidity favor blight spread.",
        "risk_mod": "Moderate moisture: monitor lower canopy leaves and avoid late-evening overhead watering.",
        "risk_low": "Lower foliar fungal pressure under current temperature and humidity.",
        "upload_header": "1. Upload Leaf Image",
        "uploader_label": "Choose a JPG, JPEG, or PNG image",
        "no_image": "No image uploaded yet.",
        "result_header": "2. Diagnosis & Guidance",
        "analyze_btn": "Run Diagnosis",
        "spinner": "Analyzing leaf image...",
        "detected": "Detected Condition",
        "confidence": "Confidence (Demo)",
        "severity": "Severity",
        "field_note_prefix": "Field note",
        "symptoms_header": "Observed Symptoms",
        "action_header": "Recommended Next Steps",
        "crops": {"Tomato": "Tomato", "Potato": "Potato"},
    },
    "hi": {
        "subtitle": "फसल की पत्तियों के रोग की पहचान और खेत के लाइव मौसम, तापमान व नमी की जानकारी।",
        "sidebar_header": "खेत और स्कैन सेटिंग्स",
        "language_label": "भाषा (Language)",
        "location_label": "खेत / शहर का स्थान",
        "crop_label": "फसल का प्रकार",
        "note_label": "खेत / प्लॉट नोट (वैकल्पिक)",
        "note_placeholder": "उदा., उत्तरी प्लॉट, पंक्ति 4",
        "weather_header": "खेत की लाइव मौसम स्थिति",
        "location_caption": "स्थान",
        "updated_caption": "अपडेट समय",
        "weather_metric": "मौसम की स्थिति",
        "temp_metric": "तापमान",
        "humidity_metric": "नमी (आर्द्रता)",
        "weather_error": "इस स्थान का मौसम डेटा लोड नहीं हो सका। साइडबार में शहर का नाम जांचें।",
        "risk_unavailable": "जोखिम आकलन के लिए मौसम डेटा उपलब्ध नहीं है।",
        "risk_high": "उच्च फफूंद जोखिम: गर्म तापमान और >=80% नमी झुलसा रोग फैला सकती है।",
        "risk_mod": "मध्यम नमी: निचली पत्तियों की निगरानी करें और शाम को ऊपर से सिंचाई से बचें।",
        "risk_low": "वर्तमान तापमान और नमी में पत्तियों पर फफूंद का जोखिम कम है।",
        "upload_header": "1. पत्ती की फोटो अपलोड करें",
        "uploader_label": "JPG, JPEG, या PNG इमेज चुनें",
        "no_image": "अभी तक कोई इमेज अपलोड नहीं की गई है।",
        "result_header": "2. रोग पहचान और सुझाव",
        "analyze_btn": "जांच शुरू करें",
        "spinner": "पत्ती की इमेज का विश्लेषण हो रहा है...",
        "detected": "पहचानी गई स्थिति",
        "confidence": "विश्वास स्तर (डेमो)",
        "severity": "गंभीरता",
        "field_note_prefix": "खेत नोट",
        "symptoms_header": "देखे गए लक्षण",
        "action_header": "अगले आवश्यक कदम",
        "crops": {"Tomato": "टमाटर (Tomato)", "Potato": "आलू (Potato)"},
    },
    "te": {
        "subtitle": "పంట ఆకుల వ్యాధి నిర్ధారణ మరియు పొలం యొక్క ప్రత్యక్ష వాతావరణం, ఉష్ణోగ్రత, తేమ వివరాలు.",
        "sidebar_header": "పొలం & స్కాన్ సెట్టింగ్‌లు",
        "language_label": "భాష (Language)",
        "location_label": "పొలం / నగరం పేరు",
        "crop_label": "పంట రకం",
        "note_label": "పొలం గమనిక (ఐచ్ఛికం)",
        "note_placeholder": "ఉదా., ఉత్తర భాగం, వరుస 4",
        "weather_header": "ప్రత్యక్ష వాతావరణ పరిస్థితులు",
        "location_caption": "ప్రదేశం",
        "updated_caption": "నవీకరించబడింది",
        "weather_metric": "వాతావరణ స్థితి",
        "temp_metric": "ఉష్ణోగ్రత",
        "humidity_metric": "తేమ శాతం",
        "weather_error": "ఈ ప్రదేశానికి వాతావరణ సమాచారం లోడ్ కాలేదు. సైడ్‌బార్‌లో నగరం పేరును తనిఖీ చేయండి.",
        "risk_unavailable": "ప్రమాద అంచనాకు వాతావరణ వివరాలు అందుబాటులో లేవు.",
        "risk_high": "అధిక శిలీంధ్ర (ఫంగల్) ప్రమాదం: వెచ్చని ఉష్ణోగ్రత మరియు >=80% తేమ తెగులు వ్యాప్తికి అనుకూలం.",
        "risk_mod": "మధ్యస్థ తేమ: కింది ఆకులను గమనిస్తూ ఉండండి మరియు సాయంత్రం పైనుండి నీరు పోయడం మానుకోండి.",
        "risk_low": "ప్రస్తుత ఉష్ణోగ్రత మరియు తేమ పరిస్థితుల్లో ఆకు తెగులు ప్రమాదం తక్కువగా ఉంది.",
        "upload_header": "1. ఆకు చిత్రాన్ని అప్‌లోడ్ చేయండి",
        "uploader_label": "JPG, JPEG, లేదా PNG చిత్రాన్ని ఎంచుకోండి",
        "no_image": "ఇంకా చిత్రం అప్‌లోడ్ చేయలేదు.",
        "result_header": "2. వ్యాధి నిర్ధారణ & సూచనలు",
        "analyze_btn": "నిర్ధారణ ప్రారంభించండి",
        "spinner": "ఆకు చిత్రాన్ని విశ్లేషిస్తోంది...",
        "detected": "గుర్తించిన స్థితి",
        "confidence": "నిర్ధారణ స్థాయి (డెమో)",
        "severity": "తీవ్రత",
        "field_note_prefix": "పొలం గమనిక",
        "symptoms_header": "గమనించిన లక్షణాలు",
        "action_header": "తీసుకోవాల్సిన చర్యలు",
        "crops": {"Tomato": "టమోటా (Tomato)", "Potato": "బంగాళాదుంప (Potato)"},
    },
    "fr": {
        "subtitle": "Diagnostic des maladies foliaires associé aux conditions météo, de température et d'humidité en direct.",
        "sidebar_header": "Paramètres du champ",
        "language_label": "Langue",
        "location_label": "Ville / Exploitation",
        "crop_label": "Culture",
        "note_label": "Note de parcelle (optionnel)",
        "note_placeholder": "ex. Parcelle Nord, Rang 4",
        "weather_header": "Conditions météo en direct",
        "location_caption": "Lieu",
        "updated_caption": "Mis à jour",
        "weather_metric": "Météo",
        "temp_metric": "Température",
        "humidity_metric": "Humidité",
        "weather_error": "Impossible de charger la météo pour ce lieu. Vérifiez le nom de la ville.",
        "risk_unavailable": "Données météo indisponibles pour estimer le risque.",
        "risk_high": "Pression fongique élevée : chaleur et humidité >=80 % favorisent le mildiou.",
        "risk_mod": "Humidité modérée : surveillez les feuilles basses et évitez l'arrosage par aspersion le soir.",
        "risk_low": "Faible pression fongique foliaire selon la température et l'humidité actuelles.",
        "upload_header": "1. Importer une photo de feuille",
        "uploader_label": "Choisir une image JPG, JPEG ou PNG",
        "no_image": "Aucune image importée pour le moment.",
        "result_header": "2. Diagnostic et conseils",
        "analyze_btn": "Lancer le diagnostic",
        "spinner": "Analyse de l'image en cours...",
        "detected": "État détecté",
        "confidence": "Confiance (Démo)",
        "severity": "Gravité",
        "field_note_prefix": "Note de parcelle",
        "symptoms_header": "Symptômes observés",
        "action_header": "Actions recommandées",
        "crops": {"Tomato": "Tomate", "Potato": "Pomme de terre"},
    },
}

WMO_WEATHER_CODES = {
    0: {"en": "Clear sky", "hi": "साफ़ आसमान", "te": "నిర్మలమైన ఆకాశం", "fr": "Ciel dégagé"},
    1: {"en": "Mainly clear", "hi": "मुख्यतः साफ़", "te": "ప్రధానంగా నిర్మలం", "fr": "Généralement dégagé"},
    2: {"en": "Partly cloudy", "hi": "आंशिक रूप से बादल", "te": "పాక్షికంగా మేఘావృతం", "fr": "Partiellement nuageux"},
    3: {"en": "Overcast", "hi": "घने बादल", "te": "మేఘావృతం", "fr": "Couvert"},
    45: {"en": "Fog", "hi": "कोहरा", "te": "పొగమంచు", "fr": "Brouillard"},
    48: {"en": "Depositing rime fog", "hi": "घना कोहरा", "te": "దట్టమైన పొగమంచు", "fr": "Brouillard givrant"},
    51: {"en": "Light drizzle", "hi": "हल्की बूंदाबांदी", "te": "తేలికపాటి చినుకులు", "fr": "Bruine légère"},
    53: {"en": "Moderate drizzle", "hi": "मध्यम बूंदाबांदी", "te": "మోస్తరు చినుకులు", "fr": "Bruine modérée"},
    55: {"en": "Dense drizzle", "hi": "तेज़ बूंदाबांदी", "te": "దట్టమైన చినుకులు", "fr": "Bruine dense"},
    61: {"en": "Slight rain", "hi": "हल्की बारिश", "te": "తేలికపాటి వర్షం", "fr": "Pluie faible"},
    63: {"en": "Moderate rain", "hi": "मध्यम बारिश", "te": "మోస్తరు వర్షం", "fr": "Pluie modérée"},
    65: {"en": "Heavy rain", "hi": "भारी बारिश", "te": "భారీ వర్షం", "fr": "Forte pluie"},
    80: {"en": "Slight rain showers", "hi": "हल्की बौछारें", "te": "తేలికపాటి జల్లులు", "fr": "Averses faibles"},
    81: {"en": "Moderate rain showers", "hi": "मध्यम बौछारें", "te": "మోస్తరు జల్లులు", "fr": "Averses modérées"},
    82: {"en": "Violent rain showers", "hi": "तेज़ बौछारें", "te": "భారీ జల్లులు", "fr": "Fortes averses"},
    95: {"en": "Thunderstorm", "hi": "आंधी-तूफ़ान", "te": "ఉరుములతో కూడిన వర్షం", "fr": "Orage"},
}

DISEASE_GUIDES = {
    "Tomato": [
        {
            "name": {
                "en": "Early Blight",
                "hi": "अगेती झुलसा (Early Blight)",
                "te": "ముందస్తు ఆకుమాడు తెగులు (Early Blight)",
                "fr": "Alternariose (Early Blight)",
            },
            "severity": {"en": "Moderate", "hi": "मध्यम", "te": "మధ్యస్థం", "fr": "Modérée"},
            "symptoms": {
                "en": "Concentric dark rings ('target spots') on older lower leaves, yellowing around spots.",
                "hi": "पुरानी निचली पत्तियों पर गहरे संकेंद्रित छल्ले और धब्बों के चारों ओर पीलापन।",
                "te": "కింది పాత ఆకులపై వలయాకారపు ముదురు మచ్చలు మరియు చుట్టూ పసుపు రంగు.",
                "fr": "Anneaux concentriques sombres sur les feuilles basses âgées avec jaunissement périphérique.",
            },
            "action": {
                "en": "Prune affected lower leaves, avoid overhead watering, and apply an approved copper or mancozeb fungicide.",
                "hi": "प्रभावित निचली पत्तियों को हटाएं, ऊपर से पानी न दें और अनुशंसित कॉपर या मैंकोज़ेब फफूंदनाशी का छिड़काव करें।",
                "te": "తెగులు సోకిన కింది ఆకులను తొలగించి, పైనుండి నీరు పోయకుండా సిఫార్సు చేసిన శిలీంధ్రనాశిని పిచికారీ చేయండి.",
                "fr": "Taillez les feuilles basses atteintes, évitez l'arrosage par aspersion et appliquez un fongicide homologué.",
            },
        },
        {
            "name": {
                "en": "Late Blight",
                "hi": "पछेती झुलसा (Late Blight)",
                "te": "ఆలస్య ఆకుమాడు తెగులు (Late Blight)",
                "fr": "Mildiou (Late Blight)",
            },
            "severity": {"en": "High", "hi": "उच्च", "te": "అధికం", "fr": "Élevée"},
            "symptoms": {
                "en": "Water-soaked dark lesions on leaves/stems with white mold growth in humid weather.",
                "hi": "पत्तियों और तनों पर पानी से भीगे गहरे धब्बे और नमी में सफेद फफूंद की परत।",
                "te": "ఆకులు, కాండాలపై నీటితో తడిసినట్లుండే ముదురు మచ్చలు మరియు తేమలో తెల్లటి బూజు.",
                "fr": "Lésions sombres d'aspect gorgé d'eau sur feuilles et tiges avec duvet blanc par temps humide.",
            },
            "action": {
                "en": "Isolate and remove infected plants immediately to limit spore spread; consult local extension guidance.",
                "hi": "संक्रमित पौधों को तुरंत अलग कर नष्ट करें ताकि बीजाणु न फैलें; कृषि विशेषज्ञ से सलाह लें।",
                "te": "వ్యాధి సోకిన మొక్కలను వెంటనే వేరు చేసి తొలగించండి; స్థానిక వ్యవసాయ నిపుణులను సంప్రదించండి.",
                "fr": "Isolez et retirez immédiatement les plants infectés pour limiter la propagation des spores.",
            },
        },
        {
            "name": {
                "en": "Healthy Leaf",
                "hi": "स्वस्थ पत्ती (Healthy Leaf)",
                "te": "ఆరోగ్యకరమైన ఆకు (Healthy Leaf)",
                "fr": "Feuille saine",
            },
            "severity": {"en": "None", "hi": "कोई नहीं", "te": "లేదు", "fr": "Aucune"},
            "symptoms": {
                "en": "Uniform green foliage without lesions, curling, or discoloration.",
                "hi": "बिना किसी धब्बे, मुड़ाव या पीलेपन के एकसमान हरी पत्तियां।",
                "te": "మచ్చలు, ముడతలు లేదా రంగు మార్పు లేకుండా సమానమైన ఆకుపచ్చ ఆకులు.",
                "fr": "Feuillage vert uniforme sans lésions, enroulement ni décoloration.",
            },
            "action": {
                "en": "Continue regular monitoring, drip/base irrigation, and field scouting.",
                "hi": "नियमित निगरानी, जड़ों के पास सिंचाई और खेत का निरीक्षण जारी रखें।",
                "te": "క్రమం తప్పకుండా పర్యవేక్షణ మరియు మొక్కల మొదళ్ల వద్ద నీటిపారుదల కొనసాగించండి.",
                "fr": "Poursuivez la surveillance régulière et l'irrigation au pied des plants.",
            },
        },
    ],
    "Potato": [
        {
            "name": {
                "en": "Early Blight",
                "hi": "अगेती झुलसा (Early Blight)",
                "te": "ముందస్తు ఆకుమాడు తెగులు (Early Blight)",
                "fr": "Alternariose (Early Blight)",
            },
            "severity": {"en": "Moderate", "hi": "मध्यम", "te": "మధ్యస్థం", "fr": "Modérée"},
            "symptoms": {
                "en": "Dark brown angular/concentric spots on foliage, premature leaf drop.",
                "hi": "पत्तियों पर गहरे भूरे कोणीय/गोल धब्बे और समय से पहले पत्तियों का गिरना।",
                "te": "ఆకులపై ముదురు గోధుమ రంగు మచ్చలు మరియు ఆకులు ముందుగానే రాలిపోవడం.",
                "fr": "Taches brun foncé anguleuses ou concentriques sur le feuillage, chute prématurée des feuilles.",
            },
            "action": {
                "en": "Maintain balanced soil nutrition, rotate crops, and use labeled protectant fungicides if needed.",
                "hi": "संतुलित पोषण बनाए रखें, फसल चक्र अपनाएं और आवश्यकतानुसार सुरक्षित फफूंदनाशी का उपयोग करें।",
                "te": "సమతుల్య పోషకాలు అందిస్తూ పంట మార్పిడి పాటించండి మరియు అవసరమైతే శిలీంధ్రనాశిని వాడండి.",
                "fr": "Maintenez une fertilisation équilibrée, pratiquez la rotation des cultures et traitez si nécessaire.",
            },
        },
        {
            "name": {
                "en": "Late Blight",
                "hi": "पछेती झुलसा (Late Blight)",
                "te": "ఆలస్య ఆకుమాడు తెగులు (Late Blight)",
                "fr": "Mildiou (Late Blight)",
            },
            "severity": {"en": "High", "hi": "उच्च", "te": "అధికం", "fr": "Élevée"},
            "symptoms": {
                "en": "Pale green to dark brown water-soaked blotches on leaf tips and margins, rapid collapse in wet conditions.",
                "hi": "पत्तियों के किनारों पर हल्के हरे से गहरे भूरे धब्बे और नमी में तेजी से सड़न।",
                "te": "ఆకుల అంచులపై లేత ఆకుపచ్చ నుండి ముదురు గోధుమ రంగు మచ్చలు మరియు తడి వాతావరణంలో వేగంగా కుళ్ళిపోవడం.",
                "fr": "Taches vert pâle à brun foncé sur les bords des feuilles, flétrissement rapide par temps humide.",
            },
            "action": {
                "en": "Destroy infected foliage promptly, avoid working in wet fields, and follow local blight advisories.",
                "hi": "संक्रमित पत्तियों को तुरंत नष्ट करें, गीले खेत में काम करने से बचें और स्थानीय सलाह का पालन करें।",
                "te": "తెగులు సోకిన ఆకులను వెంటనే నాశనం చేయండి మరియు తడి పొలంలో పనిచేయడం మానుకోండి.",
                "fr": "Détruisez rapidement le feuillage infecté et évitez d'intervenir dans les parcelles humides.",
            },
        },
        {
            "name": {
                "en": "Healthy Leaf",
                "hi": "स्वस्थ पत्ती (Healthy Leaf)",
                "te": "ఆరోగ్యకరమైన ఆకు (Healthy Leaf)",
                "fr": "Feuille saine",
            },
            "severity": {"en": "None", "hi": "कोई नहीं", "te": "లేదు", "fr": "Aucune"},
            "symptoms": {
                "en": "Uniform green foliage without lesions, curling, or discoloration.",
                "hi": "बिना किसी धब्बे, मुड़ाव या पीलेपन के एकसमान हरी पत्तियां।",
                "te": "మచ్చలు, ముడతలు లేదా రంగు మార్పు లేకుండా సమానమైన ఆకుపచ్చ ఆకులు.",
                "fr": "Feuillage vert uniforme sans lésions, enroulement ni décoloration.",
            },
            "action": {
                "en": "Continue regular monitoring, drip/base irrigation, and field scouting.",
                "hi": "नियमित निगरानी, जड़ों के पास सिंचाई और खेत का निरीक्षण जारी रखें।",
                "te": "క్రమం తప్పకుండా పర్యవేక్షణ మరియు మొక్కల మొదళ్ల వద్ద నీటిపారుదల కొనసాగించండి.",
                "fr": "Poursuivez la surveillance régulière et l'irrigation au pied des plants.",
            },
        },
    ],
}


@st.cache_data(ttl=600)
def fetch_weather(city: str, lang_code: str) -> dict | None:
    """Fetch live weather, temperature, and relative humidity via Open-Meteo."""
    try:
        geo_res = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": lang_code},
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
        code_map = WMO_WEATHER_CODES.get(code, {})
        condition_label = code_map.get(lang_code) or code_map.get("en") or f"Code {code}"

        return {
            "location": f"{place.get('name')}, {place.get('country', '')}".strip(", "),
            "condition": condition_label,
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "time": current.get("time"),
        }
    except requests.RequestException:
        return None


def assess_fungal_risk(temp_c: float | None, humidity: float | None, t: dict) -> str:
    if temp_c is None or humidity is None:
        return t["risk_unavailable"]
    if humidity >= 80 and 15 <= temp_c <= 28:
        return t["risk_high"]
    if humidity >= 65:
        return t["risk_mod"]
    return t["risk_low"]


def run_diagnosis(image: Image.Image, crop_key: str, lang_code: str) -> tuple[str, float, dict]:
    """Placeholder inference function; replace with your trained model."""
    candidates = DISEASE_GUIDES[crop_key]
    width, height = image.size
    entry = candidates[(width + height) % len(candidates)]
    confidence = min(0.78 + ((width * height) % 18) / 100.0, 0.96)
    details = {
        "severity": entry["severity"][lang_code],
        "symptoms": entry["symptoms"][lang_code],
        "action": entry["action"][lang_code],
    }
    return entry["name"][lang_code], confidence, details


# Sidebar with Language Switcher first
with st.sidebar:
    selected_lang_label = st.selectbox("🌐 Language / भाषा / భాష / Langue", list(LANGUAGES.keys()))
    lang = LANGUAGES[selected_lang_label]
    t = UI_TEXT[lang]

    st.header(t["sidebar_header"])
    location_input = st.text_input(t["location_label"], value="Hyderabad")
    crop_key = st.selectbox(
        t["crop_label"],
        options=["Tomato", "Potato"],
        format_func=lambda k: t["crops"][k],
    )
    field_note = st.text_input(t["note_label"], placeholder=t["note_placeholder"])

st.title("🌿 AgriShield")
st.caption(t["subtitle"])

# Live Weather Section
st.subheader(t["weather_header"])
weather = fetch_weather(location_input.strip(), lang) if location_input.strip() else None

if weather:
    st.caption(
        f"{t['location_caption']}: **{weather['location']}** "
        f"({t['updated_caption']}: {weather['time']})"
    )
    w1, w2, w3 = st.columns(3)
    w1.metric(t["weather_metric"], weather["condition"])
    w2.metric(t["temp_metric"], f"{weather['temperature']} °C")
    w3.metric(t["humidity_metric"], f"{weather['humidity']} %")
    st.info(assess_fungal_risk(weather["temperature"], weather["humidity"], t))
else:
    st.warning(t["weather_error"])

st.divider()

# Image Upload & Diagnosis Section
col_upload, col_result = st.columns([1, 1.2], gap="large")

with col_upload:
    st.subheader(t["upload_header"])
    uploaded_file = st.file_uploader(
        t["uploader_label"],
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
        st.write(t["no_image"])

with col_result:
    st.subheader(t["result_header"])
    analyze_clicked = st.button(
        t["analyze_btn"],
        type="primary",
        disabled=(pil_image is None),
        use_container_width=True,
    )

    if analyze_clicked and pil_image is not None:
        with st.spinner(t["spinner"]):
            condition, confidence, details = run_diagnosis(pil_image, crop_key, lang)

        st.success(f"**{t['detected']}:** {condition}")
        m1, m2 = st.columns(2)
        m1.metric(t["confidence"], f"{confidence * 100:.1f}%")
        m2.metric(t["severity"], details["severity"])

        if field_note.strip():
            st.caption(f"{t['field_note_prefix']}: {field_note.strip()}")

        st.markdown(f"**{t['symptoms_header']}**")
        st.write(details["symptoms"])

        st.markdown(f"**{t['action_header']}**")
        st.write(details["action"])
