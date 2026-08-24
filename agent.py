"""
AI Governance Assistant Module.
Provides intelligent query resolution, department routing guidance, scheme discovery,
and public service navigation using pre-trained ML models, grounded datasets,
and optional LLM enhancement (Gemini API).
"""

import os
import re
from typing import Dict, Any, List, Optional
import routing
import schemes
import services

# Check for Optional LLM API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "").strip()


def get_assistant_response(query: str, lang: str = "en") -> Dict[str, Any]:
    """
    Processes citizen queries and generates grounded, accurate governance assistance.
    Handles emergency questions, grievance department routing, schemes discovery, and civic services.
    """
    clean_query = query.strip()
    if not clean_query:
        return {
            "answer": "Please enter your query or describe the government service or grievance you need help with.",
            "category": "General",
            "metadata": {}
        }

    lower_query = clean_query.lower()

    # 1. Emergency Safety Interception
    emergency_match = _check_emergency(lower_query)
    if emergency_match:
        return emergency_match

    # 2. Check Grievance / Complaint Indicators
    grievance_indicators = [
        "not received", "not arrived", "not credited", "delay", "pending",
        "broken", "damaged", "leak", "overflow", "garbage", "pothole",
        "problem", "issue", "complaint", "report", "fault", "outage",
        "corrupt", "harass", "fraud", "stolen", "unresolved", "grievance",
        "not working", "poor", "dirty", "uncleaned", "dark", "no water"
    ]
    is_grievance_intent = any(indicator in lower_query for indicator in grievance_indicators)

    # If explicit scheme query (e.g. "what is", "eligibility", "how to apply", "scheme", "yojana") and not a complaint
    if not is_grievance_intent:
        scheme_match = _check_schemes(lower_query)
        if scheme_match:
            return scheme_match

        service_match = _check_services(lower_query)
        if service_match:
            return service_match

    # 3. Grievance & Civic Issue Routing using Pre-Trained ML Model
    try:
        routed = routing.route_grievance(clean_query)
        dept = routed["recommended_department"]
        cat = routed["service_category"]
        priority = routed["priority"]
        helpline = routed["recommended_helpline"]
        helpline_name = routed["helpline_name"]
        portal = routed["official_portal"]
        sla = routed["target_response_hours"]
        emergency_flag = routed["emergency_flag"]

        answer_text = (
            f"**Department Recommendation**: {dept}\n\n"
            f"**Service Category**: {cat}\n\n"
            f"**Estimated Priority**: {priority} (Target Response Time: ~{sla} hours)\n\n"
            f"**Recommended Helpline**: `{helpline}` ({helpline_name})\n\n"
            f"**Official Portal**: [Visit Official Portal]({portal})\n\n"
            f"💡 *You can submit this grievance directly through our **Grievances** tab to receive an official tracking ID.*"
        )

        return {
            "answer": answer_text,
            "category": "Grievance Routing",
            "metadata": routed
        }

    except Exception:
        pass

    # 4. Secondary Scheme / Service Fallback Check
    scheme_match = _check_schemes(lower_query)
    if scheme_match:
        return scheme_match

    service_match = _check_services(lower_query)
    if service_match:
        return service_match

    # 5. Default General Help Guidance
    fallback_text = (
        "I can assist you with:\n"
        "1. **Lodge & Route Grievances**: Tell me about civic issues (e.g. road damage, power cuts, sanitation, pension delays).\n"
        "2. **Find Government Schemes**: Inquire about farmer subsidies, housing loans, health cards, or pensions.\n"
        "3. **Public Services Directory**: Ask about Aadhaar updates, birth/death certificates, or consumer complaints.\n"
        "4. **Emergency Helplines**: Access verified 24/7 emergency response contacts."
    )
    return {
        "answer": fallback_text,
        "category": "General Help",
        "metadata": {}
    }


def _check_emergency(query_lower: str) -> Optional[Dict[str, Any]]:
    """Detects urgent emergency keywords and returns verified emergency helplines immediately."""
    emergency_keywords = {
        "police": ("Police Emergency", "112", "Emergency Police Support", "https://www.india.gov.in/"),
        "ambulance": ("Medical Ambulance", "108 / 102", "National Ambulance Service", "https://www.india.gov.in/"),
        "fire": ("Fire & Rescue", "101", "Fire Control Room", "https://www.india.gov.in/"),
        "women safety": ("Women in Distress", "181 / 1091", "Women Helpline", "https://wcd.nic.in/"),
        "women distress": ("Women in Distress", "181 / 1091", "Women Helpline", "https://wcd.nic.in/"),
        "cyber": ("Cyber Crime & Financial Fraud", "1930", "National Cyber Crime Helpline", "https://www.cybercrime.gov.in/"),
        "gas leak": ("LPG Gas Leakage", "1906", "LPG Emergency Helpline", "https://www.mylpg.in/"),
        "cylinder leak": ("LPG Gas Leakage", "1906", "LPG Emergency Helpline", "https://www.mylpg.in/"),
        "child abuse": ("Child Helpline", "1098", "Childline India", "https://www.india.gov.in/"),
        "elder abuse": ("Senior Citizen Helpline", "14567", "Elder Line", "https://socialjustice.gov.in/")
    }

    if "emergency" in query_lower or "urgent" in query_lower or "sos" in query_lower:
        for kw, (service, num, name, url) in emergency_keywords.items():
            if kw in query_lower:
                answer = (
                    f"🚨 **EMERGENCY ASSISTANCE: {service}**\n\n"
                    f"**Emergency Helpline Number**: `{num}` ({name})\n\n"
                    f"**Official Portal**: [Visit Portal]({url})\n\n"
                    f"⚠️ *If you are in immediate physical danger, please dial `{num}` immediately from any phone.*"
                )
                return {
                    "answer": answer,
                    "category": "Emergency",
                    "metadata": {"helpline": num, "service": service, "portal": url}
                }

    return None


def _check_schemes(query_lower: str) -> Optional[Dict[str, Any]]:
    """Checks if the query is asking about government schemes and returns matching results."""
    scheme_triggers = ["scheme", "yojana", "kisan", "pmay", "ayushman", "pension", "scholarship", "subsidy", "mudra", "svanidhi", "cheyutha", "rythu", "pm-jay", "ssy"]
    if any(trigger in query_lower for trigger in scheme_triggers):
        matched = schemes.filter_schemes(search_keyword=query_lower)
        if matched:
            top_schemes = matched[:2]
            scheme_snippets = []
            for s in top_schemes:
                snippet = (
                    f"### 🏛️ {s['scheme_name']}\n"
                    f"- **Description**: {s['description']}\n"
                    f"- **Key Benefits**: {s['benefits']}\n"
                    f"- **Required Documents**: {s['documents']}\n"
                    f"- **Official Website**: [Visit Portal]({s['official_url']})\n"
                )
                scheme_snippets.append(snippet)

            answer = (
                f"Here are matching government schemes:\n\n"
                + "\n---\n".join(scheme_snippets)
                + "\n\n💡 *Explore all schemes under the **Government Schemes** tab for custom eligibility calculation.*"
            )
            return {
                "answer": answer,
                "category": "Government Schemes",
                "metadata": {"schemes_count": len(matched)}
            }

    return None


def _check_services(query_lower: str) -> Optional[Dict[str, Any]]:
    """Checks if the query is asking about standard citizen certificates or utility services."""
    service_triggers = ["aadhaar", "birth certificate", "death certificate", "electricity bill", "water connection", "consumer complaint", "udid", "disability card"]
    for trigger in service_triggers:
        if trigger in query_lower:
            matched = services.filter_services(search_keyword=trigger)
            if matched:
                s = matched[0]
                answer = (
                    f"### 📄 {s['service_name']} ({s['category']})\n"
                    f"**Department**: {s['department']}\n\n"
                    f"**Description**: {s['description']}\n\n"
                    f"**Required Documents**: {s['documents']}\n\n"
                    f"**Helpline**: `{s['helpline']}` | **Official Website**: [Visit Portal]({s['official_url']})\n\n"
                    f"💡 *You can find more services in the **Government Services** directory.*"
                )
                return {
                    "answer": answer,
                    "category": "Government Services",
                    "metadata": s
                }

    return None

