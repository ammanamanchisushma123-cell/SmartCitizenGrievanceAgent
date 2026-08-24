"""
Government Public Services Directory Module.
Provides verified service discovery across 14 essential civic categories
with required document checklists, direct helplines, and verified official portals.
"""

from typing import List, Dict, Any, Optional
import database
import routing

CATEGORIES = [
    "All Categories",
    "Aadhaar",
    "Pension",
    "Birth Certificate",
    "Death Certificate",
    "Electricity",
    "Water",
    "Roads",
    "Sanitation",
    "Consumer Services",
    "Women Support",
    "Senior Citizen Services",
    "Disability Services",
    "Cyber Crime",
    "LPG"
]


def get_all_services() -> List[Dict[str, Any]]:
    """Retrieves all verified government services from the database."""
    services = database.execute_query("SELECT * FROM services ORDER BY category, service_name ASC")
    for s in services:
        if not routing.is_valid_url(s.get("official_url")):
            s["official_url"] = "https://www.india.gov.in/"
    return services


def filter_services(
    category: Optional[str] = None,
    search_keyword: Optional[str] = None,
    state: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Filters government public services by category, keyword search, and state.
    """
    query = "SELECT * FROM services WHERE 1=1"
    params = []

    if category and category != "All Categories":
        query += " AND category = ?"
        params.append(category)

    if state and state not in ["All", "Select State"]:
        query += " AND (state = ? OR state = 'All')"
        params.append(state)

    if search_keyword and search_keyword.strip():
        kw = f"%{search_keyword.strip()}%"
        query += " AND (service_name LIKE ? OR description LIKE ? OR department LIKE ? OR documents LIKE ?)"
        params.extend([kw, kw, kw, kw])

    query += " ORDER BY category, service_name ASC"

    services = database.execute_query(query, tuple(params))
    for s in services:
        if not routing.is_valid_url(s.get("official_url")):
            s["official_url"] = "https://www.india.gov.in/"

    return services


def get_service_categories() -> List[str]:
    """Returns the list of available government service categories."""
    return CATEGORIES

