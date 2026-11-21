"""
AI Grievance Routing, Model Inference & Evidence Management module.
Integrates the pre-trained ML model (TF-IDF + LogisticRegression) with the
grounded grievance dataset to provide department recommendations, verified helplines,
SLA response targets, and secure evidence upload handling.
"""

import os
import uuid
import re
import joblib
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
import database

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "grievance_routing_model.pkl")
DATASET_PATH = os.path.join(BASE_DIR, "data", "smart_citizen_grievance_routing_dataset.csv")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOADS_DIR, exist_ok=True)

# Cache containers
_model = None
_dataset_df = None


def get_model():
    """Loads and caches the pre-trained scikit-learn TF-IDF + LogisticRegression pipeline."""
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at: {MODEL_PATH}")
        _model = joblib.load(MODEL_PATH)
    return _model


def get_dataset() -> pd.DataFrame:
    """Loads and caches the grievance routing dataset."""
    global _dataset_df
    if _dataset_df is None:
        if not os.path.exists(DATASET_PATH):
            raise FileNotFoundError(f"Grievance dataset not found at: {DATASET_PATH}")
        _dataset_df = pd.read_csv(DATASET_PATH)
    return _dataset_df


def is_valid_url(url: Optional[str]) -> bool:
    """Validates that a URL is well-formed with http:// or https://."""
    if not url:
        return False
    return url.startswith("http://") or url.startswith("https://")


def generate_complaint_id() -> str:
    """
    Generates a unique, non-repeating government complaint reference ID.
    Format: GOV-2026-XXXXXX
    """
    year = datetime.now().year
    # Fetch current count to make sequential-style, then append random hex for uniqueness
    count_rows = database.execute_query("SELECT COUNT(*) as count FROM complaints")
    seq_num = (count_rows[0]["count"] if count_rows else 0) + 1
    rand_suffix = uuid.uuid4().hex[:4].upper()
    return f"GOV-{year}-{seq_num:05d}{rand_suffix}"


def save_evidence_file(uploaded_file) -> Tuple[bool, str, Optional[str]]:
    """
    Validates and securely saves an uploaded citizen evidence file.
    Enforces extension whitelist and a 5MB size limit.
    Returns: (success, message, relative_path_or_none)
    """
    if uploaded_file is None:
        return True, "No evidence file uploaded.", None

    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
    MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB

    # Get and validate extension
    original_name = uploaded_file.name
    _, ext = os.path.splitext(original_name)
    ext_lower = ext.lower()

    if ext_lower not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type '{ext}'. Allowed formats: JPG, JPEG, PNG, PDF.", None

    # Check file size
    file_bytes = uploaded_file.getvalue()
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        return False, "File size exceeds the 5MB limit. Please upload a smaller file.", None

    # Generate unguessable safe filename
    safe_filename = f"ev_{uuid.uuid4().hex}{ext_lower}"
    target_filepath = os.path.join(UPLOADS_DIR, safe_filename)

    try:
        with open(target_filepath, "wb") as f:
            f.write(file_bytes)
        relative_path = os.path.join("uploads", safe_filename)
        return True, "Evidence uploaded", relative_path
    except Exception as e:
        return False, f"Failed to save evidence file: {str(e)}", None


def route_grievance(
    complaint_text: str,
    state: str = "All",
    district: str = "All"
) -> Dict[str, Any]:
    """
    Applies the trained ML model to classify the complaint text into a recommended department,
    then retrieves verified metadata (category, helpline, priority, SLA, portal) from the dataset.
    """
    clean_text = complaint_text.strip()
    if not clean_text:
        raise ValueError("Complaint text cannot be empty.")

    # 1. Run Pre-trained ML Pipeline
    model = get_model()
    predicted_dept = model.predict([clean_text])[0]

    # Calculate confidence only when the model can provide it reliably.
    confidence = None
    if hasattr(model, "predict_proba"):
        try:
            probas = model.predict_proba([clean_text])[0]
            confidence = float(max(probas))
        except Exception:
            confidence = None

    # 2. Enrich with Dataset Metadata
    df = get_dataset()

    # Filter cascade: Department + State + District -> Department + State -> Department
    dept_mask = df["recommended_department"].str.lower() == predicted_dept.lower()
    dept_df = df[dept_mask]

    # Avoid fuzzy substring matching, which can select an unrelated department.
    # If there is no exact match, use the generic safe defaults below.

    matched_row = None

    if not dept_df.empty:
        # Try state + district match
        sd_match = dept_df[
            (dept_df["state"].str.lower() == state.lower()) &
            (dept_df["district"].str.lower() == district.lower())
        ]
        if not sd_match.empty:
            matched_row = sd_match.iloc[0]
        else:
            # Try state match
            s_match = dept_df[dept_df["state"].str.lower() == state.lower()]
            if not s_match.empty:
                matched_row = s_match.iloc[0]
            else:
                matched_row = dept_df.iloc[0]

    if matched_row is not None:
        service_cat = str(matched_row["service_category"])
        priority = str(matched_row["priority"])
        helpline = str(matched_row["recommended_helpline"])
        helpline_name = str(matched_row["helpline_name"])
        official_portal = str(matched_row["official_portal"])
        target_response_hours = int(matched_row["target_response_hours"])
        emergency_flag = str(matched_row["emergency_flag"])
    else:
        # Generic safe defaults if unmapped
        service_cat = "General Government Grievance"
        priority = "Medium"
        helpline = "112"
        helpline_name = "Integrated Public Support"
        official_portal = "https://pgportal.gov.in/"
        target_response_hours = 72
        emergency_flag = "No"

    # Validate official portal format
    if not is_valid_url(official_portal):
        official_portal = "https://www.india.gov.in/"

    return {
        "recommended_department": predicted_dept,
        "service_category": service_cat,
        "priority": priority,
        "confidence_score": round(confidence, 3) if confidence is not None else None,
        "state": state,
        "district": district,
        "recommended_helpline": helpline,
        "helpline_name": helpline_name,
        "official_portal": official_portal,
        "target_response_hours": target_response_hours,
        "emergency_flag": emergency_flag
    }


def submit_grievance(
    complaint_text: str,
    state: str,
    district: str,
    location: str = "",
    citizen_name: str = "",
    citizen_mobile: str = "",
    user_id: Optional[int] = None,
    evidence_path: Optional[str] = None
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Routes the grievance using AI, generates a unique Complaint ID,
    and saves the record into the SQLite database.
    """
    clean_text = complaint_text.strip()
    if len(clean_text) < 10:
        return False, "Please provide a detailed complaint description (at least 10 characters).", {}

    if not state or state == "Select State":
        return False, "Please select the state.", {}

    if not district or district == "Select District":
        return False, "Please select the district.", {}

    # Run AI Routing
    routing_info = route_grievance(clean_text, state, district)
    complaint_id = generate_complaint_id()

    # Save to SQLite Database
    try:
        database.execute_insert(
            """
            INSERT INTO complaints (
                complaint_id, user_id, citizen_name, citizen_mobile,
                complaint_text, department, category, priority,
                state, district, location, status, evidence_path,
                helpline, helpline_name, official_portal,
                target_response_hours, emergency_flag
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Submitted', ?, ?, ?, ?, ?, ?)
            """,
            (
                complaint_id,
                user_id,
                citizen_name.strip() if citizen_name else "Citizen",
                citizen_mobile.strip() if citizen_mobile else "N/A",
                clean_text,
                routing_info["recommended_department"],
                routing_info["service_category"],
                routing_info["priority"],
                state,
                district,
                location.strip(),
                evidence_path,
                routing_info["recommended_helpline"],
                routing_info["helpline_name"],
                routing_info["official_portal"],
                routing_info["target_response_hours"],
                routing_info["emergency_flag"]
            )
        )

        # Log initial status history
        database.execute_insert(
            """
            INSERT INTO complaint_status_history (complaint_id, old_status, new_status, comment, updated_by)
            VALUES (?, NULL, 'Submitted', 'Grievance submitted and classified by AI Routing Engine.', 'AI Router')
            """,
            (complaint_id,)
        )

        routing_info["complaint_id"] = complaint_id
        routing_info["status"] = "Submitted"
        routing_info["evidence_path"] = evidence_path

        return True, "Grievance submitted and routed successfully.", routing_info

    except Exception as e:
        return False, f"Database error during submission: {str(e)}", {}


def get_complaint_details(complaint_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves full complaint details and status timeline history."""
    clean_id = complaint_id.strip()
    if not clean_id:
        return None

    rows = database.execute_query(
        "SELECT * FROM complaints WHERE complaint_id = ?",
        (clean_id,)
    )
    if not rows:
        return None

    complaint = rows[0]

    # Fetch status history timeline
    history_rows = database.execute_query(
        "SELECT * FROM complaint_status_history WHERE complaint_id = ? ORDER BY id ASC",
        (clean_id,)
    )

    complaint["status_history"] = history_rows
    return complaint


def get_user_complaints(user_id: int) -> List[Dict[str, Any]]:
    """Retrieves all complaints registered by a specific citizen."""
    return database.execute_query(
        "SELECT * FROM complaints WHERE user_id = ? ORDER BY id DESC",
        (user_id,)
    )

