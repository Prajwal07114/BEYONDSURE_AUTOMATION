"""
template_registry.py

The single, authoritative mapping of template key -> (category, file, display_name).

SECURITY: renderer.py must ONLY ever load a template path that comes out of
this registry. User input (e.g. an API `template` field) is used purely as
a *lookup key* into this dict -- it is never concatenated into a filesystem
path. This prevents path traversal / arbitrary file inclusion.
"""

from typing import Dict, Any

TEMPLATE_REGISTRY: Dict[str, Dict[str, Any]] = {
    # ---- Promotional ----
    "product_showcase": {
        "type": "promotional",
        "file": "promotional/product_showcase.html",
        "display_name": "Product Showcase",
        "description": "Hero-led launch layout: intro, three benefits, feature deep-dive, trust bar, CTA.",
    },
    "product_spotlight": {
        "type": "promotional",
        "file": "promotional/product_spotlight.html",
        "display_name": "Product Spotlight",
        "description": "Single-feature spotlight with a large visual band and side-by-side benefit callouts.",
    },
    "limited_offer": {
        "type": "promotional",
        "file": "promotional/limited_offer.html",
        "display_name": "Limited-Time Offer",
        "description": "Badge-led urgency layout: big offer number, countdown-style urgency bar, terms.",
    },
    "benefits_first": {
        "type": "promotional",
        "file": "promotional/benefits_first.html",
        "display_name": "Benefits First",
        "description": "Leads with a benefits grid before any product framing; minimal hero.",
    },
    "feature_focus": {
        "type": "promotional",
        "file": "promotional/feature_focus.html",
        "display_name": "Feature Focus",
        "description": "Single-feature deep-dive with a large numbered feature list and a magazine-style pull quote.",
    },
    "service_explainer": {
        "type": "promotional",
        "file": "promotional/service_explainer.html",
        "display_name": "Service Explainer",
        "description": "Icon-row overview of a service followed by a compact linear explainer sequence.",
    },

    # ---- Lead Generation ----
    "problem_solution": {
        "type": "lead_generation",
        "file": "lead_generation/problem_solution.html",
        "display_name": "Problem \u2192 Solution",
        "description": "Pain-point list, transition statement, solution block, how-it-works, CTA.",
    },
    "quote_generation": {
        "type": "lead_generation",
        "file": "lead_generation/quote_generation.html",
        "display_name": "Quote Generation",
        "description": "Form-like quote request framing with a 3-step quick-quote strip.",
    },
    "consultation": {
        "type": "lead_generation",
        "file": "lead_generation/consultation.html",
        "display_name": "Consultation",
        "description": "Advisor-led, conversational layout inviting a 1:1 consultation booking.",
    },
    "lead_capture": {
        "type": "lead_generation",
        "file": "lead_generation/lead_capture.html",
        "display_name": "Lead Capture",
        "description": "Short, punchy hero with an immediate inline capture band -- no long scroll before the ask.",
    },

    # ---- Awareness ----
    "editorial": {
        "type": "awareness",
        "file": "awareness/editorial.html",
        "display_name": "Editorial Awareness",
        "description": "Magazine-style long-form article layout with a byline strip and pull quote.",
    },
    "myth_vs_fact": {
        "type": "awareness",
        "file": "awareness/myth_vs_fact.html",
        "display_name": "Myth vs Fact",
        "description": "Alternating MYTH/REALITY panels with an expert-insight closing block.",
    },
    "statistics": {
        "type": "awareness",
        "file": "awareness/statistics.html",
        "display_name": "Statistics / Data Story",
        "description": "One giant headline statistic, supporting data cards, interpretation, takeaway.",
    },
    "expert_insight": {
        "type": "awareness",
        "file": "awareness/expert_insight.html",
        "display_name": "Expert Insight",
        "description": "A compilation of standalone numbered insight cards rather than a single narrative.",
    },

    # ---- Educational ----
    "guide": {
        "type": "educational",
        "file": "educational/guide.html",
        "display_name": "Educational Guide",
        "description": "Numbered guide sections with a table-of-contents strip at the top.",
    },
    "how_it_works": {
        "type": "educational",
        "file": "educational/how_it_works.html",
        "display_name": "How It Works",
        "description": "Horizontal step-timeline treatment with connecting rail between steps.",
    },
    "checklist": {
        "type": "educational",
        "file": "educational/checklist.html",
        "display_name": "Checklist Guide",
        "description": "Checkbox-style list layout inside a bordered 'document' card.",
    },
    "faq": {
        "type": "educational",
        "file": "educational/faq.html",
        "display_name": "FAQ / Common Questions",
        "description": "Accordion-styled question/answer stack for addressing common objections.",
    },

    # ---- Campaign ----
    "seasonal": {
        "type": "campaign",
        "file": "campaign/seasonal.html",
        "display_name": "Seasonal Campaign",
        "description": "Full-bleed seasonal banner band with festive framing and benefits row.",
    },
    "urgency": {
        "type": "campaign",
        "file": "campaign/urgency.html",
        "display_name": "Urgency Campaign",
        "description": "High-contrast dark hero, urgency strip, stacked reasons-to-act list.",
    },
    "announcement": {
        "type": "campaign",
        "file": "campaign/announcement.html",
        "display_name": "Product Announcement",
        "description": "Press-release-style centered announcement with a quote block.",
    },
    "new_feature_launch": {
        "type": "campaign",
        "file": "campaign/new_feature_launch.html",
        "display_name": "New Feature Launch",
        "description": "Split hero (headline left, feature list panel right) for launching a specific new capability.",
    },
    "discount_campaign": {
        "type": "campaign",
        "file": "campaign/discount_campaign.html",
        "display_name": "Discount Campaign",
        "description": "Diagonal percentage-badge banner with a bold price/discount focus, distinct from limited_offer's badge+urgency-bar layout.",
    },

    # ---- Customer ----
    "renewal": {
        "type": "customer",
        "file": "customer/renewal.html",
        "display_name": "Renewal Reminder",
        "description": "Policy-card layout resembling a statement, with a renewal action bar.",
    },
    "cross_sell": {
        "type": "customer",
        "file": "customer/cross_sell.html",
        "display_name": "Cross-Sell",
        "description": "\"Because you have X\" framing with a comparison-style add-on card.",
    },
    "upgrade": {
        "type": "customer",
        "file": "customer/upgrade.html",
        "display_name": "Policy Upgrade",
        "description": "Before/after tier comparison layout with an upgrade CTA band.",
    },
    "re_engagement": {
        "type": "customer",
        "file": "customer/re_engagement.html",
        "display_name": "Re-engagement",
        "description": "\"We miss you\" framing: dormant-account narrative with a single, low-friction re-entry CTA.",
    },

    # ---- Corporate ----
    "corporate": {
        "type": "corporate",
        "file": "corporate/corporate.html",
        "display_name": "Corporate",
        "description": "Formal two-column letterhead-style layout for B2B outreach.",
    },
    "employee_benefits": {
        "type": "corporate",
        "file": "corporate/employee_benefits.html",
        "display_name": "Employee Benefits",
        "description": "HR-facing benefits matrix layout with a coverage table.",
    },

    # ---- Premium ----
    "premium_minimal": {
        "type": "premium",
        "file": "premium/premium_minimal.html",
        "display_name": "Premium Minimal",
        "description": "Extreme whitespace, single-column serif-led minimal luxury layout.",
    },
    "luxury_editorial": {
        "type": "premium",
        "file": "premium/luxury_editorial.html",
        "display_name": "Luxury Editorial",
        "description": "Dark-and-gold editorial spread with a full-width feature band.",
    },
    "executive_brief": {
        "type": "premium",
        "file": "premium/executive_brief.html",
        "display_name": "Executive Brief",
        "description": "Dense, memo-style formal layout (numbered clauses) for senior B2B/HR audiences.",
    },
}


def is_valid_template(key: str) -> bool:
    return key in TEMPLATE_REGISTRY


def get_template_meta(key: str) -> Dict[str, Any]:
    if key not in TEMPLATE_REGISTRY:
        raise KeyError(f"Unknown template key: {key}")
    return TEMPLATE_REGISTRY[key]


def list_templates():
    return [
        {"key": k, "category": v["type"], "file": v["file"], "display_name": v["display_name"]}
        for k, v in TEMPLATE_REGISTRY.items()
    ]
