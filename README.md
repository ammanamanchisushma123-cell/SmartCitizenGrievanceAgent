# 🏛️ Smart Citizen Governance Portal (SmartCitizenGrievanceAgent)

An AI-powered public governance and citizen service delivery portal designed to automate grievance classification, department routing, multi-tier escalation, welfare scheme discovery, and emergency helpline access.

---

## 📌 Project Objective

The **Smart Citizen Governance Portal** bridges the gap between citizens and public administration by providing a unified, intelligent, and transparent digital interface. Leveraging pre-trained Natural Language Processing (NLP) models, the portal automatically analyzes citizen complaint text, identifies urgency, determines service categories, assigns the grievance to the exact government department, and provides verified helplines and official redressal portals.

---

## 🌟 Key Features

1. **AI Grievance Routing & Classification**:
   - Classifies unstructured complaint text into 18 public departments using a TF-IDF + Logistic Regression pipeline.
   - Enriches predictions with verified official helplines, SLA response targets, and government portals.
   - Generates unique reference IDs (e.g. `GOV-2026-00001XXXX`).

2. **Secure Evidence Upload & Media Handling**:
   - Citizen evidence uploads (JPG, PNG, PDF) and camera photo capture.
   - Enforces 5MB size limits and safe unguessable UUID storage in `uploads/`.
   - Clear disclaimers regarding evidence submission.

3. **5-Stage Complaint Tracking & Multi-Tier Escalation**:
   - Visual progress timeline: `Submitted` ➔ `Assigned` ➔ `Under Review` ➔ `Action Taken` ➔ `Resolved`.
   - Multi-tier escalation hierarchy (`Local Authority`, `District Authority`, `State Authority`, `Central Authority`) with verified contact directories.

4. **Real SMS OTP Provider Architecture**:
   - Provider-based SMS OTP architecture supporting Twilio Verify.
   - Rate limiting, 60s resend cooldown, 10-minute expiration, and attempt limits.
   - Transparent notifications when SMS credentials are unconfigured without showing fake OTPs.

5. **Citizen Authentication & Security**:
   - Secure password hashing with `bcrypt` (12 rounds of salt).
   - Parameterized SQLite queries protecting against SQL injection.
   - Citizen profile dashboard with registered grievances and escalation tracking.

6. **Government Welfare Schemes Discovery**:
   - Multi-criteria eligibility assessment (Age, Gender, State, Occupation, Annual Income, Social Category, Disability, Farmer status).
   - Grounded links to verified portals (PM-Kisan, Ayushman Bharat PM-JAY, PMAY, Mudra, PM SVANidhi, etc.).

7. **Citizen Public Services Directory**:
   - 14 essential service domains (Aadhaar, Pension, Birth/Death Certificates, Electricity, Water, Roads, Sanitation, Cyber Crime, LPG, etc.).
   - Detailed checklists of required documents, helplines, and direct portals.

8. **AI Governance Assistant**:
   - Natural language conversational assistant for civic issue routing, welfare discovery, and emergency contacts.
   - Grounded rule-based / ML routing with optional Google Gemini API support.

9. **24/7 Verified Emergency Helplines**:
   - Instant clickable `tel:` links for Police (112), Ambulance (108), Fire (101), Women in Distress (181/1091), Cyber Crime (1930), and LPG Leaks (1906).

10. **Multi-Language Accessibility**:
    - Complete translation architecture supporting **English**, **Telugu (తెలుగు)**, and **Hindi (हिन्दी)**.

11. **Admin Analytics Dashboard**:
    - Grievance breakdown charts by department, priority, and status.
    - Demonstration status management tool for academic evaluations.

---

## 🏗️ System Architecture & File Structure

```
SmartCitizenGrievanceAgent/
│
├── data/
│   └── smart_citizen_grievance_routing_dataset.csv  # 6,000-row grievance metadata dataset
│
├── models/
│   └── grievance_routing_model.pkl                  # Trained TF-IDF + LogisticRegression pipeline
│
├── uploads/                                         # Safe user evidence storage
│
├── app.py                                           # Streamlit web application & router
├── agent.py                                         # AI Assistant (ML routing + verified rules)
├── routing.py                                       # ML inference & metadata enrichment
├── auth.py                                          # User authentication & bcrypt security
├── otp.py                                           # Provider-based SMS OTP architecture
├── database.py                                      # SQLite parameterized models & seeding
├── escalation.py                                    # Multi-level authority directory & escalations
├── schemes.py                                       # Government schemes catalog & eligibility
├── services.py                                      # 14-category public services directory
├── translations.py                                  # Multi-language dictionary (EN, TE, HI)
├── requirements.txt                                 # Production dependencies (Python 3.12 compatible)
├── .env.example                                     # Template for environment credentials
└── README.md                                        # Project documentation
```

---

## 🤖 Machine Learning Model & Dataset

- **Model Type**: scikit-learn `Pipeline` combining `TfidfVectorizer(ngram_range=(1,2), sublinear_tf=True)` and `LogisticRegression(class_weight='balanced', max_iter=2000)`.
- **Target Variable**: `recommended_department` across 18 specialized public administration domains:
  - *Municipal Sanitation / Local Body*
  - *Municipal Electrical / Local Body*
  - *Water Supply / Local Urban or Rural Body*
  - *Electricity Distribution Utility*
  - *Roads / Municipal or Rural Roads Authority*
  - *Social Welfare / Pension Administration*
  - *UIDAI (Aadhaar)*
  - *Birth & Death Registration Authority*
  - *National Consumer Helpline*
  - *Cyber Crime Police*
  - *Women Helpline / Police Support*
  - *Child Protection Services*
  - *Senior Citizens Helpline / Support Services*
  - *Disability Support Services*
  - *Emergency Response Services (112)*
  - *National Ambulance Service (108)*
  - *LPG Emergency Support (1906)*
  - *CPGRAMS / Concerned Government Authority*

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- Python 3.12 or Python 3.10+
- `pip` package manager

### 2. Clone / Open Project Directory
```bash
cd SmartCitizenGrievanceAgent
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (Optional)
Copy `.env.example` to `.env` and provide your credentials if using real SMS OTP or Gemini LLM:
```bash
cp .env.example .env
```
Inside `.env`:
```env
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_VERIFY_SERVICE_SID=your_twilio_verify_service_sid
GEMINI_API_KEY=your_gemini_api_key
```
*(If SMS credentials are not provided, the application safely informs the citizen and allows direct registered access).*

---

## 🚀 How to Run

Launch the Streamlit web application:

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

---

## 🔒 Security & Privacy

- **Password Security**: Passwords are never stored in plaintext; all credentials use salted `bcrypt` hashes.
- **SQL Injection Prevention**: All SQLite queries use strict parameter substitution (`?`).
- **File Upload Protection**: Enforces file extension whitelisting (`.jpg`, `.jpeg`, `.png`, `.pdf`), maximum 5MB size limit, and unguessable UUID filenames.
- **Credential Hygiene**: Sensitive API tokens and credentials are read exclusively from environment variables and never logged or exposed.

---

## ⚠️ Important Disclaimers & Limitations

> [!IMPORTANT]
> - **The current grievance dataset is synthetic and is used for academic/project demonstration.**
> - **Real government department submission requires authorized API/integration and is not implied by this application.**
> - Escalation and tracking timelines are simulated for educational evaluation. Official department action requires designated ministerial API endpoints.

