"""
Grievance Escalation & Higher Authorities Directory module.
Provides multi-tier escalation management (Local, District, State, Central),
retrieves verified government authority contacts, and manages escalation audit logs.
"""

from typing import List, Dict, Any, Optional, Tuple
import database
import routing


def get_verified_authorities(
    department: str,
    state: str = "All",
    district: str = "All"
) -> List[Dict[str, Any]]:
    """
    Retrieves verified higher authorities for a specific department and region.
    Filters strictly by verified = 1.
    """
    query = """
    SELECT * FROM authorities
    WHERE verified = 1
      AND (department = ? OR department = 'General Government Grievance' OR department = 'CPGRAMS / Concerned Government Authority')
      AND (state = ? OR state = 'All')
      AND (district = ? OR district = 'All')
    ORDER BY 
      CASE level
        WHEN 'Central Authority' THEN 1
        WHEN 'State Authority' THEN 2
        WHEN 'District Authority' THEN 3
        WHEN 'Local Authority' THEN 4
        ELSE 5
      END ASC
    """
    results = database.execute_query(query, (department, state, district))

    # If no specific matches, query general central authorities
    if not results:
        results = database.execute_query(
            "SELECT * FROM authorities WHERE verified = 1 AND level = 'Central Authority'"
        )

    # Validate official URLs
    for auth in results:
        if not routing.is_valid_url(auth.get("official_url")):
            auth["official_url"] = "https://pgportal.gov.in/"

    return results


def escalate_complaint(
    complaint_id: str,
    reason: str,
    escalation_level: str,
    comments: str = "",
    user_id: Optional[int] = None,
    additional_evidence_path: Optional[str] = None
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Submits a grievance escalation to higher authorities, updates complaint status,
    and logs the event in the audit trail.
    """
    clean_id = complaint_id.strip()
    clean_reason = reason.strip()

    if not clean_id:
        return False, "Invalid Complaint ID.", None

    if len(clean_reason) < 5:
        return False, "Please specify a valid reason for escalation (e.g. SLA exceeded, unsatisfactory resolution).", None

    # Fetch complaint
    complaint = routing.get_complaint_details(clean_id)
    if not complaint:
        return False, f"Complaint '{clean_id}' not found.", None

    # Find matching authority
    authorities = get_verified_authorities(
        department=complaint["department"],
        state=complaint["state"],
        district=complaint["district"]
    )

    matched_auth = None
    for auth in authorities:
        if auth["level"].lower() == escalation_level.lower():
            matched_auth = auth
            break

    if not matched_auth and authorities:
        matched_auth = authorities[0]

    if matched_auth:
        authority_name = matched_auth["authority_name"]
        helpline = matched_auth["helpline"]
        official_url = matched_auth["official_url"]
    else:
        authority_name = "Official escalation contact information is not available in the configured directory."
        helpline = "112"
        official_url = "https://pgportal.gov.in/"

    try:
        # Insert escalation record
        database.execute_insert(
            """
            INSERT INTO escalations (
                complaint_id, user_id, reason, additional_evidence_path,
                comments, escalation_level, authority_name, helpline,
                official_url, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Escalated')
            """,
            (
                clean_id,
                user_id,
                clean_reason,
                additional_evidence_path,
                comments.strip(),
                escalation_level,
                authority_name,
                helpline,
                official_url
            )
        )

        # Update complaint table status
        database.execute_update(
            "UPDATE complaints SET status = 'Escalated' WHERE complaint_id = ?",
            (clean_id,)
        )

        # Log status transition in history
        database.execute_insert(
            """
            INSERT INTO complaint_status_history (complaint_id, old_status, new_status, comment, updated_by)
            VALUES (?, ?, 'Escalated', ?, 'Citizen Escalation')
            """,
            (clean_id, complaint["status"], f"Escalated to {escalation_level}: {clean_reason}")
        )

        escalation_record = {
            "complaint_id": clean_id,
            "escalation_level": escalation_level,
            "authority_name": authority_name,
            "helpline": helpline,
            "official_url": official_url,
            "reason": clean_reason
        }

        return True, f"Complaint {clean_id} successfully escalated to {escalation_level}.", escalation_record

    except Exception as e:
        return False, f"Failed to record escalation: {str(e)}", None


def get_user_escalations(user_id: int) -> List[Dict[str, Any]]:
    """Retrieves all escalations submitted by a specific citizen."""
    return database.execute_query(
        "SELECT * FROM escalations WHERE user_id = ? ORDER BY id DESC",
        (user_id,)
    )

