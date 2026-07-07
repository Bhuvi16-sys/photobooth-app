# 📸 PHOTOBOOTH | Fun Face Insights

A premium, modern, and interactive Web Application built on **Streamlit** that utilizes the **Azure Cognitive Services Face API (v1.0)** to analyze face characteristics, orientations, and expressions ephemerally.

It offers an attractive glassmorphism design system, dynamic theme toggling, centered drag-and-drop mechanics, live photo previews, downloadable reports, and robust fallback simulator configurations (optimal for limited Azure Student pack policies).

---

## ✨ Features

*   **🎨 Premium Glassmorphic UI**: Symmetrical dashboard grid layout with smooth hover elevations, glowing shadows, and curated color systems.
*   **🌓 Dynamic Light & Dark Theme**: Toggle theme modes seamlessly at the top-right corner. All cards, tables, icons, and text adapt their color variables automatically.
*   **📤 Centered Drag-and-Drop Uploader**: Custom styled file drop box with centered instruction text and browse buttons.
*   **🖼️ Live Photo Preview**: Renders a centered preview of the uploaded photo with rounded borders and a capped size constraint so column layouts remain perfectly balanced.
*   **🧠 AI Suggestions**: Dynamic personalized feedback based on detected smile intensities, roll tilt angles, and emotion scores.
*   **📥 Results Report Download**: Download a comprehensive report combining a clean human-readable English report (summarizing coordinates, age, smile, and emotion profiles) and the raw JSON API output in one click.
*   **🛡️ Ephemeral Processing**: Uploaded images are cached temporarily in Azure Blob Storage during API execution and immediately cleaned up afterwards to preserve privacy.
*   **🎓 Restricted Fallback Simulation**: Employs auto-enrichment modules that simulate age, gender, and emotional scales if Azure limits these attributes on the subscription (e.g. Azure Student packs).

---

## ⚙️ How it Works

1.  **Upload**: Drag and drop any `.jpg`, `.jpeg`, or `.png` photo (up to 200MB) containing one or more faces.
2.  **Analyze**: Azure Face API analyzes the geometry coordinates, pose roll, pitch, yaw, and face attributes.
3.  **Enrichment**: The system verifies coordinates and simulates gated attributes if restricted by policy.
4.  **Display & Output**: View interactive face results in the insights columns and click the **Download Results** button to save a text analysis package.

---

## 🚀 Setup & Installation

### 1. Prerequisites
Ensure you have **Python 3.8+** installed. You will also need:
*   An **Azure Face API** cognitive service resource.
*   An **Azure Blob Storage** container named `photo-uploads`.

### 2. Install Dependencies
Clone this repository and install the required Python packages:
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory (you can copy the template from `example.env`):
```bash
cp example.env .env
```
Fill in your credentials:
```env
FACE_API_ENDPOINT="https://your-face-endpoint.cognitiveservices.azure.com/face/v1.0"
FACE_API_KEY="your-face-api-key"
BLOB_CONNECTION_STRING="your-blob-storage-connection-string"
```

### 4. Run the Application
Launch the Streamlit web server:
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## 📁 Repository Structure

```
├── app.py              # Main Streamlit application containing layout and APIs
├── example.env         # Template environment file
├── requirements.txt    # Python library dependencies
└── README.md           # Documentation guide
```

---

## 🛡️ Responsible AI & Privacy Statement

This application does **not** persist, log, or store face vectors or biometric details. Uploaded photos are stored inside a private Azure Blob Container solely for the duration of the API call and deleted immediately afterwards.
