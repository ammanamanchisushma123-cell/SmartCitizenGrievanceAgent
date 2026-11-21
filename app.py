"""
Smart Citizen Governance Portal - Main Application
A comprehensive, AI-powered citizen-government service portal featuring:
- AI Grievance Classification & Intelligent Department Routing
- Real SMS OTP Provider Architecture
- 5-Stage Complaint Tracking & Multi-Tier Escalation Hierarchy
- Government Welfare Schemes Discovery & Eligibility Engine
- Citizen Public Services Directory across 14 Categories
- AI Governance Assistant & Verified Emergency Helplines
- Multi-Language Translation (English, Telugu, Hindi)
- Secure User Authentication, Profile Management & Admin Analytics
"""

import os
import html
import streamlit as st
import pandas as pd
from PIL import Image
from datetime import datetime

# Import Core System Modules
import database
import auth
import otp
import routing
import escalation
import schemes
import services
import translations
import agent

# ==========================================
# Page Configuration & Metadata
# ==========================================
st.set_page_config(
    page_title="Smart Citizen Governance Portal",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize SQLite Database & Seeding
database.init_db()

# Ensure Uploads Directory Exists
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads"), exist_ok=True)

# ==========================================
# Session State Initialization
# ==========================================
if "language" not in st.session_state:
    st.session_state["language"] = "en"

if "current_nav" not in st.session_state:
    st.session_state["current_nav"] = "Home"

if "user" not in st.session_state:
    st.session_state["user"] = None

if "last_submitted_complaint_id" not in st.session_state:
    st.session_state["last_submitted_complaint_id"] = None

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        {
            "role": "assistant",
            "content": "Namaste & Welcome! I am your **AI Citizen Governance Assistant**. How can I help you today with grievances, schemes, or public services?"
        }
    ]

# Helper for Translation
def tr(key: str) -> str:
    return translations.get_text(key, st.session_state.get("language", "en"))

# ==========================================
# Professional Custom CSS Styling
# ==========================================
st.markdown("""
<style>
    /* Government Portal Theme */
    :root {
        --primary-blue: #0b2545;
        --secondary-blue: #134074;
        --accent-gold: #c89211;
        --accent-saffron: #e65c00;
        --bg-light: #f8fafc;
        --card-bg: #ffffff;
        --text-dark: #1e293b;
        --border-color: #e2e8f0;
    }

    .main-header {
        background: linear-gradient(135deg, #0b2545 0%, #134074 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .portal-title {
        font-size: 1.8rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin: 0;
        color: #ffffff;
    }

    .portal-subtitle {
        font-size: 0.95rem;
        color: #cbd5e1;
        margin-top: 0.25rem;
    }

    .hero-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 3rem 2rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.75rem;
    }

    .hero-subtitle {
        font-size: 1.15rem;
        color: #94a3b8;
        max-width: 800px;
        margin: 0 auto 1.5rem auto;
    }

    .card-service {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
    }
    .card-service:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        border-color: #134074;
    }

    .badge-priority-high {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }

    .badge-priority-med {
        background-color: #fef3c7;
        color: #92400e;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }

    .badge-priority-low {
        background-color: #e0f2fe;
        color: #075985;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }

    .badge-emergency {
        background-color: #dc2626;
        color: white;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-block;
        animation: pulse 2s infinite;
    }

    .timeline-step {
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: 600;
    }
    .timeline-active {
        background-color: #0284c7;
        color: white;
    }
    .timeline-done {
        background-color: #10b981;
        color: white;
    }
    .timeline-pending {
        background-color: #f1f5f9;
        color: #64748b;
        border: 1px solid #cbd5e1;
    }

    .official-link-btn {
        background-color: #0f766e;
        color: white !important;
        padding: 8px 16px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: 600;
        display: inline-block;
        margin-top: 8px;
    }
    .official-link-btn:hover {
        background-color: #115e59;
    }

    .emergency-box {
        background: #fff1f2;
        border-left: 5px solid #e11d48;
        padding: 1.25rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }

    .disclaimer-banner {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 0.85rem;
        color: #475569;
        margin-top: 2rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# Header & Navigation
# ==========================================
def render_header():
    col_logo, col_lang = st.columns([4, 1])
    with col_logo:
        st.markdown(f"""
        <div class="main-header">
            <div>
                <div class="portal-title">🏛️ {tr("APP_NAME")}</div>
                <div class="portal-subtitle">Government Public Grievance Redressal & Citizen Services System</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_lang:
        lang_choice = st.selectbox(
            "🌐 Language / భాష / भाषा",
            options=["en", "te", "hi"],
            format_func=lambda x: {"en": "English", "te": "తెలుగు", "hi": "हिन्दी"}[x],
            index=["en", "te", "hi"].index(st.session_state["language"]),
            key="lang_selector"
        )
        if lang_choice != st.session_state["language"]:
            st.session_state["language"] = lang_choice
            st.rerun()


# ==========================================
# Sidebar Navigation
# ==========================================
def render_sidebar():
    st.sidebar.markdown(f"### 🇮🇳 **{tr('APP_NAME')}**")
    
    # User status snippet in sidebar
    user = st.session_state.get("user")
    if user:
        st.sidebar.write("👤 Logged in as:", user["full_name"])
        if user.get("is_admin"):
            st.sidebar.info("⭐ Role: **Portal Administrator**")
    else:
        st.sidebar.caption("Citizen Access (Guest Mode)")

    st.sidebar.markdown("---")

    nav_options = [
        "Home",
        "Grievances",
        "Track Complaint",
        "Government Schemes",
        "Government Services",
        "AI Assistant",
        "Emergency Help",
        "Login/Profile"
    ]

    selected_nav = st.sidebar.radio(
        "Navigation Menu",
        options=nav_options,
        index=nav_options.index(st.session_state["current_nav"]) if st.session_state["current_nav"] in nav_options else 0,
        format_func=lambda x: {
            "Home": f"🏠 {tr('NAV_HOME')}",
            "Grievances": f"📝 {tr('NAV_GRIEVANCES')}",
            "Track Complaint": f"🔎 {tr('NAV_TRACK')}",
            "Government Schemes": f"🏛️ {tr('NAV_SCHEMES')}",
            "Government Services": f"📑 {tr('NAV_SERVICES')}",
            "AI Assistant": f"🤖 {tr('NAV_AI_ASSISTANT')}",
            "Emergency Help": f"🚨 {tr('NAV_EMERGENCY')}",
            "Login/Profile": f"👤 {tr('NAV_LOGIN_PROFILE')}"
        }.get(x, x)
    )

    if selected_nav != st.session_state["current_nav"]:
        st.session_state["current_nav"] = selected_nav
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📞 National Helplines")
    st.sidebar.markdown("""
    - 🚨 **Emergency SOS**: `112`
    - 🚑 **Ambulance**: `108 / 102`
    - 🛡️ **Cyber Crime**: `1930`
    - 👩 **Women Helpline**: `181`
    - 👴 **Elder Line**: `14567`
    - 🧒 **Childline**: `1098`
    """)

    st.sidebar.markdown("---")
    st.sidebar.caption("🔒 256-Bit SSL Encrypted | Parameterized Storage")


# ==========================================
# 1. Home Page View
# ==========================================
def render_home_page():
    # Hero Section
    st.markdown(f"""
    <div class="hero-container">
        <div class="hero-title">🏛️ {tr("HERO_TITLE")}</div>
        <div class="hero-subtitle">{tr("HERO_SUBTITLE")}</div>
    </div>
    """, unsafe_allow_html=True)

    # Quick Action Buttons
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button(f"📝 {tr('BTN_SUBMIT_GRIEVANCE')}", use_container_width=True, type="primary"):
            st.session_state["current_nav"] = "Grievances"
            st.rerun()
    with c2:
        if st.button(f"🏛️ {tr('BTN_FIND_SCHEMES')}", use_container_width=True):
            st.session_state["current_nav"] = "Government Schemes"
            st.rerun()
    with c3:
        if st.button(f"🔎 {tr('BTN_TRACK_COMPLAINT')}", use_container_width=True):
            st.session_state["current_nav"] = "Track Complaint"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Service Cards Grid (6 Main Services)
    st.markdown("### 🌟 Citizen Services & Portals")
    row1_c1, row1_c2, row1_c3 = st.columns(3)
    with row1_c1:
        st.markdown(f"""
        <div class="card-service">
            <h4>📝 {tr("NAV_GRIEVANCES")}</h4>
            <p>Report municipal, electricity, water, roads, or welfare grievances. AI automatically analyzes urgency and routes to the right authority.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Lodge Grievance →", key="btn_card_grv", use_container_width=True):
            st.session_state["current_nav"] = "Grievances"
            st.rerun()

    with row1_c2:
        st.markdown(f"""
        <div class="card-service">
            <h4>🔎 {tr("NAV_TRACK")}</h4>
            <p>Track real-time progress of your registered complaint with a 5-step transparent redressal timeline and direct officer escalation.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Check Status →", key="btn_card_trk", use_container_width=True):
            st.session_state["current_nav"] = "Track Complaint"
            st.rerun()

    with row1_c3:
        st.markdown(f"""
        <div class="card-service">
            <h4>🏛️ {tr("NAV_SCHEMES")}</h4>
            <p>Find central & state welfare schemes (PM-Kisan, Ayushman Bharat, PMAY, Mudra) with personalized eligibility assessment.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Discover Schemes →", key="btn_card_sch", use_container_width=True):
            st.session_state["current_nav"] = "Government Schemes"
            st.rerun()

    row2_c1, row2_c2, row2_c3 = st.columns(3)
    with row2_c1:
        st.markdown(f"""
        <div class="card-service">
            <h4>📑 {tr("NAV_SERVICES")}</h4>
            <p>Access official public service requirements for Aadhaar, Certificates, Electricity, Water, Sanitation, and Consumer protection.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Explore Services →", key="btn_card_srv", use_container_width=True):
            st.session_state["current_nav"] = "Government Services"
            st.rerun()

    with row2_c2:
        st.markdown(f"""
        <div class="card-service">
            <h4>🤖 {tr("NAV_AI_ASSISTANT")}</h4>
            <p>Ask questions in plain language. Our AI assistant guides you through application processes, helpline routing, and welfare discovery.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ask Assistant →", key="btn_card_ai", use_container_width=True):
            st.session_state["current_nav"] = "AI Assistant"
            st.rerun()

    with row2_c3:
        st.markdown(f"""
        <div class="card-service">
            <h4>🚨 {tr("NAV_EMERGENCY")}</h4>
            <p>Immediate 24/7 verified emergency numbers for Police (112), Ambulance (108), Women safety (181), Cyber Fraud (1930), and LPG leak (1906).</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Emergency Help →", key="btn_card_emg", use_container_width=True):
            st.session_state["current_nav"] = "Emergency Help"
            st.rerun()

    st.markdown("---")

    # "How It Works" Section
    st.markdown(f"### ⚙️ {tr('HOW_IT_WORKS_TITLE')}")
    h1, h2, h3, h4, h5 = st.columns(5)
    with h1:
        st.info(f"**{tr('STEP_1_TITLE')}**\n\n{tr('STEP_1_DESC')}")
    with h2:
        st.info(f"**{tr('STEP_2_TITLE')}**\n\n{tr('STEP_2_DESC')}")
    with h3:
        st.info(f"**{tr('STEP_3_TITLE')}**\n\n{tr('STEP_3_DESC')}")
    with h4:
        st.info(f"**{tr('STEP_4_TITLE')}**\n\n{tr('STEP_4_DESC')}")
    with h5:
        st.info(f"**{tr('STEP_5_TITLE')}**\n\n{tr('STEP_5_DESC')}")


# ==========================================
# 2. Grievance Submission & AI Routing View
# ==========================================
def render_grievance_page():
    st.markdown(f"## 📝 {tr('GRIEVANCE_FORM_TITLE')}")
    st.write("Lodge civic, municipal, utility, or welfare complaints. The machine learning pipeline classifies your complaint and assigns it to the verified department.")

    user = st.session_state.get("user")
    
    # Pre-fill user data if authenticated
    default_name = user["full_name"] if user else ""
    default_mobile = user["mobile"] if user else ""
    default_state = user["state"] if user else "Andhra Pradesh"
    default_district = user["district"] if user else "Vijayawada"

    with st.form("grievance_submission_form", clear_on_submit=False):
        col_name, col_phone = st.columns(2)
        with col_name:
            citizen_name = st.text_input("Citizen Full Name (Optional)", value=default_name)
        with col_phone:
            citizen_mobile = st.text_input("Mobile Number for SMS Updates (Optional)", value=default_mobile)

        complaint_text = st.text_area(
            f"{tr('LABEL_COMPLAINT_TEXT')} *",
            placeholder=tr("PLACEHOLDER_COMPLAINT"),
            height=130
        )

        col_st, col_dt, col_loc = st.columns(3)
        states_list = ["Andhra Pradesh", "Telangana", "Karnataka", "Tamil Nadu"]
        
        with col_st:
            state_idx = states_list.index(default_state) if default_state in states_list else 0
            state = st.selectbox(f"{tr('LABEL_STATE')} *", options=states_list, index=state_idx)

        # Dynamic District selection based on State
        district_options = {
            "Andhra Pradesh": ["Vijayawada", "Visakhapatnam", "Guntur", "Tirupati", "Nellore", "Kurnool", "Kadapa", "Anantapur", "Srikakulam", "Rajahmundry"],
            "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam"],
            "Karnataka": ["Bengaluru", "Mysuru", "Hubballi", "Mangaluru", "Belagavi"],
            "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem"]
        }

        districts = district_options.get(state, ["General"])
        with col_dt:
            dt_idx = districts.index(default_district) if default_district in districts else 0
            district = st.selectbox(f"{tr('LABEL_DISTRICT')} *", options=districts, index=dt_idx)

        with col_loc:
            location = st.text_input(f"{tr('LABEL_LOCATION')}", placeholder="e.g. Ward 12, Main Bazar Road")

        # Evidence Upload Options (File / Camera)
        st.markdown(f"#### 📎 {tr('LABEL_EVIDENCE_UPLOAD')}")
        upload_mode = st.radio("Evidence Input Method", ["File Upload (JPG, PNG, PDF)", "Camera Capture"], horizontal=True)

        uploaded_file = None
        if upload_mode == "File Upload (JPG, PNG, PDF)":
            uploaded_file = st.file_uploader("Select Evidence File (Max 5MB)", type=["jpg", "jpeg", "png", "pdf"])
        else:
            uploaded_file = st.camera_input(tr("LABEL_CAMERA_INPUT"))

        submit_btn = st.form_submit_button(f"🚀 {tr('BTN_SUBMIT')}", type="primary", use_container_width=True)

    if submit_btn:
        if not complaint_text or len(complaint_text.strip()) < 10:
            st.error("⚠️ Please provide a detailed complaint description (at least 10 characters).")
            return

        evidence_path = None
        if uploaded_file is not None:
            ok, ev_msg, saved_path = routing.save_evidence_file(uploaded_file)
            if not ok:
                st.error(f"❌ {ev_msg}")
                return
            evidence_path = saved_path
            st.info(f"📸 **Evidence Status**: {ev_msg}")
            if uploaded_file.type and uploaded_file.type.startswith("image/"):
                st.image(uploaded_file, caption="Uploaded Evidence Preview", width=300)

        # Process Submission & AI Routing
        with st.spinner("🤖 AI Engine Analyzing Intent, Urgency & Department Routing..."):
            success, msg, routing_res = routing.submit_grievance(
                complaint_text=complaint_text,
                state=state,
                district=district,
                location=location,
                citizen_name=citizen_name,
                citizen_mobile=citizen_mobile,
                user_id=user["id"] if user else None,
                evidence_path=evidence_path
            )

        if success:
            st.session_state["last_submitted_complaint_id"] = routing_res["complaint_id"]
            st.success(f"✅ **{msg}** Reference ID: **{routing_res['complaint_id']}**")

            # Render AI Routing Result Card
            st.markdown(f"### 🎯 {tr('ROUTING_RESULT_TITLE')}")
            
            p_badge = "badge-priority-low"
            if routing_res["priority"] == "High":
                p_badge = "badge-priority-high"
            elif routing_res["priority"] == "Medium":
                p_badge = "badge-priority-med"

            emg_badge = '<span class="badge-emergency">🚨 YES (EMERGENCY)</span>' if routing_res["emergency_flag"] == "Yes" else '<span class="badge-priority-low">No</span>'

            st.markdown(f"""
            <div style="background:#ffffff; border:2px solid #134074; border-radius:12px; padding:1.5rem; margin-top:1rem; box-shadow:0 4px 6px rgba(0,0,0,0.05);">
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #e2e8f0; padding-bottom:0.75rem; margin-bottom:1rem;">
                    <span style="font-size:1.2rem; font-weight:700; color:#0b2545;">📌 {tr("LABEL_COMPLAINT_ID")}: {routing_res['complaint_id']}</span>
                    <span class="{p_badge}">Priority: {routing_res['priority']}</span>
                </div>
                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap:1rem;">
                    <div>
                        <strong>🏛️ {tr("LABEL_RECOMMENDED_DEPT")}:</strong><br>
                        <span style="font-size:1.05rem; color:#1e293b; font-weight:600;">{routing_res['recommended_department']}</span>
                    </div>
                    <div>
                        <strong>📂 {tr("LABEL_SERVICE_CATEGORY")}:</strong><br>
                        <span>{routing_res['service_category']}</span>
                    </div>
                    <div>
                        <strong>⏱️ {tr("LABEL_TARGET_HOURS")}:</strong><br>
                        <span>~{routing_res['target_response_hours']} Hours (SLA)</span>
                    </div>
                    <div>
                        <strong>🚨 {tr("LABEL_EMERGENCY_STATUS")}:</strong><br>
                        {emg_badge}
                    </div>
                    <div>
                        <strong>📞 {tr("LABEL_HELPLINE")}:</strong><br>
                        <a href="tel:{routing_res['recommended_helpline']}" style="font-size:1.1rem; font-weight:700; color:#0f766e;">{routing_res['recommended_helpline']}</a> ({routing_res['helpline_name']})
                    </div>
                    <div>
                        <strong>🌐 {tr("LABEL_OFFICIAL_PORTAL")}:</strong><br>
                        <a href="{routing_res['official_portal']}" target="_blank" class="official-link-btn">{tr("BTN_VISIT_PORTAL")}</a>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.balloons()


# ==========================================
# 3. Complaint Tracking View
# ==========================================
def render_tracking_page():
    st.markdown(f"## 🔎 {tr('TRACK_TITLE')}")
    st.write("Monitor the end-to-end redressal progress of your grievance with complete transparency.")

    user = st.session_state.get("user")
    prefill_id = st.session_state.get("last_submitted_complaint_id", "")

    # Quick selector from logged-in user's complaints
    selected_from_list = None
    if user:
        my_complaints = routing.get_user_complaints(user["id"])
        if my_complaints:
            id_options = ["-- Select from My Registered Complaints --"] + [c["complaint_id"] for c in my_complaints]
            choice = st.selectbox("My Registered Grievances", options=id_options)
            if choice != "-- Select from My Registered Complaints --":
                selected_from_list = choice

    search_id = st.text_input(
        f"{tr('ENTER_COMPLAINT_ID')}",
        value=selected_from_list or prefill_id,
        placeholder="e.g. GOV-2026-00001"
    )

    if st.button("Track Status 🔍", type="primary"):
        if not search_id or not search_id.strip():
            st.error("Please enter a valid Complaint Reference ID.")
            return

        complaint = routing.get_complaint_details(search_id)
        if not complaint:
            st.error(f"❌ No complaint record found for ID: `{search_id}`. Please verify your reference number.")
            return

        # Render Complaint Details
        st.markdown(f"### 📋 Grievance Status: **{complaint['complaint_id']}**")
        
        # 5-Stage Visual Progress Timeline
        stages = ["Submitted", "Assigned", "Under Review", "Action Taken", "Resolved"]
        current_status = complaint["status"]

        st.markdown("#### ⏳ Redressal Timeline")
        cols = st.columns(len(stages))
        
        is_escalated = (current_status == "Escalated")
        passed_current = False

        for idx, stage in enumerate(stages):
            with cols[idx]:
                if is_escalated:
                    css_cls = "timeline-done" if idx == 0 else "timeline-pending"
                    st.markdown(f'<div class="timeline-step {css_cls}">{idx+1}. {stage}</div>', unsafe_allow_html=True)
                elif stage == current_status:
                    passed_current = True
                    st.markdown(f'<div class="timeline-step timeline-active">📍 {stage}</div>', unsafe_allow_html=True)
                elif not passed_current:
                    st.markdown(f'<div class="timeline-step timeline-done">✓ {stage}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="timeline-step timeline-pending">{stage}</div>', unsafe_allow_html=True)

        if is_escalated:
            st.warning("⚠️ **This grievance has been escalated to higher authorities for expedited resolution.**")

        st.markdown("<br>", unsafe_allow_html=True)

        # Key Metadata Grid
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write(f"**Department**: {complaint['department']}")
            st.write(f"**Category**: {complaint['category']}")
            st.write(f"**State & District**: {complaint['state']} - {complaint['district']}")
        with c2:
            st.write(f"**Priority**: {complaint['priority']}")
            st.write(f"**Target SLA**: ~{complaint['target_response_hours']} Hours")
            st.write(f"**Submitted Date**: {complaint['submission_time']}")
        with c3:
            st.write(f"**Official Helpline**: `{complaint['helpline']}`")
            if routing.is_valid_url(complaint["official_portal"]):
                st.markdown(f'<a href="{complaint["official_portal"]}" target="_blank" class="official-link-btn">Visit Portal ↗</a>', unsafe_allow_html=True)
            if complaint.get("evidence_path"):
                st.success("📎 Evidence Attached")

        st.markdown("---")
        st.write(f"**Original Complaint Description**:")
        st.info(complaint["complaint_text"])

        # Status History Trail
        if complaint.get("status_history"):
            st.markdown("#### 📜 Audit & Status History")
            for h in complaint["status_history"]:
                st.markdown(f"- **{h['timestamp']}** | **Status**: `{h['new_status']}` | *{h['comment']}* (Updated by: {h['updated_by']})")

        # Direct Escalation Option
        st.markdown("---")
        st.markdown("### ⚠️ Unsatisfied with progress?")
        if st.button("🚀 Escalate Grievance to Higher Authority", key="btn_trigger_esc"):
            st.session_state["escalate_target_id"] = complaint["complaint_id"]
            st.session_state["show_escalation_form"] = True
            st.rerun()

    # If Escalation Triggered
    if st.session_state.get("show_escalation_form") and st.session_state.get("escalate_target_id"):
        render_escalation_form(st.session_state["escalate_target_id"])


def render_escalation_form(complaint_id: str):
    st.markdown(f"### 🛡️ {tr('ESCALATE_TITLE')}: **{complaint_id}**")
    complaint = routing.get_complaint_details(complaint_id)
    if not complaint:
        st.error("Complaint not found.")
        return

    # Fetch verified higher authorities
    verified_auths = escalation.get_verified_authorities(
        department=complaint["department"],
        state=complaint["state"],
        district=complaint["district"]
    )

    with st.form("escalation_form"):
        esc_level = st.selectbox(
            tr("LABEL_ESCALATION_LEVEL"),
            options=["District Authority", "State Authority", "Central Authority", "Local Authority"]
        )

        esc_reason = st.text_input(
            f"{tr('LABEL_ESCALATION_REASON')} *",
            placeholder="e.g. Target SLA exceeded by 5 days without response from local body"
        )

        esc_comments = st.text_area(
            tr("LABEL_ADDITIONAL_COMMENTS"),
            placeholder="Provide additional details or context for the higher authority..."
        )

        esc_evidence = st.file_uploader("Upload Additional Evidence (Optional)", type=["jpg", "jpeg", "png", "pdf"])

        submit_esc_btn = st.form_submit_button(f"🚀 {tr('BTN_SUBMIT_ESCALATION')}", type="primary")

    if submit_esc_btn:
        if not esc_reason or len(esc_reason.strip()) < 5:
            st.error("Please enter a valid escalation reason.")
            return

        ev_path = None
        if esc_evidence:
            _, _, saved_ev = routing.save_evidence_file(esc_evidence)
            ev_path = saved_ev

        user = st.session_state.get("user")
        user_id = user["id"] if user else None

        ok, esc_msg, esc_rec = escalation.escalate_complaint(
            complaint_id=complaint_id,
            reason=esc_reason,
            escalation_level=esc_level,
            comments=esc_comments,
            user_id=user_id,
            additional_evidence_path=ev_path
        )

        if ok:
            st.success(f"✅ {esc_msg}")
            st.markdown(f"""
            <div style="background:#f0fdf4; border:1px solid #22c55e; border-radius:8px; padding:1.25rem; margin-top:1rem;">
                <h4>🏛️ Escalated Authority Details</h4>
                <p><strong>Authority Name</strong>: {html.escape(str(esc_rec.get('authority_name', '')))}</p>
                <p><strong>Helpline</strong>: <a href="tel:{html.escape(str(esc_rec.get('helpline', '')), quote=True)}">{html.escape(str(esc_rec.get('helpline', '')))}</a></p>
                <p><a href="{html.escape(str(esc_rec.get('official_url', 'https://www.india.gov.in/')), quote=True)}" target="_blank" rel="noopener noreferrer" class="official-link-btn">Visit Official Portal ↗</a></p>
            </div>
            """, unsafe_allow_html=True)
            st.session_state["show_escalation_form"] = False
        else:
            st.error(f"❌ {esc_msg}")


# ==========================================
# 4. Government Schemes View
# ==========================================
def render_schemes_page():
    st.markdown(f"## 🏛️ {tr('SCHEMES_TITLE')}")
    st.write("Find Central and State government welfare schemes tailored to your profile, occupation, and family income.")

    # Filter Sidebar / Expanders
    with st.expander("🔍 Filter & Eligibility Calculator", expanded=True):
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            age = st.number_input("Citizen Age (Years)", min_value=0, max_value=110, value=35)
            gender = st.selectbox("Gender", options=["All", "Male", "Female", "Other"])
            state = st.selectbox("State", options=["All", "Andhra Pradesh", "Telangana", "Karnataka", "Tamil Nadu"])

        with f_col2:
            occupation = st.selectbox("Occupation / Profession", options=["All", "Farmer", "Self-Employed / Vendor", "Business / Entrepreneur", "Artisan / Craftsman", "Salaried", "Unemployed", "Student"])
            farmer_status = st.selectbox("Landholding Farmer?", options=["All", "Yes", "No"])
            annual_income = st.number_input("Annual Family Income (₹)", min_value=0, max_value=2000000, value=150000, step=25000)

        with f_col3:
            category = st.selectbox("Social Category", options=["All", "General", "OBC", "SC", "ST", "Minority", "EWS"])
            disability = st.selectbox("Person with Disability (PwD)?", options=["All", "Yes", "No"])
            keyword = st.text_input("Search Keyword", placeholder="e.g. kisan, housing, pension, mudra")

    matching_schemes = schemes.filter_schemes(
        age=age,
        gender=gender,
        state=state,
        occupation=occupation,
        annual_income=annual_income,
        category=category,
        disability=disability,
        farmer=farmer_status,
        search_keyword=keyword
    )

    st.markdown(f"### 📋 Matching Schemes Found: **{len(matching_schemes)}**")

    if not matching_schemes:
        st.warning("No schemes match your exact criteria. Try broadening your filter selections.")
        return

    for s in matching_schemes:
        with st.container():
            st.markdown(f"""
            <div style="background:white; border:1px solid #cbd5e1; border-radius:12px; padding:1.5rem; margin-bottom:1.25rem; box-shadow:0 2px 4px rgba(0,0,0,0.05);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="margin:0; color:#0b2545;">🏛️ {s['scheme_name']}</h3>
                    <span style="background:#e0f2fe; color:#0369a1; padding:4px 10px; border-radius:15px; font-weight:600; font-size:0.85rem;">{s['state']}</span>
                </div>
                <p style="color:#475569; margin-top:0.5rem; font-size:1rem;">{s['description']}</p>
                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:1rem; background:#f8fafc; padding:1rem; border-radius:8px; margin-top:0.75rem;">
                    <div>
                        <strong>🎁 {tr("BENEFITS")}:</strong><br>
                        <span style="color:#15803d; font-weight:600;">{s['benefits']}</span>
                    </div>
                    <div>
                        <strong>📄 {tr("REQUIRED_DOCUMENTS")}:</strong><br>
                        <span>{s['documents']}</span>
                    </div>
                </div>
                <div style="margin-top:1rem; text-align:right;">
                    <a href="{s['official_url']}" target="_blank" class="official-link-btn">Official Application Portal ↗</a>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ==========================================
# 5. Government Services Directory View
# ==========================================
def render_services_page():
    st.markdown(f"## 📑 {tr('SERVICES_TITLE')}")
    st.write("Browse verified government citizen services, document checklists, and application guidelines across 14 public categories.")

    col_cat, col_srch, col_st = st.columns([1.5, 2, 1])
    with col_cat:
        cat_filter = st.selectbox("Category", options=services.get_service_categories())
    with col_srch:
        kw_filter = st.text_input("Search Service or Document", placeholder="e.g. Aadhaar update, Birth certificate, Pothole")
    with col_st:
        st_filter = st.selectbox("State Filter", options=["All", "Andhra Pradesh", "Telangana", "Karnataka", "Tamil Nadu"])

    service_list = services.filter_services(category=cat_filter, search_keyword=kw_filter, state=st_filter)

    st.markdown(f"### 📋 Available Citizen Services: **{len(service_list)}**")

    for s in service_list:
        with st.container():
            st.markdown(f"""
            <div style="background:white; border:1px solid #cbd5e1; border-radius:12px; padding:1.25rem; margin-bottom:1rem; box-shadow:0 2px 4px rgba(0,0,0,0.05);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="margin:0; color:#0b2545;">📄 {s['service_name']}</h4>
                    <span style="background:#f1f5f9; color:#475569; padding:4px 8px; border-radius:12px; font-size:0.8rem; font-weight:600;">{s['category']}</span>
                </div>
                <p style="color:#64748b; margin:0.4rem 0;"><strong>Department:</strong> {s['department']}</p>
                <p style="color:#334155;">{s['description']}</p>
                <div style="background:#f8fafc; border-left:3px solid #134074; padding:0.75rem 1rem; border-radius:4px; margin-top:0.5rem;">
                    <strong>📑 Required Documents:</strong> {s['documents']}
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:0.75rem;">
                    <span>📞 Helpline: <a href="tel:{s['helpline']}" style="font-weight:700; color:#0f766e;">{s['helpline']}</a></span>
                    <a href="{s['official_url']}" target="_blank" class="official-link-btn">Access Service Portal ↗</a>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ==========================================
# 6. AI Assistant View
# ==========================================
def render_ai_assistant_page():
    st.markdown(f"## 🤖 {tr('NAV_AI_ASSISTANT')}")
    st.caption("Automated Public Service & Grievance Guidance Engine. Ask questions in natural language.")

    # Render Chat History
    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input Box
    user_prompt = st.chat_input("Ask a question (e.g. 'How do I report a broken road?' or 'Tell me about PM Kisan')")

    if user_prompt:
        # Add user message
        st.session_state["chat_history"].append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Generate Assistant Response
        with st.chat_message("assistant"):
            with st.spinner("AI Assistant is analyzing governance records..."):
                resp = agent.get_assistant_response(user_prompt, lang=st.session_state.get("language", "en"))
                st.markdown(resp["answer"])
                st.session_state["chat_history"].append({"role": "assistant", "content": resp["answer"]})


# ==========================================
# 7. Emergency Help View
# ==========================================
def render_emergency_page():
    st.markdown(f"## 🚨 {tr('NAV_EMERGENCY')}")
    st.write("24/7 Verified National & State Emergency Helplines. Direct call access for crisis and life-safety situations.")

    st.markdown("""
    <div class="emergency-box">
        <h3 style="color:#991b1b; margin-top:0;">⚠️ IMMEDIATE LIFE-THREATENING EMERGENCY?</h3>
        <p style="font-size:1.1rem; color:#b91c1c; margin-bottom:0;">
            Dial <strong>112</strong> immediately for unified emergency police, medical, and disaster response.
        </p>
    </div>
    """, unsafe_allow_html=True)

    emergency_contacts = [
        {"name": "National Unified Emergency SOS", "number": "112", "service": "Police, Medical & Fire", "url": "https://www.india.gov.in/", "color": "#dc2626"},
        {"name": "National Ambulance Service", "number": "108 / 102", "service": "Emergency Medical Response", "url": "https://www.india.gov.in/", "color": "#0284c7"},
        {"name": "Fire & Rescue Control Room", "number": "101", "service": "Fire Safety & Rescue", "url": "https://www.india.gov.in/", "color": "#ea580c"},
        {"name": "National Cyber Crime Helpline", "number": "1930", "service": "Financial Fraud & Cyber Harassment", "url": "https://www.cybercrime.gov.in/", "color": "#7c3aed"},
        {"name": "Women Crisis Helpline", "number": "181 / 1091", "service": "24/7 Women in Distress Support", "url": "https://wcd.nic.in/", "color": "#db2777"},
        {"name": "National LPG Leak Emergency", "number": "1906", "service": "Cooking Gas Cylinder Leaks", "url": "https://www.mylpg.in/", "color": "#d97706"},
        {"name": "Childline India", "number": "1098", "service": "Care & Protection of Children", "url": "https://www.india.gov.in/", "color": "#059669"},
        {"name": "National Elder Line", "number": "14567", "service": "Senior Citizen Welfare & Abuse Redressal", "url": "https://socialjustice.gov.in/", "color": "#4b5563"}
    ]

    c1, c2 = st.columns(2)
    for idx, ec in enumerate(emergency_contacts):
        target_col = c1 if idx % 2 == 0 else c2
        with target_col:
            st.markdown(f"""
            <div style="background:white; border-left:6px solid {ec['color']}; border-radius:10px; padding:1.25rem; margin-bottom:1rem; box-shadow:0 2px 4px rgba(0,0,0,0.05);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="margin:0; color:#1e293b;">{ec['name']}</h4>
                </div>
                <p style="color:#64748b; margin:0.25rem 0;">{ec['service']}</p>
                <div style="margin-top:0.75rem; display:flex; justify-content:space-between; align-items:center;">
                    <a href="tel:{ec['number'].split('/')[0].strip()}" style="font-size:1.4rem; font-weight:800; color:{ec['color']}; text-decoration:none;">📞 {ec['number']}</a>
                    <a href="{ec['url']}" target="_blank" class="official-link-btn">Official Info ↗</a>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ==========================================
# 8. Authentication & Profile View
# ==========================================
def render_auth_page():
    user = st.session_state.get("user")

    if user:
        render_user_profile(user)
    else:
        render_login_signup()


def render_login_signup():
    auth_tab = st.radio("Choose Action", ["Sign In", "New Registration", "Forgot Password"], horizontal=True)

    # 1. Sign In Tab
    if auth_tab == "Sign In":
        st.markdown(f"### 🔑 {tr('LOGIN_TITLE')}")
        with st.form("login_form"):
            ident = st.text_input("Registered Mobile Number or Email", placeholder="e.g. 9876543210 or citizen@email.com")
            password = st.text_input(tr("LABEL_PASSWORD"), type="password")
            login_btn = st.form_submit_button(f"🚀 {tr('BTN_LOGIN')}", type="primary", use_container_width=True)

        if login_btn:
            ok, msg, user_dict = auth.authenticate_user(ident, password)
            if ok:
                st.session_state["user"] = user_dict
                st.success(f"✅ {msg}")
                st.rerun()
            else:
                st.error(f"❌ {msg}")

    # 2. New Registration Tab
    elif auth_tab == "New Registration":
        st.markdown(f"### 📝 {tr('SIGNUP_TITLE')}")
        
        # SMS Configuration Notification
        if not otp.is_sms_configured():
            st.info("ℹ️ **SMS Gateway Notice**: Real SMS OTP credentials are not configured. Registration is disabled by default until phone verification is available. For local development only, set ALLOW_UNVERIFIED_SIGNUP=true.")

        with st.form("signup_form"):
            r_name = st.text_input(f"{tr('LABEL_FULL_NAME')} *")
            
            c_mob, c_em = st.columns(2)
            with c_mob:
                r_mob = st.text_input(f"{tr('LABEL_MOBILE')} (10 Digits) *", max_chars=10)
            with c_em:
                r_email = st.text_input(f"{tr('LABEL_EMAIL')} *")

            c_st, c_dt = st.columns(2)
            with c_st:
                r_state = st.selectbox(f"{tr('LABEL_STATE')} *", options=["Select State", "Andhra Pradesh", "Telangana", "Karnataka", "Tamil Nadu"])
            with c_dt:
                r_district = st.selectbox(f"{tr('LABEL_DISTRICT')} *", options=["Select District", "Vijayawada", "Visakhapatnam", "Guntur", "Hyderabad", "Bengaluru", "Chennai"])

            c_p1, c_p2 = st.columns(2)
            with c_p1:
                r_pw = st.text_input(f"{tr('LABEL_PASSWORD')} *", type="password")
            with c_p2:
                r_pw2 = st.text_input(f"{tr('LABEL_CONFIRM_PASSWORD')} *", type="password")

            otp_val = None
            if otp.is_sms_configured():
                otp_val = st.text_input(tr("LABEL_OTP"), placeholder="Enter 6-digit verification code")

            register_btn = st.form_submit_button(f"🚀 {tr('BTN_SIGNUP')}", type="primary", use_container_width=True)

        if register_btn:
            ok, msg = auth.register_user(
                full_name=r_name,
                mobile=r_mob,
                email=r_email,
                state=r_state,
                district=r_district,
                password=r_pw,
                confirm_password=r_pw2,
                otp_code=otp_val
            )
            if ok:
                st.success(f"✅ {msg}")
            else:
                st.error(f"❌ {msg}")

    # 3. Forgot Password Tab
    elif auth_tab == "Forgot Password":
        st.markdown(f"### 🔄 {tr('FORGOT_PASSWORD_TITLE')}")
        
        if not otp.is_sms_configured():
            st.warning("⚠️ SMS verification is not configured. Add the SMS provider credentials to enable real OTP.")
            return

        with st.form("forgot_pw_form"):
            f_ident = st.text_input("Enter Registered Mobile Number or Email")
            send_otp_btn = st.form_submit_button(f"📲 {tr('BTN_SEND_OTP')}")

        if send_otp_btn:
            ok, msg = auth.request_password_reset_otp(f_ident)
            if ok:
                st.success(f"✅ {msg}")
            else:
                st.error(f"❌ {msg}")


def render_user_profile(user: dict):
    st.markdown(f"## 👤 {tr('PROFILE_TITLE')}")
    st.write(f"Welcome back, {user['full_name']}! Access your registered complaints, escalations, and manage account settings.")

    p_tab1, p_tab2, p_tab3, p_tab4 = st.tabs([
        f"📋 {tr('MY_COMPLAINTS')}",
        f"🛡️ {tr('MY_ESCALATIONS')}",
        "⚙️ Account Settings",
        "📊 Admin Analytics" if user.get("is_admin") else "ℹ️ Citizen Card"
    ])

    # Tab 1: My Registered Complaints
    with p_tab1:
        my_complaints = routing.get_user_complaints(user["id"])
        if not my_complaints:
            st.info("You have not registered any grievances yet. Click 'Grievances' to lodge a new complaint.")
        else:
            for c in my_complaints:
                with st.expander(f"📌 {c['complaint_id']} - {c['department']} ({c['status']})"):
                    st.write(f"**Submitted**: {c['submission_time']} | **Priority**: {c['priority']} | **Location**: {c['district']}, {c['state']}")
                    st.write(f"**Description**: {c['complaint_text']}")
                    st.write(f"**Helpline**: `{c['helpline']}` ({c['helpline_name']})")
                    if routing.is_valid_url(c["official_portal"]):
                        st.markdown(f'<a href="{c["official_portal"]}" target="_blank" class="official-link-btn">Official Portal ↗</a>', unsafe_allow_html=True)

    # Tab 2: My Escalations
    with p_tab2:
        my_esc = escalation.get_user_escalations(user["id"])
        if not my_esc:
            st.info("No escalated grievances on record.")
        else:
            for e in my_esc:
                st.markdown(f"""
                <div style="background:#f8fafc; border-left:4px solid #ea580c; padding:1rem; border-radius:6px; margin-bottom:0.75rem;">
                    <strong>Escalation for {html.escape(str(e.get('complaint_id', '')))}</strong> ({html.escape(str(e.get('escalation_level', '')))})<br>
                    <strong>Reason</strong>: {html.escape(str(e.get('reason', '')))}<br>
                    <strong>Authority</strong>: {html.escape(str(e.get('authority_name', '')))} | <strong>Helpline</strong>: {html.escape(str(e.get('helpline', '')))}
                </div>
                """, unsafe_allow_html=True)

    # Tab 3: Account Settings
    with p_tab3:
        st.markdown("#### Edit Profile Details")
        st.caption("Note: Verified mobile number cannot be changed without SMS re-verification.")
        with st.form("edit_profile_form"):
            e_name = st.text_input("Full Name", value=user["full_name"])
            e_email = st.text_input("Email", value=user["email"])
            profile_states = ["Andhra Pradesh", "Telangana", "Karnataka", "Tamil Nadu"]
            current_state = user.get("state", "Andhra Pradesh")
            state_index = profile_states.index(current_state) if current_state in profile_states else 0
            e_state = st.selectbox("State", options=profile_states, index=state_index)
            profile_districts = {
                "Andhra Pradesh": ["Vijayawada", "Visakhapatnam", "Guntur", "Tirupati", "Nellore", "Kurnool", "Kadapa", "Anantapur", "Srikakulam", "Rajahmundry"],
                "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam"],
                "Karnataka": ["Bengaluru", "Mysuru", "Hubballi", "Mangaluru", "Belagavi"],
                "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem"]
            }
            districts_for_state = profile_districts.get(e_state, [])
            saved_district = user.get("district", "")
            if saved_district and saved_district not in districts_for_state:
                districts_for_state = [saved_district] + districts_for_state
            district_index = districts_for_state.index(saved_district) if saved_district in districts_for_state else 0
            e_district = st.selectbox("District", options=districts_for_state, index=district_index)
            update_btn = st.form_submit_button("Update Profile", type="primary")

        if update_btn:
            ok, msg = auth.update_user_profile(user["id"], e_name, e_email, e_state, e_district)
            if ok:
                st.session_state["user"]["full_name"] = e_name
                st.session_state["user"]["email"] = e_email
                st.session_state["user"]["state"] = e_state
                st.session_state["user"]["district"] = e_district
                st.success("✅ Profile updated successfully.")
                st.rerun()
            else:
                st.error(f"❌ {msg}")

    # Tab 4: Admin Dashboard (or Citizen ID Card)
    with p_tab4:
        if user.get("is_admin"):
            render_admin_dashboard()
        else:
            st.markdown(f"""
            <div style="background:white; border:2px solid #0b2545; border-radius:12px; padding:1.5rem; max-width:450px;">
                <h4 style="color:#0b2545; margin:0;">🏛️ SMART CITIZEN DIGITAL ID</h4>
                <hr style="margin:0.5rem 0;">
                <p><strong>Name</strong>: {html.escape(str(user.get('full_name', '')))}</p>
                <p><strong>Mobile</strong>: +91 {html.escape(str(user.get('mobile', '')))}</p>
                <p><strong>Email</strong>: {html.escape(str(user.get('email', '')))}</p>
                <p><strong>Jurisdiction</strong>: {html.escape(str(user.get('district', '')))}, {html.escape(str(user.get('state', '')))}</p>
                <p><strong>Status</strong>: Active Verified Citizen</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button(f"🚪 {tr('BTN_LOGOUT')}", type="secondary"):
        st.session_state["user"] = None
        st.rerun()


# ==========================================
# 9. Admin Dashboard View
# ==========================================
def render_admin_dashboard():
    st.markdown("### 📊 Grievance Redressal Administration & Analytics")
    
    # Summary Metrics
    total_complaints = database.execute_query("SELECT COUNT(*) as c FROM complaints")[0]["c"]
    submitted = database.execute_query("SELECT COUNT(*) as c FROM complaints WHERE status = 'Submitted'")[0]["c"]
    resolved = database.execute_query("SELECT COUNT(*) as c FROM complaints WHERE status = 'Resolved'")[0]["c"]
    escalated = database.execute_query("SELECT COUNT(*) as c FROM complaints WHERE status = 'Escalated'")[0]["c"]
    high_priority = database.execute_query("SELECT COUNT(*) as c FROM complaints WHERE priority = 'High'")[0]["c"]
    emergency = database.execute_query("SELECT COUNT(*) as c FROM complaints WHERE emergency_flag = 'Yes'")[0]["c"]

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Total Complaints", total_complaints)
    m2.metric("Submitted", submitted)
    m3.metric("Resolved", resolved)
    m4.metric("Escalated", escalated)
    m5.metric("High Priority", high_priority)
    m6.metric("Emergency", emergency)

    st.markdown("---")

    # Analytics Charts
    all_complaints = database.execute_query("SELECT * FROM complaints")
    if all_complaints:
        df_comp = pd.DataFrame(all_complaints)
        
        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown("#### Complaints by Department")
            dept_counts = df_comp["department"].value_counts().reset_index()
            dept_counts.columns = ["Department", "Count"]
            st.bar_chart(dept_counts.set_index("Department"))

        with c_right:
            st.markdown("#### Complaints by Priority")
            priority_counts = df_comp["priority"].value_counts().reset_index()
            priority_counts.columns = ["Priority", "Count"]
            st.bar_chart(priority_counts.set_index("Priority"))

        # Manage Complaint Status Tool (For College/Demo Evaluation)
        st.markdown("---")
        st.markdown("#### 🛠️ Update Complaint Status (Demo / Admin Redressal)")
        with st.form("admin_status_update"):
            c_select_id = st.selectbox("Select Complaint ID to Update", options=df_comp["complaint_id"].tolist())
            new_st = st.selectbox("New Redressal Status", options=["Submitted", "Assigned", "Under Review", "Action Taken", "Resolved", "Escalated"])
            admin_note = st.text_input("Officer Action / Resolution Comment", value="Inspected by field municipal officer and resolved.")
            update_status_btn = st.form_submit_button("Update Status", type="primary")

        if update_status_btn:
            old_s = database.execute_query("SELECT status FROM complaints WHERE complaint_id = ?", (c_select_id,))[0]["status"]
            database.execute_update("UPDATE complaints SET status = ? WHERE complaint_id = ?", (new_st, c_select_id))
            database.execute_insert(
                "INSERT INTO complaint_status_history (complaint_id, old_status, new_status, comment, updated_by) VALUES (?, ?, ?, ?, 'Portal Admin')",
                (c_select_id, old_s, new_st, admin_note)
            )
            st.success(f"✅ Complaint {c_select_id} status updated to '{new_st}'.")
            st.rerun()


# ==========================================
# Main App Router
# ==========================================
def main():
    render_header()
    render_sidebar()

    current_nav = st.session_state.get("current_nav", "Home")

    if current_nav == "Home":
        render_home_page()
    elif current_nav == "Grievances":
        render_grievance_page()
    elif current_nav == "Track Complaint":
        render_tracking_page()
    elif current_nav == "Government Schemes":
        render_schemes_page()
    elif current_nav == "Government Services":
        render_services_page()
    elif current_nav == "AI Assistant":
        render_ai_assistant_page()
    elif current_nav == "Emergency Help":
        render_emergency_page()
    elif current_nav == "Login/Profile":
        render_auth_page()

    # Footer Disclaimer Banner
    st.markdown("""
    <div class="disclaimer-banner">
        🏛️ <strong>Smart Citizen Governance Portal</strong> — Academic & Public Service Demonstration.<br>
        <em>The current grievance dataset is synthetic and is used for academic/project demonstration. Real government department submission requires authorized API/integration and is not implied by this application.</em>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

