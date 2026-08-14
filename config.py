"""
config.py

Centralized configuration for the BeyondSure AI Email Generator.

This module owns:
- Brand identity (name, colors, legal/contact info) -- NEVER controlled by the LLM.
- Groq / LLM connection settings.
- Application-wide constants.

Nothing in this file should ever be overridden by user input or model output.
The LLM is only ever allowed to produce marketing *copy*; every visual,
structural, and legal detail below is fixed by the application.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# BRAND SYSTEM
# ---------------------------------------------------------------------------
# This is the single source of truth for brand identity. Templates pull from
# this dict via Jinja2 context. The LLM never sees or sets these values.
BRAND = {
    "name": "BeyondSure",
    "tagline": "Insurance Intelligence, Simplified",
    "website": "https://www.beyondsure.example",
    "support_email": "support@beyondsure.example",
    "support_phone": "1800-000-0000",
    "address": "BeyondSure Insurance Services Pvt. Ltd., 4th Floor, Prestige Tech Park, Bengaluru, India",
    "primary_color": "#0B3D91",      # deep insurance blue
    "accent_color": "#00B8A9",       # teal accent
    "secondary_color": "#F5A623",    # warm accent for badges / urgency
    "dark_color": "#0A1F44",
    "text_color": "#1F2937",
    "muted_text_color": "#6B7280",
    "background_color": "#F4F6F9",
    "card_background": "#FFFFFF",
    "success_color": "#1E8E5A",
    "font_family": "'Helvetica Neue', Helvetica, Arial, sans-serif",
    "logo_text": "BeyondSure",
    "unsubscribe_url": "https://www.beyondsure.example/unsubscribe",
    "privacy_url": "https://www.beyondsure.example/privacy",
    "terms_url": "https://www.beyondsure.example/terms",
    "social": {
        "linkedin": "https://www.linkedin.com/company/beyondsure",
        "twitter": "https://twitter.com/beyondsure",
        "instagram": "https://instagram.com/beyondsure",
    },
    "irdai_disclaimer": (
        "Insurance is the subject matter of solicitation. BeyondSure is a licensed "
        "insurance intermediary. Please read the policy wordings carefully before "
        "concluding a sale."
    ),
    "legal_footer": "\u00A9 {year} BeyondSure Insurance Services Pvt. Ltd. All rights reserved.",
}

# ---------------------------------------------------------------------------
# GROQ / LLM CONFIGURATION
# ---------------------------------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_API_BASE = os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1")
MAX_LLM_RETRIES = int(os.getenv("MAX_LLM_RETRIES", "2"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.6"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))

# ---------------------------------------------------------------------------
# APPLICATION CONSTANTS
# ---------------------------------------------------------------------------
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
PREVIEWS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "previews")

# Allowed categories -- used to validate template registry entries and
# to organize the template gallery in the Streamlit UI.
CAMPAIGN_CATEGORIES = [
    "promotional",
    "lead_generation",
    "awareness",
    "educational",
    "campaign",
    "customer",
    "corporate",
    "premium",
]

API_TITLE = "BeyondSure AI Promotional Email Generator"
API_VERSION = "1.0.0"
