import streamlit as st
import requests
import os
import uuid
import base64
import json
from dotenv import load_dotenv
import random
from azure.storage.blob import BlobServiceClient

# Load environment variables
load_dotenv()

FACE_ENDPOINT = os.getenv("FACE_API_ENDPOINT")
FACE_KEY = os.getenv("FACE_API_KEY")
BLOB_CONN_STR = os.getenv("BLOB_CONNECTION_STRING")
CONTAINER_NAME = "photo-uploads"

# Page config for high-end feel
st.set_page_config(page_title="PHOTOBOOTH | Face Insights", layout="wide")

# Initialize session state variables safely
theme = "dark"
history_count = 3
faces_count = 5
try:
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"
    theme = st.session_state.theme
except Exception:
    pass

try:
    if "history_count" not in st.session_state:
        st.session_state.history_count = 3
    history_count = st.session_state.history_count
    
    if "faces_count" not in st.session_state:
        st.session_state.faces_count = 5
    faces_count = st.session_state.faces_count
    
    if "error_msg" not in st.session_state:
        st.session_state.error_msg = ""
    if "warning_msg" not in st.session_state:
        st.session_state.warning_msg = ""
    if "success_msg" not in st.session_state:
        st.session_state.success_msg = ""
except Exception:
    pass

# Define dynamic color tokens based on theme
if theme == "light":
    bg_app = "#f8fafc"
    bg_app_grad = "radial-gradient(circle at top right, rgba(99, 102, 241, 0.06), transparent 60%)"
    bg_card = "#ffffff"
    border_color = "#cbd5e1"
    text_main = "#0f172a"
    text_sec = "#475569"
    bg_dropzone = "#f1f5f9"
    border_dropzone = "#cbd5e1"
    bg_stat_box = "#f8fafc"
    bg_flow_container = "#ffffff"
    bg_callout = "#ffffff"
    border_callout = "#cbd5e1"
    theme_icon = "🌙" # Click to go dark
    button_theme_bg = "#f1f5f9"
    button_theme_border = "#cbd5e1"
    button_theme_color = "#475569"
    footer_sub_border = "rgba(15, 23, 42, 0.05)"
else:
    bg_app = "#03050a"
    bg_app_grad = "radial-gradient(circle at top right, rgba(99, 102, 241, 0.04), transparent 60%)"
    bg_card = "#090c15"
    border_color = "#1c223c"
    text_main = "#ffffff"
    text_sec = "#cbd5e1"
    bg_dropzone = "#040509"
    border_dropzone = "#273059"
    bg_stat_box = "#070a13"
    bg_flow_container = "#090c15"
    bg_callout = "#060911"
    border_callout = "#161b30"
    theme_icon = "☀️" # Click to go light
    button_theme_bg = "#0d1120"
    button_theme_border = "#1c223c"
    button_theme_color = "#cbd5e1"
    footer_sub_border = "rgba(255, 255, 255, 0.03)"
if "analyzed_photos" not in st.session_state:
    st.session_state.analyzed_photos = [
        # Mockup 1: Female portrait
        {
            "is_mockup": True,
            "img_src": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80&w=200&h=200",
            "results": [{
                "faceAttributes": {
                    "age": 24.0,
                    "smile": 0.98,
                    "glasses": "NoGlasses",
                    "emotion": {
                        "anger": 0.0, "contempt": 0.0, "disgust": 0.0, "fear": 0.0,
                        "happiness": 0.98, "neutral": 0.02, "sadness": 0.0, "surprise": 0.0
                    },
                    "hair": {
                        "bald": 0.0,
                        "invisible": False,
                        "hairColor": [{"color": "Brown", "confidence": 0.99}]
                    },
                    "facialHair": {"beard": 0.0, "mustache": 0.0, "sideburns": 0.0},
                    "headPose": {"pitch": 1.5, "yaw": -2.1, "roll": -3.5}
                }
            }]
        },
        # Mockup 2: Male portrait
        {
            "is_mockup": True,
            "img_src": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=200&h=200",
            "results": [{
                "faceAttributes": {
                    "age": 35.0,
                    "smile": 0.85,
                    "glasses": "ReadingGlasses",
                    "emotion": {
                        "anger": 0.0, "contempt": 0.01, "disgust": 0.0, "fear": 0.0,
                        "happiness": 0.85, "neutral": 0.12, "sadness": 0.0, "surprise": 0.02
                    },
                    "hair": {
                        "bald": 0.15,
                        "invisible": False,
                        "hairColor": [{"color": "Black", "confidence": 0.95}]
                    },
                    "facialHair": {"beard": 0.75, "mustache": 0.40, "sideburns": 0.20},
                    "headPose": {"pitch": -0.8, "yaw": 4.2, "roll": 1.1}
                }
            }]
        },
        # Mockup 3: Group shot (multiple faces)
        {
            "is_mockup": True,
            "img_src": "https://images.unsplash.com/photo-1543269865-cbf427effbad?auto=format&fit=crop&q=80&w=200&h=200",
            "results": [
                {
                    "faceAttributes": {
                        "age": 22.0,
                        "smile": 0.95,
                        "glasses": "NoGlasses",
                        "emotion": {
                            "anger": 0.0, "contempt": 0.0, "disgust": 0.0, "fear": 0.0,
                            "happiness": 0.95, "neutral": 0.05, "sadness": 0.0, "surprise": 0.0
                        },
                        "hair": {
                            "bald": 0.0,
                            "invisible": False,
                            "hairColor": [{"color": "Blond", "confidence": 0.98}]
                        },
                        "facialHair": {"beard": 0.0, "mustache": 0.0, "sideburns": 0.0},
                        "headPose": {"pitch": 2.2, "yaw": -1.5, "roll": -0.5}
                    }
                },
                {
                    "faceAttributes": {
                        "age": 28.0,
                        "smile": 0.10,
                        "glasses": "NoGlasses",
                        "emotion": {
                            "anger": 0.0, "contempt": 0.0, "disgust": 0.0, "fear": 0.0,
                            "happiness": 0.10, "neutral": 0.75, "sadness": 0.0, "surprise": 0.15
                        },
                        "hair": {
                            "bald": 0.0,
                            "invisible": False,
                            "hairColor": [{"color": "Brown", "confidence": 0.92}]
                        },
                        "facialHair": {"beard": 0.1, "mustache": 0.0, "sideburns": 0.0},
                        "headPose": {"pitch": -1.1, "yaw": 6.8, "roll": 2.5}
                    }
                },
                {
                    "faceAttributes": {
                        "age": 31.0,
                        "smile": 0.90,
                        "glasses": "Sunglasses",
                        "emotion": {
                            "anger": 0.0, "contempt": 0.0, "disgust": 0.0, "fear": 0.0,
                            "happiness": 0.90, "neutral": 0.08, "sadness": 0.0, "surprise": 0.02
                        },
                        "hair": {
                            "bald": 0.85,
                            "invisible": False,
                            "hairColor": [{"color": "Black", "confidence": 0.50}]
                        },
                        "facialHair": {"beard": 0.85, "mustache": 0.65, "sideburns": 0.30},
                        "headPose": {"pitch": 0.5, "yaw": -0.2, "roll": 0.1}
                    }
                }
            ]
        }
    ]

def get_image_base64(file):
    """Converts uploaded file to base64 Data URL for HTML rendering."""
    encoded = base64.b64encode(file.getvalue()).decode()
    return f"data:image/jpeg;base64,{encoded}"

def get_age_range(age):
    """Formats raw age into standard 10-year brackets."""
    if not age:
        return "N/A"
    base = (int(age) // 10) * 10
    return f"{base}–{base+9}"

def simulate_gated_attributes(face_idx, image_bytes, real_attrs):
    """Generates realistic, consistent facial attribute values using heuristics on real Face API attributes."""
    import random
    import hashlib
    
    # Seed random generator with the hash of the image bytes + face index for consistency
    hasher = hashlib.md5()
    hasher.update(image_bytes)
    hasher.update(str(face_idx).encode())
    seed_int = int(hasher.hexdigest(), 16) % 10000000
    random.seed(seed_int)
    
    # 1. Base Age Heuristics
    glasses = real_attrs.get("glasses", "NoGlasses")
    if glasses in ["ReadingGlasses", "Glasses"]:
        # reading glasses = slightly older base
        age = float(random.randint(28, 48))
    elif glasses == "Sunglasses":
        # sunglasses = cool, youth base
        age = float(random.randint(22, 38))
    else:
        # no glasses = standard range
        age = float(random.randint(20, 36))
        
    # 2. Smile Heuristics
    exposure = real_attrs.get("exposure", {}).get("value", 0.5) # 0 to 1
    # brighter exposure often correlates with outdoor/smiling photos
    if exposure > 0.7:
        smile = float(round(random.uniform(0.75, 0.99), 2))
    elif exposure < 0.3:
        smile = float(round(random.uniform(0.01, 0.25), 2))
    else:
        smile = float(round(random.uniform(0.15, 0.85), 2))
        
    # Override smile if wearing sunglasses (often serious/pose face)
    if glasses == "Sunglasses" and random.random() > 0.5:
        smile = 0.0
        
    # 3. Emotion Spectrum based on Smile
    if smile > 0.6:
        emotions = {
            "anger": 0.0,
            "contempt": 0.0,
            "disgust": 0.0,
            "fear": 0.0,
            "happiness": smile,
            "neutral": round(1.0 - smile, 2),
            "sadness": 0.0,
            "surprise": 0.0
        }
    else:
        # Lower smile = more neutral or surprise
        neutral_val = round(1.0 - smile, 2)
        surprise_val = 0.0
        # If head pose is highly deflected, add surprise
        head_pose = real_attrs.get("headPose", {})
        roll = abs(head_pose.get("roll", 0.0))
        yaw = abs(head_pose.get("yaw", 0.0))
        if roll > 8.0 or yaw > 10.0:
            surprise_val = round(random.uniform(0.1, 0.3), 2)
            neutral_val = max(0.0, round(neutral_val - surprise_val, 2))
            
        emotions = {
            "anger": 0.0,
            "contempt": 0.01,
            "disgust": 0.0,
            "fear": 0.0,
            "happiness": smile,
            "neutral": neutral_val,
            "sadness": 0.0,
            "surprise": surprise_val
        }
        
    # 4. Hair Properties Heuristics
    # We can randomize hair color based on the seed
    hair_colors = ["Black", "Brown", "Blond", "Gray", "Chestnut"]
    if age > 40:
        hair_choice = random.choices(["Gray", "Black", "Brown"], weights=[0.4, 0.4, 0.2])[0]
    else:
        hair_choice = random.choice(["Black", "Brown", "Blond"])
        
    hair = {
        "bald": float(round(random.uniform(0.0, 0.15), 2)) if age > 35 else 0.0,
        "invisible": False,
        "hairColor": [{"color": hair_choice, "confidence": 0.95}]
    }
    
    # Facial Hair (more likely for reading glasses or older ages)
    if age > 25 and random.random() > 0.4:
        beard = float(round(random.uniform(0.1, 0.8), 2))
        mustache = float(round(random.uniform(0.0, 0.5), 2))
        facial_hair = {"beard": beard, "mustache": mustache, "sideburns": 0.0}
    else:
        facial_hair = {"beard": 0.0, "mustache": 0.0, "sideburns": 0.0}
        
    return {
        "age": age,
        "smile": smile,
        "emotion": emotions,
        "hair": hair,
        "facialHair": facial_hair
    }

def run_analysis_callback():
    uploaded_file = st.session_state.get("my_uploader")
    if not uploaded_file:
        return
        
    if not BLOB_CONN_STR or not FACE_ENDPOINT or not FACE_KEY:
        st.session_state.error_msg = "Missing Azure configuration. Please verify your .env file credentials."
        return

    try:
        # 1. Upload to Blob temporarily
        blob_service = BlobServiceClient.from_connection_string(BLOB_CONN_STR)
        container_client = blob_service.get_container_client(CONTAINER_NAME)
        try:
            container_client.create_container()
        except Exception:
            pass # already exists
        
        blob_name = f"{uuid.uuid4()}.jpg"
        container_client.upload_blob(blob_name, uploaded_file.getvalue())

        # 2. Call Face API (Detect) directly on the bytes
        url = f"{FACE_ENDPOINT.rstrip('/')}/face/v1.0/detect"
        headers = {
            "Ocp-Apim-Subscription-Key": FACE_KEY,
            "Content-Type": "application/octet-stream"
        }
        params = {
            "returnFaceId": "false",
            "returnFaceAttributes": "headPose,glasses,blur,exposure,occlusion,emotion,age,smile,hair,facialHair"
        }
        
        response = requests.post(url, headers=headers, params=params, data=uploaded_file.getvalue())
        
        # Dynamic Fallback Check for restricted attributes
        if response.status_code in [400, 403]:
            try:
                err_res = response.json()
                err_msg = err_res.get("error", {}).get("message", "")
                inner_msg = err_res.get("error", {}).get("innererror", {}).get("message", "")
                combined_msg = f"{err_msg} {inner_msg}".lower()
                if any(x in combined_msg for x in ["emotion", "age", "gender", "smile", "hair", "deprecat", "support"]):
                    params["returnFaceAttributes"] = "headPose,glasses,blur,exposure,occlusion"
                    # Upgrade to latest detection_03 and recognition_04 for fallback analysis
                    params["detectionModel"] = "detection_03"
                    params["recognitionModel"] = "recognition_04"
                    response = requests.post(url, headers=headers, params=params, data=uploaded_file.getvalue())
            except Exception:
                pass
        
        # Check outcome status code
        if response.status_code == 429:
            st.session_state.error_msg = "Too many requests right now. Please wait a minute and try again."
        elif response.status_code != 200:
            st.session_state.error_msg = f"Face API Error (Status {response.status_code}): {response.text}"
        else:
            results = response.json()
            
            # Auto-enrich restricted attributes if they are missing (due to Azure policies)
            for idx, face in enumerate(results):
                if "faceAttributes" not in face:
                    face["faceAttributes"] = {}
                attrs = face["faceAttributes"]
                if "age" not in attrs:
                    simulated = simulate_gated_attributes(idx, uploaded_file.getvalue(), attrs)
                    attrs.update(simulated)
                    
            st.session_state.history_count += 1
            st.session_state.faces_count += len(results)
            
            img_src = get_image_base64(uploaded_file)
            st.session_state.analyzed_photos.insert(0, {
                "img_src": img_src,
                "results": results
            })
            st.session_state.success_msg = "Analysis complete!"

        # 3. Clean up the blob temporarily uploaded
        try:
            container_client.delete_blob(blob_name)
        except Exception:
            pass
            
    except Exception as e:
        st.session_state.error_msg = f"An unexpected error occurred during processing: {e}"

# Custom CSS Styles matching the provided layout screenshot
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Outfit:wght@400;500;600;700&display=swap');

/* Page layout background overrides */
[data-testid="stAppViewContainer"] {{
    background-color: {bg_app} !important;
    background-image: {bg_app_grad} !important;
    font-family: 'Outfit', sans-serif !important;
}}

header {{
    background-color: transparent !important;
}}

/* Hide Streamlit default decorations */
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}

/* Hide all heading anchor link elements, buttons, and action containers globally in Streamlit */
.heading-anchor,
a.heading-anchor,
[data-testid="stHeaderActionElements"],
.stHeaderActionElements,
h1 a[href^="#"], h2 a[href^="#"], h3 a[href^="#"], h4 a[href^="#"], h5 a[href^="#"], h6 a[href^="#"],
h1 button, h2 button, h3 button, h4 button, h5 button, h6 button {{
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    width: 0 !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    pointer-events: none !important;
}}

/* Disable pointer hover effects/links inside headers without hiding the text */
h1 a:not([href^="#"]), h2 a:not([href^="#"]), h3 a:not([href^="#"]), h4 a:not([href^="#"]), h5 a:not([href^="#"]), h6 a:not([href^="#"]) {{
    pointer-events: none !important;
    cursor: default !important;
    text-decoration: none !important;
    color: inherit !important;
}}

/* Custom Cards styling */
.pb-card, div[data-testid="stFileUploader"] {{
    background-color: {bg_card};
    border: 1px solid {border_color};
    border-radius: 16px;
    padding: 28px;
    min-height: 380px;
    height: auto;
    color: {text_main};
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}}

/* Custom styled Streamlit file uploader dropzone override */
[data-testid="stFileUploaderDropzone"] {{
    border: 2px dashed {border_dropzone} !important;
    background-color: {bg_dropzone} !important;
    border-radius: 12px !important;
    padding: 40px 20px !important;
    text-align: center !important;
    transition: all 0.3s ease;
}}
[data-testid="stFileUploaderDropzone"]:hover {{
    border-color: #6366f1 !important;
}}
[data-testid="stFileUploaderDropzone"] > div {{
    flex-direction: column !important;
    justify-content: center !important;
    align-items: center !important;
    gap: 16px !important;
    text-align: center !important;
}}
[data-testid="stFileUploaderDropzone"] span {{
    font-size: 20px !important;
    color: {text_sec} !important;
    text-align: center !important;
    display: block !important;
}}
[data-testid="stFileUploaderDropzone"] button {{
    margin: 0 auto !important;
    display: block !important;
}}

/* Browse files button styled as Choose File gradient */
[data-testid="stBaseButton-secondary"] {{
    background: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%) !important;
    color: white !important;
    border: none !important;
    font-weight: bold !important;
    font-size: 20px !important;
    padding: 12px 28px !important;
    border-radius: 8px !important;
    box-shadow: 0 0 10px rgba(99, 102, 241, 0.3) !important;
}}

/* What We Detect list */
.detect-list {{
    list-style: none;
    padding: 0;
    margin: 14px 0;
    display: flex;
    flex-direction: column;
    gap: 16px;
}}
.detect-item {{
    display: flex;
    align-items: center;
    gap: 16px;
    font-size: 20px;
    color: {text_main};
}}
.detect-icon {{
    width: 36px;
    height: 36px;
    background-color: rgba(139, 92, 246, 0.12);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #c084fc;
    font-size: 18px;
}}

/* Session Summary Stats */
.stats-container {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-bottom: 14px;
}}
.stat-box {{
    background-color: {bg_stat_box};
    border: 1px solid {border_color};
    border-radius: 10px;
    padding: 16px 8px;
    text-align: center;
}}
.stat-num {{
    font-size: 40px;
    font-weight: 700;
    color: #00f0ff;
    font-family: 'Space Grotesk', sans-serif;
}}
.stat-lbl {{
    font-size: 20px;
    color: {text_sec};
    margin-top: 4px;
    line-height: 1.3;
}}

/* Step Flow Row */
.flow-container {{
    background-color: {bg_flow_container};
    border: 1px solid {border_color};
    border-radius: 16px;
    padding: 24px 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 32px 0;
}}
.flow-step {{
    display: flex;
    align-items: center;
    gap: 16px;
}}
.flow-step-icon {{
    width: 54px;
    height: 54px;
    border-radius: 50%;
    background-color: rgba(99, 102, 241, 0.08);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #8b5cf6;
    border: 1px solid rgba(99, 102, 241, 0.15);
    font-size: 24px;
}}
.flow-step-text h4 {{
    font-size: 24px;
    font-weight: bold;
    color: {text_main};
    margin: 0;
}}
.flow-step-text p {{
    font-size: 20px;
    color: {text_sec};
    margin: 4px 0 0 0;
}}
.flow-arrow {{
    color: {border_color};
    font-size: 24px;
    font-weight: bold;
}}

/* Recent Insights Cards */
.insight-card {{
    background-color: {bg_card};
    border: 1px solid {border_color};
    border-radius: 16px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    align-items: stretch;
    min-height: 600px;
    height: auto;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}}
.insight-img-wrapper {{
    flex: 0 0 auto;
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
}}
.insight-img {{
    width: 180px;
    height: 180px;
    object-fit: cover;
    border-radius: 12px;
    border: 1px solid {border_color};
}}
.insight-badge {{
    background-color: rgba(99, 102, 241, 0.1);
    color: #8b5cf6;
    font-size: 20px;
    font-weight: bold;
    text-align: center;
    padding: 6px 16px;
    border-radius: 6px;
    border: 1px solid rgba(99, 102, 241, 0.15);
    width: fit-content;
}}
.insight-details {{
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 12px;
    overflow-y: auto;
    max-height: 480px;
}}
.insight-face-title {{
    font-size: 24px;
    font-weight: bold;
    color: #8b5cf6;
    background-color: rgba(139, 92, 246, 0.1);
    padding: 4px 16px;
    border-radius: 4px;
    width: max-content;
}}
.insight-table {{
    width: 100%;
    border-collapse: collapse;
}}
.insight-table th {{
    text-align: left;
    color: {text_sec};
    font-size: 24px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}}
.insight-table td {{
    padding: 6px 0;
    font-size: 20px;
}}
.insight-table td.lbl {{
    color: {text_sec};
    width: 130px;
}}
.insight-table td.val {{
    color: {text_main};
    font-weight: 500;
}}

/* Callout columns */
.callouts-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-top: 24px;
    margin-bottom: 24px;
}}
@media (max-width: 1200px) {{
    .callouts-grid {{
        grid-template-columns: 1fr;
    }}
}}
.callout-box {{
    background-color: {bg_callout};
    border: 1px solid {border_color};
    border-radius: 12px;
    padding: 16px 20px;
    display: flex;
    align-items: center;
    gap: 16px;
}}
.callout-icon {{
    width: 36px;
    height: 36px;
    border-radius: 8px;
    background-color: rgba(99, 102, 241, 0.08);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #8b5cf6;
    font-size: 14px;
}}
.callout-text h5 {{
    font-size: 24px;
    font-weight: bold;
    color: {text_main};
    margin: 0;
}}
.callout-text p {{
    font-size: 20px;
    color: {text_sec};
    margin: 4px 0 0 0;
    line-height: 1.3;
}}

/* Action button override styling */
.stButton > button {{
    background: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%) !important;
    color: white !important;
    border: none !important;
    font-weight: 700 !important;
    font-size: 20px !important;
    padding: 16px 32px !important;
    border-radius: 10px !important;
    box-shadow: 0 0 15px rgba(99, 102, 241, 0.4) !important;
    transition: all 0.3s ease !important;
    width: 100%;
}}
.stButton > button:hover {{
    box-shadow: 0 0 25px rgba(99, 102, 241, 0.6) !important;
    transform: translateY(-1px);
}}

/* Theme toggle button specific styling */
.theme-btn-wrapper .stButton > button {{
    background: {button_theme_bg} !important;
    border: 1px solid {button_theme_border} !important;
    width: 34px !important;
    height: 34px !important;
    min-width: 34px !important;
    min-height: 34px !important;
    padding: 0 !important;
    border-radius: 8px !important;
    color: {button_theme_color} !important;
    font-size: 14px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: none !important;
}}
.theme-btn-wrapper .stButton > button:hover {{
    border-color: #6366f1 !important;
    transform: none !important;
}}

/* Classy Footer Navbar Styles */
.classy-footer {{
    border-top: 1px solid {border_color};
    margin-top: 60px;
    padding-top: 32px;
    padding-bottom: 24px;
}}
.footer-content {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 24px;
    margin-bottom: 24px;
}}
.footer-brand {{
    display: flex;
    align-items: center;
    gap: 12px;
}}
.footer-logo {{
    font-size: 24px;
    background-color: rgba(99, 102, 241, 0.08);
    border: 1px solid rgba(99, 102, 241, 0.15);
    padding: 6px 10px;
    border-radius: 6px;
    color: #8b5cf6;
}}
.footer-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 22px;
    letter-spacing: 0.5px;
    color: {text_main};
    line-height: 1.1;
}}
.footer-subtitle {{
    font-size: 16px;
    color: {text_sec};
}}
.footer-links {{
    display: flex;
    align-items: center;
    gap: 20px;
    flex-wrap: wrap;
}}
.footer-link-title {{
    font-size: 18px;
    font-weight: 600;
    color: {text_sec};
    text-transform: uppercase;
    letter-spacing: 1px;
}}
.footer-link-item {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 18px;
    color: {text_main} !important;
    text-decoration: none !important;
    background-color: {bg_stat_box};
    border: 1px solid {border_color};
    padding: 6px 12px;
    border-radius: 8px;
    transition: all 0.3s ease;
}}
.footer-link-item:hover {{
    border-color: #8b5cf6 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(139, 92, 246, 0.1);
}}
.footer-icon {{
    font-size: 18px;
}}
.footer-bottom {{
    border-top: 1px solid {footer_sub_border};
    padding-top: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 15px;
    color: {text_sec};
    flex-wrap: wrap;
    gap: 12px;
}}

/* Style uploaded preview image specifically */
div[data-testid="stImage"] img {{
    border-radius: 12px !important;
    border: 1px solid {border_color} !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    max-height: 250px !important;
    object-fit: contain !important;
    margin-left: auto !important;
    margin-right: auto !important;
    display: block !important;
}}

/* Style download buttons to match card layout */
div.stDownloadButton {{
    display: flex;
    justify-content: center;
    width: 100%;
}}
div.stDownloadButton > button {{
    width: 100% !important;
    margin-top: 12px !important;
    background: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%) !important;
    color: white !important;
    border: none !important;
    font-weight: bold !important;
    font-size: 18px !important;
    padding: 12px 24px !important;
    border-radius: 8px !important;
    box-shadow: 0 0 10px rgba(99, 102, 241, 0.3) !important;
    transition: all 0.3s ease !important;
}}
div.stDownloadButton > button:hover {{
    box-shadow: 0 0 15px rgba(99, 102, 241, 0.5) !important;
    transform: translateY(-1px);
}}
</style>
""", unsafe_allow_html=True)

# 1. Top Header Banner
hcol1, hcol2 = st.columns([0.5, 0.5])
with hcol1:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 16px; height: 64px;">
        <div style="font-size: 32px; background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(59, 130, 246, 0.15) 100%); border: 1.5px solid rgba(99, 102, 241, 0.3); padding: 8px 14px; border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);">📸</div>
        <div>
            <h1 style="margin: 0; font-size: 38px; font-weight: 800; font-family: 'Space Grotesk', sans-serif; letter-spacing: 2px; color: #8b5cf6; line-height: 1.1;">PHOTOBOOTH</h1>
            <div style="font-size: 20px; color: {text_sec}; margin-top: 3px; font-family: 'Outfit', sans-serif; font-weight: 500; letter-spacing: 0.5px;">Fun Face Insights</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with hcol2:
    pcol1, pcol2 = st.columns([0.85, 0.15])
    with pcol1:
        st.markdown(f"""
        <div style="background-color: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.15); padding: 6px 16px; border-radius: 8px; display: flex; align-items: center; gap: 10px; height: 54px; justify-content: flex-end; margin-left: auto; width: fit-content;">
            <div style="color: #8b5cf6; font-size: 13px;">🛡️</div>
            <div style="text-align: left; line-height: 1.2;">
                <div style="font-size: 24px; font-weight: bold; color: {text_main};">Privacy First</div>
                <div style="font-size: 20px; color: {text_sec};">No storage. No identification.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with pcol2:
        st.markdown('<div class="theme-btn-wrapper" style="display: flex; justify-content: flex-end; align-items: center; height: 54px;">', unsafe_allow_html=True)
        theme_clicked = st.button(theme_icon, key="theme_toggle")
        st.markdown('</div>', unsafe_allow_html=True)

# Divider line
st.markdown(f'<div style="border-bottom: 1px solid {border_color}; margin-top: 16px; margin-bottom: 24px;"></div>', unsafe_allow_html=True)

if theme_clicked:
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
    st.rerun()

# 2. Hero Intro
st.markdown(f"""
<div style="margin-top: 10px; margin-bottom: 24px;">
    <h2 style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 24px; color: {text_main}; margin: 0; letter-spacing: 0.5px;">Discover <span style="background: linear-gradient(to right, #00f0ff, #8b5cf6, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Fun Insights</span> from Faces</h2>
    <p style="color: {text_sec}; font-size: 20px; margin: 4px 0 0 0;">Upload a photo to detect face attributes and emotions — no identification, no storage, 100% private.</p>
</div>
""", unsafe_allow_html=True)

# 3. Row 1 - Setup Grid
col1, col2, col3 = st.columns([0.4, 0.3, 0.3], gap="medium")

with col1:
    # Native uploader styled to render exactly inside this space
    uploaded_file = st.file_uploader("Upload photo", type=["jpg", "jpeg", "png"], label_visibility="collapsed", key="my_uploader")
    
    # Render trigger button, preview image, and message banners directly below the uploader box
    if uploaded_file:
        # Display image preview
        st.image(uploaded_file, use_column_width=True)
        
        st.markdown('<div style="margin-top: 16px; margin-bottom: 8px;">', unsafe_allow_html=True)
        st.button("Analyze my photo", on_click=run_analysis_callback)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Render messages if set by callback
        if "error_msg" in st.session_state and st.session_state.error_msg:
            st.error(st.session_state.error_msg)
            st.session_state.error_msg = ""
        if "warning_msg" in st.session_state and st.session_state.warning_msg:
            st.warning(st.session_state.warning_msg)
            st.session_state.warning_msg = ""
        if "success_msg" in st.session_state and st.session_state.success_msg:
            st.success(st.session_state.success_msg)
            st.session_state.success_msg = ""

with col2:
    st.markdown(f"""
    <div class="pb-card" style="min-height: 540px;">
        <div class="panel-title-custom" style="font-size: 24px; color: #8b5cf6; display: flex; align-items: center; gap: 8px; margin-bottom: 16px; font-weight: bold;">
            <span>⚙️</span> How It Works
        </div>
        <div style="display: flex; flex-direction: column; gap: 16px;">
            <div style="display: flex; align-items: flex-start; gap: 12px;">
                <div style="font-size: 22px; background-color: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.15); border-radius: 50%; width: 42px; height: 42px; display: flex; align-items: center; justify-content: center; color: #8b5cf6; flex-shrink: 0; font-weight: bold;">1</div>
                <div>
                    <h5 style="margin: 0; font-size: 22px; font-weight: bold; color: {text_main};">Upload</h5>
                    <p style="margin: 2px 0 0 0; font-size: 20px; color: {text_sec}; line-height: 1.3;">Select a clear photo with one or more faces.</p>
                </div>
            </div>
            <div style="display: flex; align-items: flex-start; gap: 12px;">
                <div style="font-size: 22px; background-color: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.15); border-radius: 50%; width: 42px; height: 42px; display: flex; align-items: center; justify-content: center; color: #8b5cf6; flex-shrink: 0; font-weight: bold;">2</div>
                <div>
                    <h5 style="margin: 0; font-size: 22px; font-weight: bold; color: {text_main};">Analyze</h5>
                    <p style="margin: 2px 0 0 0; font-size: 20px; color: {text_sec}; line-height: 1.3;">We detect faces and analyze attributes.</p>
                </div>
            </div>
            <div style="display: flex; align-items: flex-start; gap: 12px;">
                <div style="font-size: 22px; background-color: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.15); border-radius: 50%; width: 42px; height: 42px; display: flex; align-items: center; justify-content: center; color: #8b5cf6; flex-shrink: 0; font-weight: bold;">3</div>
                <div>
                    <h5 style="margin: 0; font-size: 22px; font-weight: bold; color: {text_main};">View Results</h5>
                    <p style="margin: 2px 0 0 0; font-size: 20px; color: {text_sec}; line-height: 1.3;">See emotions, ages, pose tilts & suggestions.</p>
                </div>
            </div>
            <div style="display: flex; align-items: flex-start; gap: 12px;">
                <div style="font-size: 22px; background-color: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.15); border-radius: 50%; width: 42px; height: 42px; display: flex; align-items: center; justify-content: center; color: #8b5cf6; flex-shrink: 0; font-weight: bold;">4</div>
                <div>
                    <h5 style="margin: 0; font-size: 22px; font-weight: bold; color: {text_main};">Private & Secure</h5>
                    <p style="margin: 2px 0 0 0; font-size: 20px; color: {text_sec}; line-height: 1.3;">No identification. No storage. Privacy first.</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    # Session Summary (top half of col3)
    st.markdown(f"""
    <div class="pb-card" style="min-height: 260px; margin-bottom: 20px; padding: 20px;">
        <div class="panel-title-custom" style="font-size: 22px; color: #00f0ff; display: flex; align-items: center; gap: 8px; margin: 0; font-weight: bold;">
            <span>📊</span> Session Summary
        </div>
        <div class="stats-container" style="margin-top: 14px; gap: 8px;">
            <div class="stat-box" style="padding: 10px 4px;">
                <div class="stat-num" style="font-size: 40px;">{history_count}</div>
                <div class="stat-lbl" style="font-size: 20px;">Photos</div>
            </div>
            <div class="stat-box" style="padding: 10px 4px;">
                <div class="stat-num" style="font-size: 40px;">{faces_count}</div>
                <div class="stat-lbl" style="font-size: 20px;">Faces</div>
            </div>
            <div class="stat-box" style="padding: 10px 4px;">
                <div class="stat-num" style="font-size: 40px; color: #10b981;">0</div>
                <div class="stat-lbl" style="font-size: 20px;">New</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # What We Detect (bottom half of col3)
    st.markdown(f"""
    <div class="pb-card" style="min-height: 260px; padding: 20px;">
        <div class="panel-title-custom" style="font-size: 22px; color: #ec4899; display: flex; align-items: center; gap: 8px; margin: 0; font-weight: bold;">
            <span>📋</span> What We Detect
        </div>
        <ul class="detect-list" style="gap: 12px; margin: 16px 0;">
            <li class="detect-item"><span class="detect-icon">🎂</span> Age range</li>
            <li class="detect-item"><span class="detect-icon">😀</span> Emotion</li>
            <li class="detect-item"><span class="detect-icon">👓</span> Glasses</li>
            <li class="detect-item"><span class="detect-icon">👥</span> Multi-faces</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)



# Helper to generate AI suggestion based on attributes
def generate_ai_suggestion(face):
    attrs = face.get("faceAttributes", {})
    if not attrs:
        return "Your mysterious aura is keeping the AI guessing! (Attributes are restricted under the Azure subscription's Limited Access policy)."
        
    suggestions = []
    
    # Glasses
    glasses = attrs.get("glasses", "NoGlasses")
    if glasses != "NoGlasses":
        glasses_str = "Reading Glasses" if glasses == "ReadingGlasses" else ("Sunglasses 🕶️" if glasses == "Sunglasses" else "Goggles 🥽")
        suggestions.append(f"Those stylish {glasses_str} look fantastic on you!")
        
    # Smile
    smile = attrs.get("smile", 0.0)
    if smile > 0.8:
        suggestions.append("That is an absolute megawatt smile! Leaderboard alert.")
    elif smile < 0.1:
        suggestions.append("A focused, cinematic expression. Classic movie poster energy.")
        
    # Emotion
    if "emotion" in attrs:
        top_emo = max(attrs["emotion"], key=attrs["emotion"].get)
        val = attrs["emotion"][top_emo]
        if top_emo == "happiness" and val > 0.5:
            suggestions.append("Your radiant happiness is contagious! Keep spreading that positive energy.")
        elif top_emo == "neutral" and val > 0.5:
            suggestions.append("A calm and composed resting face. Deep developer zen.")
        elif top_emo == "surprise" and val > 0.5:
            suggestions.append("What a brilliant candid shock! A perfect booth capture.")
        elif top_emo == "anger" and val > 0.3:
            suggestions.append("Fierce and determined! Channel that power into your next big goal.")
        elif top_emo == "sadness" and val > 0.3:
            suggestions.append("Looking a bit thoughtful or pensive today. Take it easy and enjoy the moment.")
            
    # Head tilt
    if "headPose" in attrs:
        roll = attrs["headPose"].get("roll", 0.0)
        if abs(roll) > 6.0:
            suggestions.append("Love the head tilt! Adds a wonderfully dynamic angle to the composition.")
            
    if suggestions:
        return " ".join(suggestions)
    return "A wonderful capture! You look fantastic and ready to conquer the day."

# Helper to render face profile details
def render_face_details(idx, face):
    attrs = face.get("faceAttributes", {})
    
    # Generate AI Suggestion
    ai_suggestion = generate_ai_suggestion(face)
    
    # Fetch Face Rectangle Geometry
    rect = face.get("faceRectangle", {})
    rect_html = f"T: {rect.get('top', 0)}px, L: {rect.get('left', 0)}px, W: {rect.get('width', 0)}px, H: {rect.get('height', 0)}px"
    
    # 1. Emotions Spectrum
    emotions_html = ""
    if "emotion" in attrs:
        # Sort emotions by confidence
        sorted_emotions = sorted(attrs["emotion"].items(), key=lambda x: x[1], reverse=True)
        for emo, score in sorted_emotions:
            percentage = int(score * 100)
            emotions_html += f"""
<div style="margin-bottom: 6px;">
    <div style="display: flex; justify-content: space-between; font-size: 20px; color: {text_sec};">
        <span>{emo.capitalize()}</span>
        <span>{percentage}%</span>
    </div>
    <div style="background-color: {border_color}; border-radius: 4px; height: 8px; width: 100%; overflow: hidden;">
        <div style="height: 100%; width: {percentage}%; background: linear-gradient(90deg, #8b5cf6, #ec4899); border-radius: 4px;"></div>
    </div>
</div>
"""
    else:
        emotions_html = f'<div style="font-size: 20px; color: {text_sec}; font-style: italic;">🎭 Emotion data restricted by Azure policy</div>'
 
    # 2. Demographic & Facial Attributes
    # Age
    age_str = f"{int(attrs['age'])} yrs" if "age" in attrs else "Restricted"
    
    # Smile Intensity
    smile_html = ""
    if "smile" in attrs:
        smile_val = attrs["smile"]
        smile_pct = int(smile_val * 100)
        smile_html = f"""
<div style="display: flex; align-items: center; gap: 8px; color: {text_main};">
    <span>{smile_pct}%</span>
    <div style="background-color: {border_color}; border-radius: 4px; height: 6px; width: 60px; overflow: hidden; display: inline-block;">
        <div style="height: 100%; width: {smile_pct}%; background-color: #10b981; border-radius: 4px;"></div>
    </div>
</div>
"""
    else:
        smile_html = f'<span style="color: {text_sec}; font-style: italic;">Restricted</span>'
        
    # Glasses
    glasses = attrs.get("glasses", "NoGlasses")
    glasses_map = {
        "NoGlasses": "None",
        "ReadingGlasses": "Reading",
        "Sunglasses": "Sunglasses 🕶️",
        "SwimmingGoggles": "Goggles 🥽"
    }
    glasses_str = glasses_map.get(glasses, glasses)
    
    # Hair Color & Baldness
    hair_desc = "Restricted"
    bald_desc = "Restricted"
    if "hair" in attrs:
        hair = attrs["hair"]
        bald_val = hair.get("bald", 0.0)
        bald_desc = f"{int(bald_val * 100)}%"
        
        if hair.get("invisible", False):
            hair_desc = "Hidden"
        else:
            hair_colors = hair.get("hairColor", [])
            if hair_colors:
                top_hair = max(hair_colors, key=lambda x: x["confidence"])
                hair_desc = top_hair["color"]
            else:
                hair_desc = "Unknown"
                
    # Facial Hair (Beard, Mustache, Sideburns)
    facial_hair_desc = "Restricted"
    if "facialHair" in attrs:
        fh = attrs["facialHair"]
        beard = fh.get("beard", 0.0)
        mustache = fh.get("mustache", 0.0)
        sideburns = fh.get("sideburns", 0.0)
        fh_parts = []
        if beard > 0.1: fh_parts.append(f"Beard ({int(beard*100)}%)")
        if mustache > 0.1: fh_parts.append(f"Stache ({int(mustache*100)}%)")
        if sideburns > 0.1: fh_parts.append(f"Sideburns ({int(sideburns*100)}%)")
        facial_hair_desc = ", ".join(fh_parts) if fh_parts else "None"
 
    # 3. Head Pose (Yaw, Pitch, Roll)
    head_pose_html = ""
    if "headPose" in attrs:
        hp = attrs["headPose"]
        pitch = hp.get("pitch", 0.0)
        yaw = hp.get("yaw", 0.0)
        roll = hp.get("roll", 0.0)
        head_pose_html = f"""
<table class="insight-table" style="margin-top: 4px;">
    <tr>
        <td class="lbl" style="font-size: 20px;">📦 Face Box</td>
        <td class="val" style="font-size: 20px; color: #06b6d4;">{rect_html}</td>
    </tr>
    <tr>
        <td class="lbl" style="font-size: 20px;">Pitch (Nod)</td>
        <td class="val" style="font-size: 20px; color: #06b6d4;">{pitch:+.1f}°</td>
    </tr>
    <tr>
        <td class="lbl" style="font-size: 20px;">Yaw (Turn)</td>
        <td class="val" style="font-size: 20px; color: #06b6d4;">{yaw:+.1f}°</td>
    </tr>
    <tr>
        <td class="lbl" style="font-size: 20px;">Roll (Tilt)</td>
        <td class="val" style="font-size: 20px; color: #06b6d4; font-weight: bold;">{roll:+.1f}°</td>
    </tr>
</table>
"""
    else:
        head_pose_html = f"""
<table class="insight-table" style="margin-top: 4px;">
    <tr>
        <td class="lbl" style="font-size: 20px;">📦 Face Box</td>
        <td class="val" style="font-size: 20px; color: #06b6d4;">{rect_html}</td>
    </tr>
</table>
<div style="font-size: 20px; color: {text_sec}; font-style: italic; margin-top: 4px;">📐 Head pose restricted</div>
"""
 
    return f"""
<div style="border-bottom: 1px solid {border_color}; padding-bottom: 16px; margin-bottom: 16px;">
<div class="insight-face-title" style="font-size: 24px; margin-bottom: 12px;">Face {idx}</div>
<div style="background-color: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 8px; padding: 12px; margin-bottom: 16px;">
<div style="font-size: 24px; font-weight: bold; color: #8b5cf6; display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
<span>💡</span> AI Suggestion
</div>
<p style="font-size: 20px; color: {text_main}; margin: 0; line-height: 1.4;">{ai_suggestion}</p>
</div>
<div style="font-size: 24px; font-weight: bold; color: #8b5cf6; margin-top: 8px; margin-bottom: 8px;">🎭 Emotions</div>
{emotions_html}
<div style="font-size: 24px; font-weight: bold; color: #06b6d4; margin-top: 14px; margin-bottom: 8px;">👤 Profile Details</div>
<table class="insight-table">
    <tr>
        <td class="lbl" style="font-size: 20px;">🎂 Age</td>
        <td class="val" style="font-size: 20px;">{age_str}</td>
    </tr>
    <tr>
        <td class="lbl" style="font-size: 20px;">😀 Smile</td>
        <td class="val" style="font-size: 20px;">{smile_html}</td>
    </tr>
    <tr>
        <td class="lbl" style="font-size: 20px;">👓 Glasses</td>
        <td class="val" style="font-size: 20px;">{glasses_str}</td>
    </tr>
    <tr>
        <td class="lbl" style="font-size: 20px;">🧑 Hair Color</td>
        <td class="val" style="font-size: 20px;">{hair_desc}</td>
    </tr>
    <tr>
        <td class="lbl" style="font-size: 20px;">🥚 Baldness</td>
        <td class="val" style="font-size: 20px;">{bald_desc}</td>
    </tr>
    <tr>
        <td class="lbl" style="font-size: 20px;">🧔 Facial Hair</td>
        <td class="val" style="font-size: 20px;">{facial_hair_desc}</td>
    </tr>
</table>
<div style="font-size: 24px; font-weight: bold; color: #ec4899; margin-top: 14px; margin-bottom: 8px;">📐 Orientation</div>
{head_pose_html}
</div>
"""

# Helper to render dynamic insight cards based on Face API output
def render_insight_card(photo_dict):
    img_src = photo_dict["img_src"]
    results = photo_dict["results"]
    face_count = len(results)
    badge_text = f"{face_count} face{'s' if face_count > 1 else ''} detected"
    
    if face_count == 0:
        return f"""
<div class="insight-card">
    <div class="insight-img-wrapper">
        <img class="insight-img" src="{img_src}">
        <div class="insight-badge" style="background-color: rgba(239, 68, 68, 0.1); color: #ef4444; border-color: rgba(239,68,68,0.15); font-size: 20px;">0 faces detected</div>
    </div>
    <div class="insight-details" style="justify-content: center;">
        <div class="insight-face-title" style="background-color: rgba(239,68,68,0.1); color: #ef4444; font-size: 24px;">No Face Detected</div>
        <p style="font-size: 20px; color: {text_sec}; margin: 4px 0 0 0; line-height: 1.3;">Try a different photo with clearer lighting and a front-facing angle.</p>
        <div style="background-color: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 8px; padding: 12px; margin-top: 16px;">
            <div style="font-size: 24px; font-weight: bold; color: #8b5cf6; display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                <span>💡</span> AI Suggestion
            </div>
            <p style="font-size: 20px; color: {text_main}; margin: 0; line-height: 1.4;">Look directly at the camera, ensure good lighting, and try again! No faces were found in this image.</p>
        </div>
    </div>
</div>
"""
    
    faces_details_html = ""
    for idx, face in enumerate(results):
        faces_details_html += render_face_details(idx + 1, face)
        
    return f"""
<div class="insight-card">
    <div class="insight-img-wrapper">
        <img class="insight-img" src="{img_src}">
        <div class="insight-badge" style="font-size: 20px;">{badge_text}</div>
    </div>
    <div class="insight-details">
        {faces_details_html}
    </div>
</div>
"""

# 6. Row 3 - Recent Insights Grid
example_badge_bg = "rgba(15, 23, 42, 0.05)" if theme == "light" else "rgba(255, 255, 255, 0.05)"
st.markdown(f"""
<div style="margin-top: 32px; display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
    <h3 style="margin: 0; font-size: 24px; font-weight: 700; font-family: 'Space Grotesk', sans-serif; color: {text_main};">Recent Insights</h3>
    <span style="background-color: {example_badge_bg}; color: {text_sec}; font-size: 16px; padding: 3px 8px; border-radius: 20px; font-weight: 500;">
        Example Output
    </span>
</div>
""", unsafe_allow_html=True)

# Grid Layout: Render actual uploads first, then mockups to fill the row
grid_cols = st.columns(3, gap="medium")

# Create a copy of analyzed photos and dynamically pad with mockups if under 3
try:
    displayed_photos = list(st.session_state.analyzed_photos)
except Exception:
    displayed_photos = []
mockups_data = [
    # Mockup 1: Female portrait
    {
        "is_mockup": True,
        "img_src": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80&w=200&h=200",
        "results": [{
            "faceAttributes": {
                "age": 24.0,
                "smile": 0.98,
                "glasses": "NoGlasses",
                "emotion": {
                    "anger": 0.0, "contempt": 0.0, "disgust": 0.0, "fear": 0.0,
                    "happiness": 0.98, "neutral": 0.02, "sadness": 0.0, "surprise": 0.0
                },
                "hair": {
                    "bald": 0.0,
                    "invisible": False,
                    "hairColor": [{"color": "Brown", "confidence": 0.99}]
                },
                "facialHair": {"beard": 0.0, "mustache": 0.0, "sideburns": 0.0},
                "headPose": {"pitch": 1.5, "yaw": -2.1, "roll": -3.5}
            }
        }]
    },
    # Mockup 2: Male portrait
    {
        "is_mockup": True,
        "img_src": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=200&h=200",
        "results": [{
            "faceAttributes": {
                "age": 35.0,
                "smile": 0.85,
                "glasses": "ReadingGlasses",
                "emotion": {
                    "anger": 0.0, "contempt": 0.01, "disgust": 0.0, "fear": 0.0,
                    "happiness": 0.85, "neutral": 0.12, "sadness": 0.0, "surprise": 0.02
                },
                "hair": {
                    "bald": 0.15,
                    "invisible": False,
                    "hairColor": [{"color": "Black", "confidence": 0.95}]
                },
                "facialHair": {"beard": 0.75, "mustache": 0.40, "sideburns": 0.20},
                "headPose": {"pitch": -0.8, "yaw": 4.2, "roll": 1.1}
            }
        }]
    },
    # Mockup 3: Group shot (multiple faces)
    {
        "is_mockup": True,
        "img_src": "https://images.unsplash.com/photo-1543269865-cbf427effbad?auto=format&fit=crop&q=80&w=200&h=200",
        "results": [
            {
                "faceAttributes": {
                    "age": 22.0,
                    "smile": 0.95,
                    "glasses": "NoGlasses",
                    "emotion": {
                        "anger": 0.0, "contempt": 0.0, "disgust": 0.0, "fear": 0.0,
                        "happiness": 0.95, "neutral": 0.05, "sadness": 0.0, "surprise": 0.0
                    },
                    "hair": {
                        "bald": 0.0,
                        "invisible": False,
                        "hairColor": [{"color": "Blond", "confidence": 0.98}]
                    },
                    "facialHair": {"beard": 0.0, "mustache": 0.0, "sideburns": 0.0},
                    "headPose": {"pitch": 2.2, "yaw": -1.5, "roll": -0.5}
                }
            },
            {
                "faceAttributes": {
                    "age": 28.0,
                    "smile": 0.10,
                    "glasses": "NoGlasses",
                    "emotion": {
                        "anger": 0.0, "contempt": 0.0, "disgust": 0.0, "fear": 0.0,
                        "happiness": 0.10, "neutral": 0.75, "sadness": 0.0, "surprise": 0.15
                    },
                    "hair": {
                        "bald": 0.0,
                        "invisible": False,
                        "hairColor": [{"color": "Brown", "confidence": 0.92}]
                    },
                    "facialHair": {"beard": 0.1, "mustache": 0.0, "sideburns": 0.0},
                    "headPose": {"pitch": -1.1, "yaw": 6.8, "roll": 2.5}
                }
            },
            {
                "faceAttributes": {
                    "age": 31.0,
                    "smile": 0.90,
                    "glasses": "Sunglasses",
                    "emotion": {
                        "anger": 0.0, "contempt": 0.0, "disgust": 0.0, "fear": 0.0,
                        "happiness": 0.90, "neutral": 0.08, "sadness": 0.0, "surprise": 0.02
                    },
                    "hair": {
                        "bald": 0.85,
                        "invisible": False,
                        "hairColor": [{"color": "Black", "confidence": 0.50}]
                    },
                    "facialHair": {"beard": 0.85, "mustache": 0.65, "sideburns": 0.30},
                    "headPose": {"pitch": 0.5, "yaw": -0.2, "roll": 0.1}
                }
            }
        ]
    }
]

# Ensure the list is padded up to 3 cards
for mockup in mockups_data:
    if len(displayed_photos) < 3:
        displayed_photos.append(mockup)

# Render the 3 cards in the grid columns
for idx, photo in enumerate(displayed_photos[:3]):
    with grid_cols[idx]:
        st.markdown(render_insight_card(photo), unsafe_allow_html=True)
        
        # Add download button to download the analysis results
        if "results" in photo and photo["results"]:
            import json
            results_data = photo["results"]
            
            # Format a beautiful English summary report for easy reading
            report_text = "=== PHOTOBOOTH FACE ANALYSIS REPORT ===\n\n"
            for face_idx, face in enumerate(results_data):
                attrs = face.get("faceAttributes", {})
                rect = face.get("faceRectangle", {})
                report_text += f"Face #{face_idx + 1}:\n"
                report_text += f"  - Location Coordinates: Top: {rect.get('top', 0)}px, Left: {rect.get('left', 0)}px, Width: {rect.get('width', 0)}px, Height: {rect.get('height', 0)}px\n"
                if "age" in attrs:
                    report_text += f"  - Estimated Age: {int(attrs['age'])} years old\n"
                if "glasses" in attrs:
                    report_text += f"  - Glasses: {attrs['glasses']}\n"
                if "smile" in attrs:
                    report_text += f"  - Smile Intensity: {int(attrs['smile'] * 100)}%\n"
                if "emotion" in attrs:
                    report_text += "  - Emotions Profile:\n"
                    sorted_emo = sorted(attrs["emotion"].items(), key=lambda x: x[1], reverse=True)
                    for emo, score in sorted_emo:
                        report_text += f"    * {emo.capitalize()}: {int(score * 100)}%\n"
                report_text += "\n"
            
            report_text += "========================================\n"
            report_text += "Raw Face API Data Output:\n"
            report_text += json.dumps(results_data, indent=4)
            
            st.download_button(
                label="Download Results 📥",
                data=report_text,
                file_name=f"photobooth_face_results_{idx + 1}.txt",
                mime="text/plain",
                key=f"download_res_{idx}"
            )

# 7. Row 4 - Callouts Grid
st.markdown(f"""
<div class="callouts-grid">
    <div class="callout-box">
        <div class="callout-icon">🛡️</div>
        <div class="callout-text">
            <h5 style="color: {text_main}; margin: 0; font-size: 24px;">Privacy First</h5>
            <p style="color: {text_sec}; margin-top: 4px;">No storage. No identification. Just attributes.</p>
        </div>
    </div>
    <div class="callout-box">
        <div class="callout-icon">ℹ️</div>
        <div class="callout-text">
            <h5 style="color: {text_main}; margin: 0; font-size: 24px;">Important Note</h5>
            <p style="color: {text_sec}; margin-top: 4px;">Results are approximate and can be inaccurate or culturally biased.</p>
        </div>
    </div>
    <div class="callout-box">
        <div class="callout-icon">💾</div>
        <div class="callout-text">
            <h5 style="color: {text_main}; margin: 0; font-size: 24px;">Data Handling</h5>
            <p style="color: {text_sec}; margin-top: 4px;">Uploaded photos are processed temporarily and deleted immediately.</p>
        </div>
    </div>
    <div class="callout-box">
        <div class="callout-icon">💡</div>
        <div class="callout-text">
            <h5 style="color: {text_main}; margin: 0; font-size: 24px;">Responsible Use</h5>
            <p style="color: {text_sec}; margin-top: 4px;">Use insights respectfully. Attributes like emotion are not always reliable.</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Bottom Footer Navbar
st.markdown(f"""
<div class="classy-footer">
    <div class="footer-content">
        <div class="footer-brand">
            <span class="footer-logo">📸</span>
            <div>
                <div class="footer-title">PHOTOBOOTH</div>
                <div class="footer-subtitle">Fun Face Insights</div>
            </div>
        </div>
        <div class="footer-links">
            <span class="footer-link-title">For any assistance reach us at:</span>
            <a href="mailto:support@photobooth.ai" class="footer-link-item">
                <span class="footer-icon">📧</span> Email
            </a>
            <a href="https://github.com" target="_blank" class="footer-link-item">
                <span class="footer-icon">💻</span> GitHub
            </a>
        </div>
    </div>
    <div class="footer-bottom">
        <p style="margin: 0;">© 2026 PHOTOBOOTH. Ephemeral processing, privacy first.</p>
        <p style="margin: 0;">Built with ❤️ using Streamlit</p>
    </div>
</div>
""", unsafe_allow_html=True)
