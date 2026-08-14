"""
prompts.py

System and user prompt construction for the Groq LLM call. The model is
strictly instructed to return content-only JSON matching the CampaignContent
schema -- never HTML/CSS/JS, never brand or legal details, never fabricated
statistics.
"""

import json

SYSTEM_PROMPT = """You are a professional insurance marketing copywriter working for an \
insurance intermediary called BeyondSure. You generate ONLY structured JSON campaign \
content for promotional emails. You are one stage in a pipeline: your JSON output is \
validated by a schema and then inserted into a fixed, pre-built HTML template by the \
application. You have no control over layout, styling, or branding.

STRICT RULES -- violating any of these makes your output unusable:

1. Output ONLY a single valid JSON object. No markdown code fences, no commentary, \
no preamble, no explanation before or after the JSON.
2. NEVER generate HTML, CSS, JavaScript, or any markup of any kind. Plain text only \
inside JSON string values.
3. NEVER invent the company name, logo, address, support email, website URL, phone \
number, or legal/regulatory disclaimer text. These are supplied by the application, \
not you. Do not include them in your JSON at all.
4. NEVER fabricate statistics, percentages, survey results, or numeric claims. If you \
include an item in the "statistics" array, it MUST include a real, verifiable "source" \
string describing where that figure could plausibly come from (e.g. a named report or \
regulator). If you are not confident a statistic is real and verifiable, DO NOT include \
it -- write a qualitative, non-numeric statement instead in the relevant text field.
5. NEVER invent a false urgency or a fake deadline (e.g. a specific expiry date you made \
up). If the campaign has a genuine time-bound offer, phrase urgency generally ("offer \
valid for a limited period") rather than inventing a specific date.
6. Do not fabricate named customer testimonials attributed to real, identifiable \
individuals. If you include a testimonial, attribute it generically (e.g. "Verified \
Policyholder").
7. Match the requested JSON schema exactly. Only include the fields that are relevant \
to this campaign's template category -- leave irrelevant fields out (or null) rather \
than padding them with filler.
8. Write concise, professional, persuasive marketing copy. Avoid excessive hype, \
exclamation marks, ALL CAPS shouting, or unsupported superlative claims ("the best", \
"guaranteed", "#1") that an insurance regulator would flag.
9. Tone should match the target audience and campaign intent provided in the user prompt.
10. Keep individual text fields concise: headlines under ~12 words, body/description \
fields under ~40 words, unless explicitly asked for longer-form (e.g. an educational \
guide section).

Return ONLY the JSON object matching the schema you are given. Nothing else.
"""


def build_user_prompt(
    topic: str,
    category: str,
    template_key: str,
    schema_hint: dict,
    target_audience: str = None,
    campaign_intent: str = None,
) -> str:
    audience_line = f"Target audience: {target_audience}\n" if target_audience else ""
    intent_line = f"Campaign intent: {campaign_intent}\n" if campaign_intent else ""

    return f"""Generate promotional email campaign content as JSON.

Campaign topic: {topic}
Template category: {category}
Template style: {template_key}
{audience_line}{intent_line}
Return a JSON object with (a subset of, as relevant) these fields:
{json.dumps(schema_hint, indent=2)}

Reminders:
- JSON only, no markdown fences, no extra commentary.
- No brand name/logo/address/legal text (the application adds these).
- No fabricated statistics -- omit "statistics" entirely if you have no real, sourceable figure.
- Keep every field's language professional insurance marketing copy.
"""


# A field hint dict shown to the model so it knows the shape of CampaignContent
# without us dumping the full Pydantic JSON schema (which would be noisier
# and include internal validator descriptions).
CONTENT_SCHEMA_HINT = {
    "hero_headline": "string",
    "subheadline": "string (optional)",
    "intro": "string (optional)",
    "benefits": [{"title": "string", "description": "string", "icon_hint": "string (optional, e.g. shield/clock/wallet)"}],
    "features": [{"name": "string", "description": "string"}],
    "statistics": [{"value": "string", "description": "string", "source": "string (REQUIRED if included)", "source_url": "string (optional)"}],
    "problem": "string (optional)",
    "pain_points": ["string", "..."],
    "solution": "string (optional)",
    "steps": [{"step_number": "int", "title": "string", "description": "string"}],
    "myths_facts": [{"myth": "string", "fact": "string"}],
    "expert_insight": "string (optional)",
    "offer": {"headline": "string", "details": "string", "terms": "string (optional)", "expiry_text": "string (optional, general phrasing only)"},
    "urgency_text": "string (optional)",
    "testimonial": {"quote": "string", "attribution": "string (optional, generic only)"},
    "checklist": [{"label": "string", "detail": "string (optional)"}],
    "key_takeaway": "string (optional)",
    "faq": [{"question": "string", "answer": "string"}],
    "insights": ["string", "... (short standalone expert-insight statements)"],
    "story": "string (optional, short customer-journey narrative)",
    "cta": {"label": "string", "url": "string (optional)"},
    "secondary_cta": {"label": "string", "url": "string (optional)"},
    "disclaimer": "string (optional, campaign-specific caveat only)",
}
