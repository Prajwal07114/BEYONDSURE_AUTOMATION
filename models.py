"""
models.py

Pydantic models for:
- The structured content the LLM is allowed to produce (CampaignContent).
- Sub-structures for statistics/evidence, benefits, steps, myths/facts, etc.
- API request/response schemas.

Design principle: fields are OPTIONAL. A given template only uses the
subset of fields relevant to it. The LLM must never be forced to invent
content for a section a campaign doesn't need.
"""

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, HttpUrl


# ---------------------------------------------------------------------------
# SUB-STRUCTURES
# ---------------------------------------------------------------------------

class Benefit(BaseModel):
    title: str
    description: str
    icon_hint: Optional[str] = Field(
        default=None,
        description="A short semantic hint (e.g. 'shield', 'clock', 'wallet') "
                    "used to pick a pre-approved icon. Never raw SVG/HTML.",
    )


class Feature(BaseModel):
    name: str
    description: str


class Statistic(BaseModel):
    """
    A verified, sourced data point. This is the ONLY way numeric claims may
    enter an email. Unsourced statistics are rejected by evidence.py.
    """
    value: str = Field(..., description="e.g. '68%', '2.3x', '10,000+'")
    description: str
    source: str
    source_url: Optional[str] = None

    @field_validator("source")
    @classmethod
    def source_required(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Every statistic must cite a source.")
        return v.strip()


class MythFact(BaseModel):
    myth: str
    fact: str


class Step(BaseModel):
    step_number: int
    title: str
    description: str


class Testimonial(BaseModel):
    quote: str
    attribution: Optional[str] = Field(
        default=None, description="e.g. 'Verified Policyholder, Pune' -- no fabricated named individuals."
    )


class Offer(BaseModel):
    headline: str
    details: str
    terms: Optional[str] = None
    expiry_text: Optional[str] = Field(
        default=None, description="e.g. 'Offer ends 30th September' -- must not fabricate a false deadline."
    )


class ChecklistItem(BaseModel):
    label: str
    detail: Optional[str] = None


class FAQItem(BaseModel):
    question: str
    answer: str


class CTA(BaseModel):
    label: str
    url: Optional[str] = Field(
        default=None,
        description="If not supplied by the LLM, the renderer substitutes BRAND['website'].",
    )


# ---------------------------------------------------------------------------
# TOP-LEVEL CAMPAIGN CONTENT
# ---------------------------------------------------------------------------

class CampaignContent(BaseModel):
    topic: str
    category: str
    campaign_intent: str = Field(
        default="", description="Short machine-readable intent, e.g. 'drive_quote_requests'."
    )

    # Narrative / hero content
    hero_headline: str
    subheadline: Optional[str] = None
    intro: Optional[str] = None

    # Structured content blocks (all optional -- template decides what it uses)
    benefits: Optional[List[Benefit]] = None
    features: Optional[List[Feature]] = None
    statistics: Optional[List[Statistic]] = None
    problem: Optional[str] = None
    pain_points: Optional[List[str]] = None
    solution: Optional[str] = None
    steps: Optional[List[Step]] = None
    myths_facts: Optional[List[MythFact]] = None
    expert_insight: Optional[str] = None
    offer: Optional[Offer] = None
    urgency_text: Optional[str] = None
    testimonial: Optional[Testimonial] = None
    checklist: Optional[List[ChecklistItem]] = None
    key_takeaway: Optional[str] = None
    faq: Optional[List[FAQItem]] = Field(
        default=None, description="Frequently asked questions -- used by the 'faq' template."
    )
    insights: Optional[List[str]] = Field(
        default=None,
        description="A short list of standalone expert-insight statements -- used by the "
                    "'expert_insight' compilation template (distinct from the single "
                    "'expert_insight' field used as a closing line in other templates).",
    )
    story: Optional[str] = Field(
        default=None,
        description="A short narrative/customer-journey paragraph -- used by storytelling-style templates.",
    )

    cta: CTA
    secondary_cta: Optional[CTA] = None
    disclaimer: Optional[str] = Field(
        default=None,
        description="Additional campaign-specific disclaimer text (in ADDITION to the fixed "
                    "IRDAI/legal footer, never a replacement for it).",
    )

    @field_validator("statistics")
    @classmethod
    def statistics_must_be_sourced(cls, v):
        if v is None:
            return v
        for stat in v:
            if not stat.source or not stat.source.strip():
                raise ValueError("Unsourced statistic detected -- rejecting content.")
        return v


# ---------------------------------------------------------------------------
# API SCHEMAS
# ---------------------------------------------------------------------------

class GenerateEmailRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=200)
    template: Optional[str] = Field(
        default=None, description="Optional manual template key from TEMPLATE_REGISTRY."
    )
    target_audience: Optional[str] = Field(default=None, max_length=200)
    campaign_type: Optional[str] = Field(
        default=None, description="Optional manual category override."
    )


class GenerateEmailResponse(BaseModel):
    topic: str
    category: str
    template: str
    content: CampaignContent
    html: str


class TemplateInfo(BaseModel):
    key: str
    category: str
    file: str
    display_name: str


class TemplateListResponse(BaseModel):
    templates: List[TemplateInfo]
