"""
Government Schemes Discovery & Eligibility Recommendation Module.
Provides multi-criteria search and eligibility evaluation for Central and State government welfare schemes.
Grounds all portal links in official verified government domains (e.g., pmkisan.gov.in, pmjay.gov.in).
"""

import os
import re
from typing import List, Dict, Any, Optional

# Verified Government Schemes Catalog
VERIFIED_SCHEMES_CATALOG: List[Dict[str, Any]] = [
    {
        "scheme_name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        "description": "Direct financial assistance of ₹6,000 per year in 3 equal installments to all landholding farmer families.",
        "state": "All",
        "min_age": 18,
        "max_age": 100,
        "gender": "All",
        "occupation": "Farmer",
        "income_limit": 0,
        "category": "All",
        "disability": "All",
        "farmer": "Yes",
        "benefits": "₹6,000 annually credited directly to bank account via DBT in three 4-monthly installments.",
        "documents": "Aadhaar Card, Landholding Ownership Records (Khata/Khatoni), Bank Passbook with Aadhaar seeding.",
        "official_url": "https://pmkisan.gov.in/"
    },
    {
        "scheme_name": "Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana (PM-JAY)",
        "description": "World's largest health assurance scheme providing health cover of ₹5 Lakhs per family per year for secondary and tertiary care hospitalization.",
        "state": "All",
        "min_age": 0,
        "max_age": 100,
        "gender": "All",
        "occupation": "All",
        "income_limit": 250000,
        "category": "All",
        "disability": "All",
        "farmer": "All",
        "benefits": "Cashless and paperless access to healthcare services up to ₹5,00,000 per family per year across empaneled hospitals.",
        "documents": "Aadhaar Card, Ration Card / SECC 2011 proof, Family ID.",
        "official_url": "https://pmjay.gov.in/"
    },
    {
        "scheme_name": "Pradhan Mantri Awas Yojana - Gramin / Urban (PMAY)",
        "description": "Financial assistance to eligible rural and urban homeless families for construction of pucca houses with basic amenities.",
        "state": "All",
        "min_age": 18,
        "max_age": 100,
        "gender": "All",
        "occupation": "All",
        "income_limit": 300000,
        "category": "All",
        "disability": "All",
        "farmer": "All",
        "benefits": "Financial subsidy of ₹1.20 Lakhs in plains and ₹1.30 Lakhs in hilly states + toilet assistance under SBM.",
        "documents": "Aadhaar Card, Bank Account Details, Land/Homeless declaration, Income Certificate.",
        "official_url": "https://pmaymis.gov.in/"
    },
    {
        "scheme_name": "Sukanya Samriddhi Yojana (SSY)",
        "description": "Small deposit savings scheme targeted for the parents of a girl child to build a fund for her higher education and marriage.",
        "state": "All",
        "min_age": 0,
        "max_age": 10,
        "gender": "Female",
        "occupation": "All",
        "income_limit": 0,
        "category": "All",
        "disability": "All",
        "farmer": "All",
        "benefits": "High compound interest rate (8.2%+ p.a.), tax exemption under Section 80C, maturity on girl reaching 21 years.",
        "documents": "Girl Child Birth Certificate, Parents' Aadhaar & PAN Card, Address Proof.",
        "official_url": "https://www.india.gov.in/"
    },
    {
        "scheme_name": "National Social Assistance Programme - Indira Gandhi National Old Age Pension (IGNOAPS)",
        "description": "Monthly pension support to elderly citizens living Below Poverty Line (BPL).",
        "state": "All",
        "min_age": 60,
        "max_age": 100,
        "gender": "All",
        "occupation": "All",
        "income_limit": 100000,
        "category": "All",
        "disability": "All",
        "farmer": "All",
        "benefits": "Monthly pension assistance of ₹500 to ₹1,000 (Central + State contribution) credited via DBT.",
        "documents": "Age Proof (Aadhaar / Voter ID), BPL Card / Income Certificate, Bank Account Passbook.",
        "official_url": "https://nsap.nic.in/"
    },
    {
        "scheme_name": "PM Street Vendor's AtmaNirbhar Nidhi (PM SVANidhi)",
        "description": "Collateral-free working capital micro-loans to street vendors to resume their livelihoods.",
        "state": "All",
        "min_age": 18,
        "max_age": 75,
        "gender": "All",
        "occupation": "Self-Employed / Vendor",
        "income_limit": 0,
        "category": "All",
        "disability": "All",
        "farmer": "No",
        "benefits": "Initial working capital loan of ₹10,000 with 7% interest subsidy; scalable up to ₹20,000 and ₹50,000 on timely repayment.",
        "documents": "Aadhaar Card, Vending Certificate / Letter of Recommendation from Urban Local Body, Bank Account.",
        "official_url": "https://pmsvanidhi.mohua.gov.in/"
    },
    {
        "scheme_name": "Pradhan Mantri Mudra Yojana (PMMY)",
        "description": "Collateral-free loans up to ₹10 Lakhs to non-corporate, non-farm micro/small enterprises under Shishu, Kishore, and Tarun categories.",
        "state": "All",
        "min_age": 18,
        "max_age": 65,
        "gender": "All",
        "occupation": "Business / Entrepreneur",
        "income_limit": 0,
        "category": "All",
        "disability": "All",
        "farmer": "All",
        "benefits": "Loans up to ₹50,000 (Shishu), ₹5 Lakhs (Kishore), and ₹10 Lakhs (Tarun) without collateral.",
        "documents": "Business Identity/Address Proof, Aadhaar, PAN Card, Project Quotation/Proposal, Bank Statement.",
        "official_url": "https://www.mudra.org.in/"
    },
    {
        "scheme_name": "PM Vishwakarma Scheme",
        "description": "End-to-end holistic support to traditional artisans and craftspeople working with hands and tools.",
        "state": "All",
        "min_age": 18,
        "max_age": 70,
        "gender": "All",
        "occupation": "Artisan / Craftsman",
        "income_limit": 0,
        "category": "All",
        "disability": "All",
        "farmer": "All",
        "benefits": "Recognition via Vishwakarma Certificate & ID, skill training with ₹500/day stipend, ₹15,000 toolkit incentive, and collateral-free credit up to ₹3 Lakhs at 5% interest.",
        "documents": "Aadhaar Card, Mobile Number, Bank Account Details, Ration Card.",
        "official_url": "https://pmvishwakarma.gov.in/"
    },
    {
        "scheme_name": "National Disability Pension Scheme (IGNDPS)",
        "description": "Monthly financial pension to severely disabled citizens living Below Poverty Line.",
        "state": "All",
        "min_age": 18,
        "max_age": 79,
        "gender": "All",
        "occupation": "All",
        "income_limit": 120000,
        "category": "All",
        "disability": "Yes",
        "farmer": "All",
        "benefits": "Monthly financial pension assistance transferred directly to the beneficiary bank account.",
        "documents": "Disability Certificate (minimum 80% or severe disability) / UDID Card, BPL Card, Aadhaar, Bank Details.",
        "official_url": "https://nsap.nic.in/"
    },
    {
        "scheme_name": "Andhra Pradesh YSR Cheyutha",
        "description": "Financial empowerment scheme for women aged 45-60 from SC, ST, BC, and Minority communities to establish sustainable micro-enterprises.",
        "state": "Andhra Pradesh",
        "min_age": 45,
        "max_age": 60,
        "gender": "Female",
        "occupation": "All",
        "income_limit": 144000,
        "category": "SC / ST / BC / Minority",
        "disability": "All",
        "farmer": "All",
        "benefits": "Financial assistance of ₹75,000 over 4 years (₹18,750 per year) for economic independence.",
        "documents": "Aadhaar Card, Community/Caste Certificate, Income Certificate, Age Proof, Bank Passbook.",
        "official_url": "https://navasakam.ap.gov.in/"
    },
    {
        "scheme_name": "Telangana Rythu Bandhu / Rythu Bharosa",
        "description": "Investment support scheme for agriculture and horticulture crops to empower Telangana farmers.",
        "state": "Telangana",
        "min_age": 18,
        "max_age": 100,
        "gender": "All",
        "occupation": "Farmer",
        "income_limit": 0,
        "category": "All",
        "disability": "All",
        "farmer": "Yes",
        "benefits": "Financial assistance of ₹10,000 per acre per year (₹5,000 per season) for seeds, fertilizers, and farm labor.",
        "documents": "Pattadar Passbook / Dharani RoR 1B, Aadhaar Card, Bank Account Details.",
        "official_url": "https://rythubandhu.telangana.gov.in/"
    }
]

STOPWORDS = {"tell", "me", "about", "the", "a", "an", "is", "for", "in", "to", "what", "are", "how", "give", "show", "details", "scheme", "schemes", "yojana"}


def get_all_schemes() -> List[Dict[str, Any]]:
    """Returns the full list of verified government welfare schemes."""
    return VERIFIED_SCHEMES_CATALOG


def filter_schemes(
    age: Optional[int] = None,
    gender: Optional[str] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    occupation: Optional[str] = None,
    annual_income: Optional[int] = None,
    category: Optional[str] = None,
    disability: Optional[str] = None,
    farmer: Optional[str] = None,
    search_keyword: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Evaluates citizen profile parameters against scheme eligibility criteria.
    Returns matching schemes with rich eligibility details.
    """
    results = []

    # Extract meaningful search tokens
    search_tokens = []
    if search_keyword and search_keyword.strip():
        raw_tokens = re.findall(r"\w+", search_keyword.strip().lower())
        search_tokens = [t for t in raw_tokens if t not in STOPWORDS and len(t) > 2]
        if not search_tokens:
            search_tokens = raw_tokens

    for scheme in VERIFIED_SCHEMES_CATALOG:
        # 1. State check
        if state and state not in ["All", "Select State"] and scheme["state"] not in ["All", state]:
            continue

        # 2. Age check
        if age is not None and age > 0:
            if age < scheme["min_age"] or age > scheme["max_age"]:
                continue

        # 3. Gender check
        if gender and gender not in ["All", "Other"] and scheme["gender"] not in ["All", gender]:
            continue

        # 4. Income check
        if annual_income is not None and annual_income > 0 and scheme["income_limit"] > 0:
            if annual_income > scheme["income_limit"]:
                continue

        # 5. Farmer check
        if farmer and farmer != "All":
            if scheme["farmer"] != "All" and scheme["farmer"] != farmer:
                continue

        # 6. Disability check
        if disability and disability != "All":
            if scheme["disability"] != "All" and scheme["disability"] != disability:
                continue

        # 7. Occupation check
        if occupation and occupation not in ["All", "Any"]:
            if scheme["occupation"] != "All" and scheme["occupation"] != occupation:
                continue

        # 8. Tokenized Keyword search
        if search_tokens:
            text_corpus = f"{scheme['scheme_name']} {scheme['description']} {scheme['benefits']} {scheme['occupation']}".lower()
            # Require all meaningful query terms to match to avoid noisy,
            # unrelated scheme recommendations from a single common keyword.
            if not all(token in text_corpus for token in search_tokens):
                continue

        results.append(scheme)

    return results

