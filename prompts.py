"""
prompts.py

System and user prompt construction for the Groq LLM call.

The model generates structured campaign content only.
It does not generate HTML, CSS, JavaScript, branding,
legal information, or unsupported statistics.
"""

import json


SYSTEM_PROMPT = """
You are a professional insurance and healthcare marketing
copywriter working for an insurance intermediary called BeyondSure.

You generate ONLY structured JSON campaign content for promotional
emails.

You are one stage in a pipeline:

User topic
    ↓
Template selection
    ↓
Campaign content generation
    ↓
Pydantic validation
    ↓
Fixed HTML template rendering

You have NO control over layout, styling, branding, or HTML.

STRICT RULES:

1. OUTPUT JSON ONLY

Return ONLY one valid JSON object.

Do not return:

- Markdown
- Code fences
- Explanations
- Commentary
- Text before the JSON
- Text after the JSON

2. NEVER GENERATE HTML

Never generate:

- HTML
- CSS
- JavaScript
- Markdown markup

All content inside JSON must be plain text.

3. DO NOT INVENT BRAND INFORMATION

Never invent:

- Company name
- Logo
- Address
- Email address
- Phone number
- Website URL
- Legal information
- Regulatory disclaimer

The application controls all brand information.

4. DO NOT FABRICATE STATISTICS

Never invent:

- Percentages
- Statistics
- Survey results
- Numerical claims
- Market-share figures
- Medical statistics

If a statistic is included, it must have a
real and verifiable source.

If you are not confident that a statistic is real,
DO NOT include it.

Use a qualitative statement instead.

5. DO NOT INVENT DEADLINES

Never invent a specific:

- Expiry date
- Deadline
- Offer date
- Limited-time date

If the campaign requires urgency, use general language
such as "available for a limited period" without creating
a fake date.

6. TESTIMONIALS

Do not create testimonials attributed to real,
identifiable people.

If a testimonial is needed, use a generic attribution
such as:

"Verified Policyholder"

7. MATCH THE CAMPAIGN

The campaign topic and campaign type determine
what the email is about.

The generated content must remain directly relevant
to the requested campaign.

8. CONCISE MARKETING COPY

Write:

- Clear
- Professional
- Persuasive
- Easy-to-understand
- Concise

Avoid:

- Excessive hype
- Excessive exclamation marks
- ALL CAPS
- Unsupported superlatives
- "Best"
- "#1"
- "Guaranteed"

9. HEALTHCARE AND INSURANCE RELEVANCE

Keep the campaign relevant to healthcare or insurance.

Do not introduce unrelated industries,
products, or topics.

10. FIELD LENGTH

Keep individual fields concise.

Headlines:
approximately 12 words or fewer.

Body/description fields:
approximately 40 words or fewer unless
the template specifically requires longer content.

Return ONLY the JSON object.
Nothing else.
"""


def build_user_prompt(
    topic: str,
    category: str,
    template_key: str,
    schema_hint: dict,
    target_audience: str = None,
    campaign_intent: str = None,
) -> str:
    """
    Build the user prompt sent to Groq.
    """

    audience_line = (
        f"Target audience: {target_audience}\n"
        if target_audience
        else ""
    )

    intent_line = (
        f"Campaign intent: {campaign_intent}\n"
        if campaign_intent
        else ""
    )

    return f"""
Generate promotional email campaign content as JSON.

Campaign topic:
{topic}

Campaign type:
{category}

Selected template:
{template_key}

{audience_line}{intent_line}

The application has already selected the email template.

Generate content that fits the selected template.

The topic determines WHAT the campaign is about.

The campaign type determines the PURPOSE and CATEGORY
of the campaign.

The target audience determines WHO the campaign is written for.

Return a JSON object using only the fields relevant to
the campaign and selected template.

Available schema fields:

{json.dumps(schema_hint, indent=2)}

IMPORTANT:

- JSON only.
- No markdown.
- No HTML.
- No CSS.
- No JavaScript.
- No extra commentary.
- Do not invent company information.
- Do not invent legal information.
- Do not invent statistics.
- Do not invent deadlines.
- Keep the content concise.
- Keep the campaign directly relevant to healthcare
  or insurance.
- Match the target audience when provided.
- Match the campaign intent when provided.
- Make the copy appropriate for the selected template.

Return ONLY the JSON object.
"""


CONTENT_SCHEMA_HINT = {
    "hero_headline": "string",
    "subheadline": "string (optional)",
    "intro": "string (optional)",

    "benefits": [
        {
            "title": "string",
            "description": "string",
            "icon_hint": (
                "string (optional, e.g. "
                "shield/clock/wallet)"
            ),
        }
    ],

    "features": [
        {
            "name": "string",
            "description": "string",
        }
    ],

    "statistics": [
        {
            "value": "string",
            "description": "string",
            "source": (
                "string "
                "(REQUIRED if included)"
            ),
            "source_url": "string (optional)",
        }
    ],

    "problem": "string (optional)",

    "pain_points": [
        "string",
        "...",
    ],

    "solution": "string (optional)",

    "steps": [
        {
            "step_number": "int",
            "title": "string",
            "description": "string",
        }
    ],

    "myths_facts": [
        {
            "myth": "string",
            "fact": "string",
        }
    ],

    "expert_insight": "string (optional)",

    "offer": {
        "headline": "string",
        "details": "string",
        "terms": "string (optional)",
        "expiry_text": (
            "string (optional, "
            "general phrasing only)"
        ),
    },

    "urgency_text": "string (optional)",

    "testimonial": {
        "quote": "string",
        "attribution": (
            "string (optional, generic only)"
        ),
    },

    "checklist": [
        {
            "label": "string",
            "detail": "string (optional)",
        }
    ],

    "key_takeaway": "string (optional)",

    "faq": [
        {
            "question": "string",
            "answer": "string",
        }
    ],

    "insights": [
        "string",
        "... (short standalone expert-insight statements)",
    ],

    "story": (
        "string "
        "(optional, short customer-journey narrative)"
    ),

    "cta": {
        "label": "string",
        "url": "string (optional)",
    },

    "secondary_cta": {
        "label": "string",
        "url": "string (optional)",
    },

    "disclaimer": (
        "string "
        "(optional, campaign-specific caveat only)"
    ),
}