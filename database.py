"""
Database management module for Smart Citizen Governance Portal.
Provides SQLite initialization, thread-safe connection handling,
schema migrations, and parameterized query helper functions.
"""

import sqlite3
import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "smart_governance.db")


def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with row factory enabled for dict-like access."""
    conn = sqlite3.connect(DB_PATH, timeout=20.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """Initializes the database tables and seeds verified directories."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        mobile TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        state TEXT NOT NULL,
        district TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        is_mobile_verified INTEGER DEFAULT 0,
        is_admin INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Complaints Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT UNIQUE NOT NULL,
        user_id INTEGER,
        citizen_name TEXT,
        citizen_mobile TEXT,
        complaint_text TEXT NOT NULL,
        department TEXT NOT NULL,
        category TEXT NOT NULL,
        priority TEXT NOT NULL,
        state TEXT NOT NULL,
        district TEXT NOT NULL,
        location TEXT,
        submission_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'Submitted',
        evidence_path TEXT,
        helpline TEXT,
        helpline_name TEXT,
        official_portal TEXT,
        target_response_hours INTEGER DEFAULT 72,
        emergency_flag TEXT DEFAULT 'No',
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
    );
    """)

    # 3. Complaint Status History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaint_status_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT NOT NULL,
        old_status TEXT,
        new_status TEXT NOT NULL,
        comment TEXT,
        updated_by TEXT DEFAULT 'System',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (complaint_id) REFERENCES complaints(complaint_id) ON DELETE CASCADE
    );
    """)

    # 4. Escalations Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS escalations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT NOT NULL,
        user_id INTEGER,
        reason TEXT NOT NULL,
        additional_evidence_path TEXT,
        comments TEXT,
        escalation_level TEXT NOT NULL,
        authority_name TEXT NOT NULL,
        helpline TEXT,
        official_url TEXT,
        status TEXT DEFAULT 'Escalated',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (complaint_id) REFERENCES complaints(complaint_id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
    );
    """)

    # 5. Higher Authorities Directory Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS authorities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        authority_name TEXT NOT NULL,
        department TEXT NOT NULL,
        state TEXT NOT NULL,
        district TEXT DEFAULT 'All',
        level TEXT NOT NULL,
        helpline TEXT,
        official_url TEXT NOT NULL,
        verified INTEGER DEFAULT 1
    );
    """)

    # 6. Government Services Directory Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_name TEXT NOT NULL,
        department TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        documents TEXT NOT NULL,
        helpline TEXT NOT NULL,
        official_url TEXT NOT NULL,
        state TEXT DEFAULT 'All',
        district TEXT DEFAULT 'All'
    );
    """)

    # 7. OTP Log & Cooldown Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS otp_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mobile TEXT NOT NULL,
        purpose TEXT NOT NULL,
        attempts INTEGER DEFAULT 0,
        max_attempts INTEGER DEFAULT 3,
        expires_at TIMESTAMP NOT NULL,
        resend_available_at TIMESTAMP NOT NULL,
        verified INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()

    # Seed default directories and optionally provision a verified admin account.
    _seed_authorities(conn)
    _seed_services(conn)
    _provision_admin_from_env(conn)

    conn.close()


def _provision_admin_from_env(conn: sqlite3.Connection) -> None:
    """Promotes only an existing phone-verified account matching ADMIN_MOBILE."""
    admin_mobile = re.sub(r"[^\\d]", "", os.getenv("ADMIN_MOBILE", ""))
    if len(admin_mobile) != 10:
        return
    conn.execute(
        "UPDATE users SET is_admin = 1, updated_at = CURRENT_TIMESTAMP "
        "WHERE mobile = ? AND is_mobile_verified = 1",
        (admin_mobile,)
    )
    conn.commit()


def _seed_authorities(conn: sqlite3.Connection) -> None:
    """Seeds verified public authorities across Central, State, and District levels."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM authorities")
    if cursor.fetchone()[0] > 0:
        return

    verified_authorities = [
        # Central Authorities
        ("Centralized Public Grievance Redress and Monitoring System (CPGRAMS) - DARPG",
         "CPGRAMS / Concerned Government Authority", "All", "All", "Central Authority",
         "1800-11-4000", "https://pgportal.gov.in/", 1),
        ("Department of Social Welfare & Empowerment - Grievance Cell",
         "Social Welfare / Pension Administration", "All", "All", "Central Authority",
         "1800-11-1960", "https://www.pgportal.gov.in/pension/", 1),
        ("National Consumer Disputes Redressal Commission (NCDRC)",
         "National Consumer Helpline", "All", "All", "Central Authority",
         "1915", "https://consumerhelpline.gov.in/", 1),
        ("Ministry of Home Affairs - Indian Cybercrime Coordination Centre (I4C)",
         "Cyber Crime Police", "All", "All", "Central Authority",
         "1930", "https://www.cybercrime.gov.in/", 1),
        ("Unique Identification Authority of India (UIDAI) - Public Grievance Office",
         "UIDAI", "All", "All", "Central Authority",
         "1947", "https://uidai.gov.in/", 1),
        ("National Commission for Women (NCW) - Redressal Cell",
         "Women Helpline / Police Support", "All", "All", "Central Authority",
         "7827170170", "https://ncw.nic.in/", 1),
        ("Ministry of Power - Central Electricity Regulatory Commission",
         "Electricity Distribution Utility", "All", "All", "Central Authority",
         "112", "https://cercind.gov.in/", 1),
        ("Ministry of Road Transport and Highways (MoRTH)",
         "Roads / Municipal or Rural Roads Authority", "All", "All", "Central Authority",
         "1033", "https://morth.nic.in/", 1),

        # State Authorities - Andhra Pradesh
        ("Andhra Pradesh CMO - Spandana Public Grievance Cell",
         "Municipal Sanitation / Local Body", "Andhra Pradesh", "All", "State Authority",
         "1902", "https://www.spandana.ap.gov.in/", 1),
        ("AP State Municipal Administration & Urban Development Directorate",
         "Municipal Electrical / Local Body", "Andhra Pradesh", "All", "State Authority",
         "1902", "https://www.spandana.ap.gov.in/", 1),
        ("AP Water Resources & Rural Water Supply Department",
         "Water Supply / Local Urban or Rural Body", "Andhra Pradesh", "All", "State Authority",
         "1902", "https://www.spandana.ap.gov.in/", 1),
        ("AP Eastern / Southern Power Distribution Corporation (APEPDCL/APSPDCL)",
         "Electricity Distribution Utility", "Andhra Pradesh", "All", "State Authority",
         "1912", "https://www.apeasternpower.com/", 1),

        # State Authorities - Telangana
        ("Telangana Prajavani Public Grievance Redressal",
         "CPGRAMS / Concerned Government Authority", "Telangana", "All", "State Authority",
         "1800-425-1110", "https://prajavani.telangana.gov.in/", 1),
        ("Greater Hyderabad Municipal Corporation (GHMC) Commissionerate",
         "Municipal Sanitation / Local Body", "Telangana", "Hyderabad", "District Authority",
         "040-21111111", "https://www.ghmc.gov.in/", 1),

        # State Authorities - Karnataka
        ("Karnataka Janaspandana Grievance Redressal Cell",
         "CPGRAMS / Concerned Government Authority", "Karnataka", "All", "State Authority",
         "1904", "https://ipgrs.karnataka.gov.in/", 1),
        ("Bruhat Bengaluru Mahanagara Palike (BBMP) Central Control",
         "Municipal Sanitation / Local Body", "Karnataka", "Bengaluru", "District Authority",
         "080-22660000", "https://bbmp.gov.in/", 1),

        # State Authorities - Tamil Nadu
        ("Tamil Nadu CM's Special Cell - Mudhalvarin Mugavari",
         "CPGRAMS / Concerned Government Authority", "Tamil Nadu", "All", "State Authority",
         "1100", "https://cmhelpline.tnega.org/", 1),
        ("Greater Chennai Corporation Grievance Division",
         "Municipal Sanitation / Local Body", "Tamil Nadu", "Chennai", "District Authority",
         "1913", "https://chennaicorporation.gov.in/", 1),

        # Local & District Level Authorities
        ("District Collectorate & Grievance Redressal Officer",
         "General Government Grievance", "All", "All", "District Authority",
         "112", "https://www.india.gov.in/", 1),
        ("Municipal Commissioner / Zonal Officer",
         "Municipal Sanitation / Local Body", "All", "All", "Local Authority",
         "112", "https://www.india.gov.in/", 1)
    ]

    cursor.executemany("""
    INSERT INTO authorities (authority_name, department, state, district, level, helpline, official_url, verified)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, verified_authorities)
    conn.commit()


def _seed_services(conn: sqlite3.Connection) -> None:
    """Seeds verified public government services directory across essential citizen categories."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM services")
    if cursor.fetchone()[0] > 0:
        return

    services_data = [
        ("Aadhaar Enrolment & Update", "UIDAI", "Aadhaar",
         "Enrol for new Aadhaar card, update biometric and demographic details (address, name, phone).",
         "Proof of Identity (PoI), Proof of Address (PoA), Proof of Date of Birth (DoB)",
         "1947", "https://uidai.gov.in/", "All", "All"),

        ("National Pension Grievance & CPENGRAMS Redressal", "Social Welfare / Pension Administration", "Pension",
         "Lodge and track grievances regarding Central/State civil pensions, EPFO, and family pensions.",
         "PPO Number, Pensioner Bank Account Number, Sanction Order copy",
         "1800-11-1960", "https://www.pgportal.gov.in/pension/", "All", "All"),

        ("Registration of Births and Issuance of Certificate", "Birth & Death Registration Authority", "Birth Certificate",
         "Register births occurring at home or hospital, and obtain official digital birth certificates with QR code.",
         "Hospital Discharge Certificate, Parents' ID Proofs (Aadhaar), Marriage Certificate",
         "1902", "https://crsorgi.gov.in/", "All", "All"),

        ("Registration of Deaths and Issuance of Certificate", "Birth & Death Registration Authority", "Death Certificate",
         "Register deaths and download authenticated municipal death certificates for legal and estate settlement.",
         "Medical Certificate of Cause of Death, Deceased ID Proof, Applicant's ID Proof",
         "1902", "https://crsorgi.gov.in/", "All", "All"),

        ("Electricity Supply Fault & Billing Redressal", "Electricity Distribution Utility", "Electricity",
         "Report power outages, transformer breakdown, irregular meter reading, and erroneous billing.",
         "Consumer Service Number (SC No.), Electricity Bill Copy, Address Proof",
         "1912", "https://pgportal.gov.in/", "All", "All"),

        ("Public Water Supply & Pipeline Maintenance", "Water Supply / Local Urban or Rural Body", "Water",
         "Report pipe bursts, water contamination, non-delivery of tanker water, and low water pressure.",
         "Water Connection Assessment Number, Location Landmark",
         "1902", "https://www.india.gov.in/", "All", "All"),

        ("Road Repair, Pothole & Highway Hazard Reporting", "Roads / Municipal or Rural Roads Authority", "Roads",
         "Report damaged roads, open ditches, unpaved surfaces, and road accident hazards.",
         "Road Name / GPS Location Coordinates, Photographic Evidence",
         "1073", "https://morth.nic.in/", "All", "All"),

        ("Municipal Solid Waste Management & Sanitation", "Municipal Sanitation / Local Body", "Sanitation",
         "Request garbage clearance, drain unblocking, dead animal removal, and public toilet cleaning.",
         "Ward Number / Street Address, Description of Sanitation Issue",
         "1902", "https://swachhbharatmission.ddws.gov.in/", "All", "All"),

        ("National Consumer Complaint Registration", "National Consumer Helpline", "Consumer Services",
         "Register complaints against defective products, unfair trade practices, e-commerce fraud, and deficient services.",
         "Purchase Invoice, Order ID, Communication with Seller/Service Provider",
         "1915", "https://consumerhelpline.gov.in/", "All", "All"),

        ("Women Helpline & Crisis Intervention (181)", "Women Helpline / Police Support", "Women Support",
         "24/7 emergency response, legal aid, psycho-social counseling, and shelter support for women in distress.",
         "Personal Details (or anonymous distress reporting), Incident Location",
         "181", "https://wcd.nic.in/", "All", "All"),

        ("National Helpline for Senior Citizens (Elder Line)", "Senior Citizens Helpline / Support Services", "Senior Citizen Services",
         "Free support for senior citizens facing neglect, abuse, pension issues, healthcare guidance, and emotional support.",
         "Age Proof / Senior Citizen ID (optional for emergency reporting)",
         "14567", "https://socialjustice.gov.in/", "All", "All"),

        ("Unique Disability ID (UDID) & Support Services", "Disability Support Services", "Disability Services",
         "Apply for nationwide UDID card to avail government concessions, scholarships, aids, and appliances.",
         "Medical Disability Certificate from authorized medical board, Identity Proof, Photo",
         "14456", "https://www.swavlambancard.gov.in/", "All", "All"),

        ("National Cyber Crime Reporting Portal", "Cyber Crime Police", "Cyber Crime",
         "Report financial cyber fraud, social media harassment, hacking, cyberbullying, and identity theft.",
         "Transaction ID, Bank Account Statement, Screenshot of Fraudulent Messages/Links",
         "1930", "https://www.cybercrime.gov.in/", "All", "All"),

        ("Emergency LPG Leakage & Safety Support", "LPG Emergency Support", "LPG",
         "Emergency response for cooking gas cylinder leaks, regulator faults, and delivery malpractice.",
         "LPG Consumer Number, Distributor Agency Name, Registered Mobile Number",
         "1906", "https://www.mylpg.in/", "All", "All")
    ]

    cursor.executemany("""
    INSERT INTO services (service_name, department, category, description, documents, helpline, official_url, state, district)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, services_data)
    conn.commit()


# Safe Helper Execution Functions
def execute_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Executes a SELECT query safely with parameters and returns a list of dictionaries."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def execute_insert(query: str, params: tuple = ()) -> int:
    """Executes an INSERT query safely with parameters and returns the last row ID."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def execute_update(query: str, params: tuple = ()) -> int:
    """Executes an UPDATE/DELETE query safely with parameters and returns the rowcount."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()

