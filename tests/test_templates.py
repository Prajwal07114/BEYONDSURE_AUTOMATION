"""
tests/test_templates.py

Automated tests covering every registered template.

These tests do NOT call the live Groq API (no network dependency, fully
deterministic in CI). Instead they build a fully-populated, schema-valid
CampaignContent fixture per topic and push it through the real renderer
against every template in TEMPLATE_REGISTRY. This exercises exactly the
same Pydantic -> Jinja2 -> HTML path that the API/Streamlit app uses.

Matrix: 23 templates x 5 campaign topics = 115 render checks.

For each render we verify:
  - Template loads (no missing file / registry mismatch)
  - Pydantic validation succeeds
  - Jinja2 rendering succeeds with NO undefined variables (StrictUndefined)
  - The rendered HTML contains: CTA text, footer/brand markers
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import BRAND
from models import (
    CampaignContent, Benefit, Feature, Statistic, MythFact, Step,
    Testimonial, Offer, ChecklistItem, CTA, FAQItem,
)
from template_registry import TEMPLATE_REGISTRY
from renderer import render_email
from evidence import filter_verified_statistics

TOPICS = [
    "Health Insurance for Young Families",
    "Motor Insurance Renewal",
    "Cyber Insurance for Businesses",
    "Cashless OPD Services",
    "Policy Renewal",
]


def build_mock_content(topic: str, category: str) -> CampaignContent:
    """Builds a fully-populated CampaignContent so every template's optional
    sections have something to render, regardless of which fields that
    particular template actually uses."""
    statistics = filter_verified_statistics([
        Statistic(
            value="68%",
            description=f"of customers researched {topic.lower()} online before buying",
            source="Illustrative test fixture (not for production use)",
            source_url=None,
        ),
        Statistic(
            value="10,000+",
            description="network partners nationwide",
            source="Illustrative test fixture (not for production use)",
        ),
        Statistic(
            value="24/7",
            description="claims support availability",
            source="Illustrative test fixture (not for production use)",
        ),
    ])

    return CampaignContent(
        topic=topic,
        category=category,
        campaign_intent="test_intent",
        hero_headline=f"Everything you need to know about {topic}",
        subheadline=f"A smarter way to think about {topic.lower()}.",
        intro=f"{topic} matters more than ever. Here's what BeyondSure offers.",
        benefits=[
            Benefit(title="Comprehensive Cover", description="Broad protection tailored to your needs.", icon_hint="shield"),
            Benefit(title="Fast Claims", description="Streamlined claims processing.", icon_hint="clock"),
            Benefit(title="Transparent Pricing", description="No hidden costs or fine print.", icon_hint="wallet"),
        ],
        features=[
            Feature(name="Cashless Network", description="Wide network of partner service providers."),
            Feature(name="Digital Policy", description="Manage everything from the BeyondSure app."),
        ],
        statistics=statistics,
        problem=f"Many customers are underprepared when it comes to {topic.lower()}.",
        pain_points=[
            "Confusing policy documents",
            "Slow claims processing",
            "Limited provider networks",
        ],
        solution=f"BeyondSure simplifies {topic.lower()} with clear, dependable coverage.",
        steps=[
            Step(step_number=1, title="Check eligibility", description="Answer a few quick questions."),
            Step(step_number=2, title="Compare plans", description="See tailored recommendations."),
            Step(step_number=3, title="Get covered", description="Complete your purchase in minutes."),
        ],
        myths_facts=[
            MythFact(myth="All policies are the same.", fact="Coverage details vary significantly between plans."),
            MythFact(myth="Claims always take weeks.", fact="Many claims are processed within days."),
        ],
        expert_insight="Reviewing your coverage annually helps avoid costly gaps.",
        offer=Offer(
            headline="Special introductory pricing",
            details="Available for a limited period on select plans.",
            terms="Subject to underwriting approval. Standard terms apply.",
            expiry_text="Offer valid for a limited period.",
        ),
        urgency_text="Limited period offer",
        testimonial=Testimonial(quote="The process was simple and the support was excellent.", attribution="Verified Policyholder"),
        checklist=[
            ChecklistItem(label="Keep ID proof handy", detail="Required for verification."),
            ChecklistItem(label="Review existing coverage", detail="Avoid duplicate policies."),
            ChecklistItem(label="Note the renewal date", detail=None),
        ],
        key_takeaway=f"Don't wait -- review your {topic.lower()} coverage today.",
        faq=[
            FAQItem(question=f"Who is {topic} suitable for?", answer="Most individuals and families looking for reliable, transparent coverage."),
            FAQItem(question="How long does approval take?", answer="Typically a few business days, subject to standard checks."),
        ],
        insights=[
            "Reviewing coverage annually helps avoid gaps.",
            "Bundled policies often simplify claims handling.",
        ],
        story=f"A policyholder recently relied on their {topic.lower()} coverage during an unexpected event and found the claims process straightforward.",
        cta=CTA(label="Get Started", url=BRAND["website"]),
        secondary_cta=CTA(label="Talk to an advisor", url=BRAND["website"]),
        disclaimer="Coverage subject to policy terms and conditions.",
    )


@pytest.mark.parametrize("topic", TOPICS)
@pytest.mark.parametrize("template_key", list(TEMPLATE_REGISTRY.keys()))
def test_template_renders_cleanly(template_key, topic):
    meta = TEMPLATE_REGISTRY[template_key]
    content = build_mock_content(topic, meta["type"])

    # Pydantic validation already happened in build_mock_content(); if it
    # didn't raise, validation passed.
    html = render_email(template_key, content)

    assert html and len(html) > 200, "Rendered HTML is unexpectedly short/empty"

    # CTA must appear
    assert content.cta.label in html, "CTA label missing from rendered HTML"

    # Brand must appear (footer / header)
    assert BRAND["name"] in html, "Brand name missing from rendered HTML"

    # Footer / legal elements must appear
    assert "Unsubscribe" in html, "Unsubscribe link missing from footer"
    assert BRAND["irdai_disclaimer"] in html, "Regulatory disclaimer missing from footer"

    # Basic sanity: no leaked Jinja syntax
    assert "{{" not in html and "}}" not in html, "Unrendered Jinja expression leaked into output"
    assert "{%" not in html, "Unrendered Jinja block leaked into output"


def test_all_registered_templates_have_files():
    """Every registry entry must point at a file that actually exists."""
    from config import TEMPLATES_DIR
    for key, meta in TEMPLATE_REGISTRY.items():
        path = os.path.join(TEMPLATES_DIR, meta["file"])
        assert os.path.isfile(path), f"Registered template '{key}' points to missing file: {path}"


def test_at_least_20_templates_registered():
    assert len(TEMPLATE_REGISTRY) >= 20, "Fewer than 20 templates registered."


def test_unsourced_statistics_are_filtered():
    # Pydantic's own validator already rejects an empty source at
    # construction time (see models.Statistic.source_required). We use
    # model_construct() here to bypass that validator and prove that
    # evidence.filter_verified_statistics() is an independent, defense-in-depth
    # check -- not merely relying on the Pydantic validator alone.
    unsourced = Statistic.model_construct(value="99%", description="unsourced claim", source="", source_url=None)
    sourced = Statistic(value="50%", description="sourced claim", source="Test Source")

    stats = filter_verified_statistics([unsourced, sourced])
    assert len(stats) == 1
    assert stats[0].source == "Test Source"


def test_unknown_template_key_raises():
    content = build_mock_content("Test Topic", "promotional")
    with pytest.raises(KeyError):
        render_email("not_a_real_template_key", content)
