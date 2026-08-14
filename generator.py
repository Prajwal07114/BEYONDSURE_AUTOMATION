"""
generator.py

Handles the call to the Groq API to produce structured campaign content,
parses/validates the JSON against the Pydantic CampaignContent model, and
applies evidence filtering (see evidence.py) before returning.

Retries up to MAX_LLM_RETRIES times on invalid JSON / schema failures,
tightening the prompt on retry.
"""

import json
import logging
from typing import Optional

from groq import Groq

from config import GROQ_API_KEY, GROQ_MODEL, MAX_LLM_RETRIES, LLM_TEMPERATURE, LLM_MAX_TOKENS
from models import CampaignContent, CTA
from prompts import SYSTEM_PROMPT, build_user_prompt, CONTENT_SCHEMA_HINT
from evidence import filter_verified_statistics
from config import BRAND

logger = logging.getLogger("beyondsure.generator")

_client: Optional[Groq] = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        if not GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Copy .env.example to .env and provide a key."
            )
        _client = Groq(api_key=GROQ_API_KEY)
    return _client


def _extract_json(raw: str) -> dict:
    """Best-effort extraction of a JSON object from the model's raw text output."""
    raw = raw.strip()
    # Strip accidental markdown fences if the model adds them despite instructions.
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:]
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in model output.")
    return json.loads(raw[start:end + 1])


def _call_groq(system_prompt: str, user_prompt: str) -> str:
    client = _get_client()
    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return completion.choices[0].message.content


def generate_campaign_content(
    topic: str,
    category: str,
    template_key: str,
    target_audience: Optional[str] = None,
    campaign_intent: Optional[str] = None,
) -> CampaignContent:
    """
    Calls the LLM, validates its JSON output against CampaignContent, filters
    out any unsourced statistics, and returns a validated CampaignContent.

    Raises RuntimeError if all retries are exhausted.
    """
    user_prompt = build_user_prompt(
        topic=topic,
        category=category,
        template_key=template_key,
        schema_hint=CONTENT_SCHEMA_HINT,
        target_audience=target_audience,
        campaign_intent=campaign_intent,
    )

    last_error: Optional[Exception] = None
    system_prompt = SYSTEM_PROMPT

    for attempt in range(MAX_LLM_RETRIES + 1):
        try:
            raw = _call_groq(system_prompt, user_prompt)
            data = _extract_json(raw)

            # Application controls these -- never trust the model even if it
            # accidentally included them.
            data["topic"] = topic
            data["category"] = category
            data.setdefault("campaign_intent", campaign_intent or "")

            if "cta" not in data or not data["cta"]:
                data["cta"] = {"label": "Learn More", "url": BRAND["website"]}

            content = CampaignContent.model_validate(data)

            # Hard enforcement: strip any statistic missing a source, even if
            # it somehow passed the Pydantic validator logic.
            content.statistics = filter_verified_statistics(content.statistics)

            return content

        except Exception as exc:  # noqa: BLE001
            last_error = exc
            logger.warning("LLM generation attempt %s failed: %s", attempt + 1, exc)
            # Tighten instructions for the retry.
            system_prompt = (
                SYSTEM_PROMPT
                + "\n\nIMPORTANT: Your previous response was invalid "
                  f"({exc}). Return ONLY a single valid JSON object matching the schema, "
                  "with no markdown fences and no extra text."
            )

    raise RuntimeError(f"LLM content generation failed after {MAX_LLM_RETRIES + 1} attempts: {last_error}")
