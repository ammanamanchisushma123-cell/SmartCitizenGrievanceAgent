"""
Multi-Language Translation Architecture for Smart Citizen Governance Portal.
Supports English, Telugu (తెలుగు), and Hindi (हिन्दी) with keyed lookups
and graceful fallback to ensure consistent multi-lingual accessibility.
"""

from typing import Dict, Any

LANGUAGES = {
    "en": "English",
    "te": "తెలుగు",
    "hi": "हिन्दी"
}

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # 1. Navigation & App Titles
    "APP_NAME": {
        "en": "SMART CITIZEN GOVERNANCE PORTAL",
        "te": "స్మార్ట్ సిటిజన్ గవర్నెన్స్ పోర్టల్",
        "hi": "स्मार्ट नागरिक शासन पोर्टल"
    },
    "NAV_HOME": {
        "en": "Home",
        "te": "హోమ్",
        "hi": "होम"
    },
    "NAV_GRIEVANCES": {
        "en": "Grievances",
        "te": "ఫిర్యాదులు",
        "hi": "शिकायतें"
    },
    "NAV_TRACK": {
        "en": "Track Complaint",
        "te": "ఫిర్యాదు ట్రాక్ చేయండి",
        "hi": "शिकायत ट्रैक करें"
    },
    "NAV_SCHEMES": {
        "en": "Government Schemes",
        "te": "ప్రభుత్వ పథకాలు",
        "hi": "सरकारी योजनाएं"
    },
    "NAV_SERVICES": {
        "en": "Government Services",
        "te": "ప్రభుత్వ సేవలు",
        "hi": "सरकारी सेवाएं"
    },
    "NAV_AI_ASSISTANT": {
        "en": "AI Assistant",
        "te": "AI సహాయకుడు",
        "hi": "AI सहायक"
    },
    "NAV_EMERGENCY": {
        "en": "Emergency Help",
        "te": "అత్యవసర సహాయం",
        "hi": "आपातकालीन सहायता"
    },
    "NAV_LOGIN_PROFILE": {
        "en": "Login / Profile",
        "te": "లాగిన్ / ప్రొఫైల్",
        "hi": "लॉगिन / प्रोफ़ाइल"
    },

    # 2. Hero Section & Home Page
    "HERO_TITLE": {
        "en": "AI-Powered Government Public Service Portal",
        "te": "AI ఆధారిత ప్రభుత్వ ప్రజా సేవల పోర్టల్",
        "hi": "AI-संचालित सरकारी लोक सेवा पोर्टल"
    },
    "HERO_SUBTITLE": {
        "en": "One platform for citizen grievances, government schemes and public services.",
        "te": "పౌర ఫిర్యాదులు, ప్రభుత్వ పథకాలు మరియు ప్రజా సేవల కొరకు ఏకీకృత వేదిక.",
        "hi": "नागरिक शिकायतों, सरकारी योजनाओं और लोक सेवाओं के लिए एकीकृत मंच।"
    },
    "BTN_SUBMIT_GRIEVANCE": {
        "en": "Submit Grievance",
        "te": "ఫిర్యాదును సమర్పించండి",
        "hi": "शिकायत दर्ज करें"
    },
    "BTN_FIND_SCHEMES": {
        "en": "Find Government Schemes",
        "te": "ప్రభుత్వ పథకాలను కనుగొనండి",
        "hi": "सरकारी योजनाएं खोजें"
    },
    "BTN_TRACK_COMPLAINT": {
        "en": "Track Complaint",
        "te": "ఫిర్యాదు స్థితి చూడండి",
        "hi": "शिकायत की स्थिति जांचें"
    },
    "HOW_IT_WORKS_TITLE": {
        "en": "How It Works",
        "te": "ఇది ఎలా పనిచేస్తుంది",
        "hi": "यह कैसे काम करता है"
    },
    "STEP_1_TITLE": {
        "en": "1. Submit",
        "te": "1. సమర్పించండి",
        "hi": "1. दर्ज करें"
    },
    "STEP_1_DESC": {
        "en": "Enter your grievance details and upload supporting photos or documents.",
        "te": "మీ ఫిర్యాదు వివరాలను నమోదు చేసి, ఆధారాల ఫోటోలు లేదా పత్రాలను అప్‌లోడ్ చేయండి.",
        "hi": "अपनी शिकायत का विवरण दर्ज करें और साक्ष्य फोटो या दस्तावेज अपलोड करें।"
    },
    "STEP_2_TITLE": {
        "en": "2. AI Analysis",
        "te": "2. AI విశ్లేషణ",
        "hi": "2. AI विश्लेषण"
    },
    "STEP_2_DESC": {
        "en": "Machine Learning pipeline analyzes intent, urgency, and category automatically.",
        "te": "మెషిన్ లెర్నింగ్ ద్వారా ఫిర్యాదు తీవ్రత మరియు విభాగాన్ని స్వయంచాలకంగా విశ్లేషిస్తుంది.",
        "hi": "मशीन लर्निंग पाइपलाइन स्वचालित रूप से समस्या की गंभीरता और विभाग का विश्लेषण करती है।"
    },
    "STEP_3_TITLE": {
        "en": "3. Department Routing",
        "te": "3. విభాగ కేటాయింపు",
        "hi": "3. विभाग आवंटन"
    },
    "STEP_3_DESC": {
        "en": "Directly routes to the verified government department and official helpline.",
        "te": "సంబంధిత ప్రభుత్వ విభాగానికి మరియు అధికారిక హెల్ప్‌లైన్‌కు నేరుగా కేటాయిస్తుంది.",
        "hi": "संबंधित सरकारी विभाग और आधिकारिक हेल्पलाइन को सीधे निर्देशित किया जाता है।"
    },
    "STEP_4_TITLE": {
        "en": "4. Track",
        "te": "4. ట్రాక్ చేయండి",
        "hi": "4. ट्रैक करें"
    },
    "STEP_4_DESC": {
        "en": "Receive a unique Complaint ID to monitor real-time redressal progress.",
        "te": "పురోగతిని పర్యవేక్షించడానికి ప్రత్యేకమైన ఫిర్యాదు సంఖ్య (ID) పొందండి.",
        "hi": "शिकायत निवारण की प्रगति की निगरानी के लिए एक विशिष्ट संदर्भ आईडी प्राप्त करें।"
    },
    "STEP_5_TITLE": {
        "en": "5. Resolution / Escalation",
        "te": "5. పరిష్కారం / ఉన్నతాధికారికి నివేదన",
        "hi": "5. समाधान / उच्चाधिकारियों को प्रेषण"
    },
    "STEP_5_DESC": {
        "en": "Get resolved within SLA or escalate to district, state, or central authorities.",
        "te": "నిర్ణీత వ్యవధిలో పరిష్కారం పొందండి లేదా ఉన్నతాధికారులకు అప్పీల్ చేయండి.",
        "hi": "निर्धारित समय में समाधान प्राप्त करें या उच्च अधिकारियों को अपील करें।"
    },

    # 3. Grievance Form & Labels
    "GRIEVANCE_FORM_TITLE": {
        "en": "Lodge Citizen Grievance",
        "te": "పౌర సమస్య ఫిర్యాదు సమర్పణ",
        "hi": "नागरिक शिकायत पंजीकरण"
    },
    "LABEL_COMPLAINT_TEXT": {
        "en": "Complaint Description",
        "te": "ఫిర్యాదు వివరణ",
        "hi": "शिकायत का विवरण"
    },
    "PLACEHOLDER_COMPLAINT": {
        "en": "Describe the civic issue, location details, and how long it has been pending...",
        "te": "సమస్య, ప్రదేశం మరియు ఎన్ని రోజుల నుండి పెండింగ్‌లో ఉందో వివరంగా తెలపండి...",
        "hi": "समस्या, स्थान और कितने समय से लंबित है इसका विवरण लिखें..."
    },
    "LABEL_STATE": {
        "en": "State",
        "te": "రాష్ట్రం",
        "hi": "राज्य"
    },
    "LABEL_DISTRICT": {
        "en": "District",
        "te": "జిల్లా",
        "hi": "ज़िला"
    },
    "LABEL_LOCATION": {
        "en": "Specific Landmark / Street / Ward",
        "te": "నిర్దిష్ట ప్రదేశం / వీధి / వార్డు",
        "hi": "विशिष्ट स्थान / सड़क / वार्ड"
    },
    "LABEL_EVIDENCE_UPLOAD": {
        "en": "Upload Evidence Photo / Document (Max 5MB)",
        "te": "ఆధార ఫోటో / పత్రం అప్‌లోడ్ చేయండి (గరిష్టంగా 5MB)",
        "hi": "साक्ष्य फोटो / दस्तावेज़ अपलोड करें (अधिकतम 5MB)"
    },
    "LABEL_CAMERA_INPUT": {
        "en": "Or Capture Photo via Camera",
        "te": "లేదా కెమెరా ద్వారా ఫోటో తీయండి",
        "hi": "या कैमरे से फोटो खींचें"
    },
    "BTN_SUBMIT": {
        "en": "Submit Grievance",
        "te": "ఫిర్యాదు సమర్పించండి",
        "hi": "शिकायत जमा करें"
    },

    # 4. Grievance Result Card
    "ROUTING_RESULT_TITLE": {
        "en": "AI Grievance Analysis & Department Routing",
        "te": "AI ఫిర్యాదు విశ్లేషణ మరియు విభాగ కేటాయింపు",
        "hi": "AI शिकायत विश्लेषण और विभाग आवंटन"
    },
    "LABEL_RECOMMENDED_DEPT": {
        "en": "Recommended Department",
        "te": "సిఫార్సు చేయబడిన విభాగం",
        "hi": "अनुशंसित विभाग"
    },
    "LABEL_SERVICE_CATEGORY": {
        "en": "Service Category",
        "te": "సేవా వర్గం",
        "hi": "सेवा श्रेणी"
    },
    "LABEL_PRIORITY": {
        "en": "Priority Level",
        "te": "ప్రాధాన్యతా స్థాయి",
        "hi": "प्राथमिकता स्तर"
    },
    "LABEL_TARGET_HOURS": {
        "en": "Target Response Time",
        "te": "లక్ష్య ప్రతిస్పందన సమయం",
        "hi": "लक्षित प्रतिक्रिया समय"
    },
    "LABEL_EMERGENCY_STATUS": {
        "en": "Emergency Status",
        "te": "అత్యవసర స్థితి",
        "hi": "आपातकालीन स्थिति"
    },
    "LABEL_HELPLINE": {
        "en": "Official Helpline",
        "te": "అధికారిక హెల్ప్‌లైన్",
        "hi": "आधिकारिक हेल्पलाइन"
    },
    "LABEL_OFFICIAL_PORTAL": {
        "en": "Official Portal",
        "te": "అధికారిక పోర్టల్",
        "hi": "आधिकारिक पोर्टल"
    },
    "LABEL_COMPLAINT_ID": {
        "en": "Complaint Reference ID",
        "te": "ఫిర్యాదు రిఫరెన్స్ సంఖ్య",
        "hi": "शिकायत संदर्भ संख्या"
    },
    "BTN_VISIT_PORTAL": {
        "en": "Visit Official Portal ↗",
        "te": "అధికారిక పోర్టల్‌ను సందర్శించండి ↗",
        "hi": "आधिकारिक पोर्टल पर जाएं ↗"
    },

    # 5. Tracking & Status Timeline
    "TRACK_TITLE": {
        "en": "Track Grievance Status",
        "te": "ఫిర్యాదు స్థితిని తనిఖీ చేయండి",
        "hi": "शिकायत की स्थिति ट्रैक करें"
    },
    "ENTER_COMPLAINT_ID": {
        "en": "Enter Complaint ID (e.g. GOV-2026-00001)",
        "te": "ఫిర్యాదు సంఖ్యను నమోదు చేయండి (ఉదా: GOV-2026-00001)",
        "hi": "शिकायत आईडी दर्ज करें (उदा. GOV-2026-00001)"
    },
    "STATUS_SUBMITTED": {
        "en": "Submitted",
        "te": "సమర్పించబడింది",
        "hi": "दर्ज किया गया"
    },
    "STATUS_ASSIGNED": {
        "en": "Assigned",
        "te": "కేటాయించబడింది",
        "hi": "आवंटित"
    },
    "STATUS_UNDER_REVIEW": {
        "en": "Under Review",
        "te": "పరిశీలనలో ఉంది",
        "hi": "समीक्षाधीन"
    },
    "STATUS_ACTION_TAKEN": {
        "en": "Action Taken",
        "te": "చర్య తీసుకోబడింది",
        "hi": "कार्रवाई की गई"
    },
    "STATUS_RESOLVED": {
        "en": "Resolved",
        "te": "పరిష్కరించబడింది",
        "hi": "समाधान हो गया"
    },
    "STATUS_ESCALATED": {
        "en": "Escalated",
        "te": "ఉన్నతాధికారికి పంపబడింది",
        "hi": "उच्चाधिकारियों को प्रेषित"
    },

    # 6. Escalation
    "ESCALATE_TITLE": {
        "en": "Escalate Grievance to Higher Authority",
        "te": "ఫిర్యాదును ఉన్నతాధికారికి నివేదించండి",
        "hi": "शिकायत को उच्चाधिकारी के पास अग्रेषित करें"
    },
    "LABEL_ESCALATION_LEVEL": {
        "en": "Escalation Level",
        "te": "నివేదన స్థాయి",
        "hi": "अपील का स्तर"
    },
    "LABEL_ESCALATION_REASON": {
        "en": "Reason for Escalation",
        "te": "నివేదనకు కారణం",
        "hi": "अपील का कारण"
    },
    "LABEL_ADDITIONAL_COMMENTS": {
        "en": "Additional Comments",
        "te": "అదనపు వ్యాఖ్యలు",
        "hi": "अतिरिक्त टिप्पणी"
    },
    "BTN_SUBMIT_ESCALATION": {
        "en": "Submit Escalation",
        "te": "ఉన్నతాధికారికి సమర్పించండి",
        "hi": "अपील दर्ज करें"
    },

    # 7. Schemes & Services
    "SCHEMES_TITLE": {
        "en": "Government Welfare Schemes Discovery",
        "te": "ప్రభుత్వ సంక్షేమ పథకాల శోధన",
        "hi": "सरकारी कल्याणकारी योजनाएं खोजें"
    },
    "SERVICES_TITLE": {
        "en": "Government Public Services Directory",
        "te": "ప్రభుత్వ ప్రజా సేవల డైరెక్టరీ",
        "hi": "सरकारी लोक सेवा निर्देशिका"
    },
    "REQUIRED_DOCUMENTS": {
        "en": "Required Documents",
        "te": "అవసరమైన పత్రాలు",
        "hi": "आवश्यक दस्तावेज़"
    },
    "BENEFITS": {
        "en": "Key Benefits",
        "te": "ప్రధాన ప్రయోజనాలు",
        "hi": "मुख्य लाभ"
    },
    "ELIGIBILITY": {
        "en": "Eligibility Criteria",
        "te": "అర్హత నిబంధనలు",
        "hi": "पात्रता मानदंड"
    },

    # 8. Authentication & Profile
    "LOGIN_TITLE": {
        "en": "Citizen Portal Sign In",
        "te": "పౌర పోర్టల్ లాగిన్",
        "hi": "नागरिक पोर्टल लॉगिन"
    },
    "SIGNUP_TITLE": {
        "en": "New Citizen Registration",
        "te": "కొత్త పౌర నమోదు",
        "hi": "नया नागरिक पंजीकरण"
    },
    "FORGOT_PASSWORD_TITLE": {
        "en": "Reset Your Password",
        "te": "పాస్‌వర్డ్ రీసెట్ చేయండి",
        "hi": "अपना पासवर्ड रीसेट करें"
    },
    "LABEL_FULL_NAME": {
        "en": "Full Name",
        "te": "పూర్తి పేరు",
        "hi": "पूरा नाम"
    },
    "LABEL_MOBILE": {
        "en": "Mobile Number",
        "te": "మొబైల్ నంబర్",
        "hi": "मोबाइल नंबर"
    },
    "LABEL_EMAIL": {
        "en": "Email Address",
        "te": "ఈమెయిల్ చిరునామా",
        "hi": "ईमेल पता"
    },
    "LABEL_PASSWORD": {
        "en": "Password",
        "te": "పాస్‌వర్డ్",
        "hi": "पासवर्ड"
    },
    "LABEL_CONFIRM_PASSWORD": {
        "en": "Confirm Password",
        "te": "పాస్‌వర్డ్‌ను నిర్ధారించండి",
        "hi": "पासवर्ड की पुष्टि करें"
    },
    "LABEL_OTP": {
        "en": "Enter OTP Code",
        "te": "OTP కోడ్‌ను నమోదు చేయండి",
        "hi": "OTP कोड दर्ज करें"
    },
    "BTN_SEND_OTP": {
        "en": "Send SMS OTP",
        "te": "SMS OTP పంపండి",
        "hi": "SMS OTP भेजें"
    },
    "BTN_VERIFY_OTP": {
        "en": "Verify OTP",
        "te": "OTP ని ధృవీకరించండి",
        "hi": "OTP सत्यापित करें"
    },
    "BTN_LOGIN": {
        "en": "Sign In",
        "te": "లాగిన్ అవ్వండి",
        "hi": "साइन इन करें"
    },
    "BTN_SIGNUP": {
        "en": "Register Account",
        "te": "ఖాతాను నమోదు చేయండి",
        "hi": "खाता बनाएं"
    },
    "BTN_LOGOUT": {
        "en": "Sign Out",
        "te": "లాగౌట్",
        "hi": "लॉग आउट"
    },
    "PROFILE_TITLE": {
        "en": "Citizen Profile & Activity",
        "te": "పౌర ప్రొఫైల్ మరియు కార్యకలాపాలు",
        "hi": "नागरिक प्रोफ़ाइल और गतिविधियां"
    },
    "MY_COMPLAINTS": {
        "en": "My Registered Complaints",
        "te": "నా నమోదిత ఫిర్యాదులు",
        "hi": "मेरी पंजीकृत शिकायतें"
    },
    "MY_ESCALATIONS": {
        "en": "My Escalations",
        "te": "నా అప్పీళ్ళు",
        "hi": "मेरी अपीलें"
    }
}


def get_text(key: str, lang: str = "en") -> str:
    """
    Fetches the localized string for a translation key.
    Falls back gracefully to English if the language or key is missing.
    """
    key_dict = TRANSLATIONS.get(key)
    if not key_dict:
        return key

    # Return target language translation or fallback to English
    return key_dict.get(lang, key_dict.get("en", key))

