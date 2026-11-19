import io
import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="AgriShield — Crop Disease Diagnosis",
    page_icon="🌿",
    layout="wide",
)

# Sample knowledge base for quick UI testing; replace with your real model or API call
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
    },
    "Potato": {
        "Early Blight": {
            "severity": "Moderate",
            "symptoms": "Dark brown angular/concentric spots on foliage, premature leaf drop.",
            "action": "Maintain balanced soil nutrition, rotate crops, and use labeled protectant fungicides if needed.",
        },
        "Healthy Leaf": {
            "severity": "None",
            "symptoms": "Uniform green foliage without lesions, curling, or discoloration.",
            "action": "Continue regular monitoring, drip/base irrigation, and field scouting.",
        },
    },
    "Rice": {
        "Leaf Blast": {
            "severity": "High",
            "symptoms": "Diamond- or spindle-shaped lesions with gray centers and dark brown borders.",
            "action": "Avoid excessive nitrogen fertilizer and follow regional agricultural recommendations for blast control.",
        },
        "Healthy Leaf": {
            "severity": "None",
            "symptoms": "Clean green blades free of spots or streaking.",
            "action": "Maintain standard water management and periodic scouting.",
        },
    },
}


def run_diagnosis(image: Image.Image, crop: str) -> tuple[str, float, dict]:
    """Placeholder inference function using image dimensions as a deterministic demo hook."""
    candidates = list(DISEASE_GUIDES.get(crop, {}).items())
    if not candidates:
        return (
            "Healthy Leaf",
            0.85,
            {
                "severity": "None",
                "symptoms": "No specific disease pattern configured yet for this crop.",
                "action": "Inspect leaves closely and connect a trained model in `run_diagnosis()`.",
            },
        )

    width, height = image.size
    idx = (width + height) % len(candidates)
    condition, details = candidates[idx]
    confidence = 0.78 + ((width * height) % 18) / 100.0
    return condition, min(confidence, 0.96), details


st.title("🌿 AgriShield")
st.caption("Upload a crop leaf image to preview a diagnosis workflow and recommended next steps.")

with st.sidebar:
    st.header("Scan Settings")
    crop = st.selectbox("Crop Type", ["Tomato", "Potato", "Rice"])
    field_note = st.text_input("Plot / Field Note (optional)", placeholder="e.g., North plot, Row 4")
    st.divider()
    st.info(
        "This starter uses placeholder logic in `run_diagnosis()`. "
        "Swap in your PyTorch/TensorFlow/ONNX model or API endpoint when ready."
    )

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
        st.image(pil_image, caption=f"{uploaded_file.name} ({pil_image.size[0]}×{pil_image.size[1]}px)", use_container_width=True)
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
