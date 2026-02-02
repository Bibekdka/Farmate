# Farmate: Agricultural Decision Support System (ADSS)

**Farmate** is an intelligent, data-driven farming assistant designed for farmers in Assam and India. It moves beyond simple record-keeping to provide actionable intelligence using official agricultural models (FPE) and AI.

## ✨ Key Features

### 🧠 **Knowledge Hub & Decision Tools**
- **🧪 Smart Fertilizer Calculator:** Uses *Fertilizer Prescription Equations (FPE)* for Sali Rice to calculate exact Nitrogen, Phosphorus, and Potassium needs based on Soil Test Values.
- **❄️ ZECC Builder:** Helps farmers build a *Zero Energy Cool Chamber* (Pusa Model) to extend produce shelf life by 4x without electricity.
- **💰 Turmeric Profit Engine:** Projects revenue difference between selling raw vs. processed turmeric, factoring in cultivation efficiency (35% loss target).
- **⚠️ Pest Warning System:** Compares farmer observations against *Economic Threshold Levels (ETL)* to advise if chemical action is actually needed.

### 📸 **AI Crop Doctor**
- **Disease Detection:** Uses Google Gemini 1.5 Flash Vision to analyze photos of crops (Tea, Potato, etc.).
- **Instant Diagnosis:** Identifies diseases like *Late Blight* or *Red Rust* and suggests treatments.

### 📊 **Farm Management**
- **Financial Tracking:** Monitor Income vs. Expenses with Category breakdown.
- **Crop Lifecycle:** Track sowing to harvest progress.
- **Weather Integration:** Real-time weather data and history.

---

## 🛠️ Tech Stack
- **Backend:** Python (Flask)
- **Database:** SQLite (SQLAlchemy)
- **AI Engine:** Google Gemini 1.5 Flash
- **Frontend:** HTML5, Bootstrap 5, Jinja2, JavaScript

## 📂 Project Structure
```
Farmate/
├── app.py                 # Main Flask Application
├── ai_service.py          # AI Logic (Gemini Integration)
├── config.py              # App Configuration
├── data/                  # Knowledge Base (JSON)
│   ├── pest_etl.json      # Pest Threshold Data
│   ├── pest_calendar.json # Seasonal Pest Risks
│   └── crop_calendar.json # Sowing Months
├── templates/             # HTML Frontend
│   ├── knowledge.html     # New Decision Tools
│   ├── disease_log.html   # AI Camera Scanner
│   └── ...
└── static/                # CSS/JS Assets
```

## 🚀 Installation

1. **Clone the repo:**
   ```bash
   git clone https://github.com/Bibekdka/Farmate.git
   cd Farmate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   Create a `.env` file:
   ```env
   GEMINI_API_KEY=your_api_key
   SECRET_KEY=your_secret
   ```

4. **Run the App:**
   ```bash
   python app.py
   ```
   Access at `http://127.0.0.1:5000`

---
**Version:** 2.0 (Knowledge Upgrade)
**License:** Open Source

