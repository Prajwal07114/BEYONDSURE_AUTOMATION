"""
scripts_generate_previews.py

One-off script to populate previews/ with realistic, clearly-labeled mock
data (no live LLM call, no fabricated "real" statistics -- see the
disclaimer baked into each mock statistic's `source` field). Run:

    python scripts_generate_previews.py

This is NOT part of the runtime application; it's a dev/demo utility.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import BRAND, PREVIEWS_DIR
from models import (
    CampaignContent, Benefit, Feature, Statistic, MythFact, Step,
    Testimonial, Offer, ChecklistItem, CTA, FAQItem,
)
from renderer import render_email

MOCK_SOURCE_NOTE = "Mock preview data -- illustrative only, not a verified statistic"

PREVIEW_TARGETS = {
    "product_showcase": ("Cashless OPD Services", "promotional"),
    "limited_offer": ("Motor Insurance Renewal -- Flat 20% Off", "promotional"),
    "myth_vs_fact": ("5 Things Your Health Insurance Doesn't Cover", "awareness"),
    "statistics": ("The State of Health Insurance in India", "awareness"),
    "problem_solution": ("Protect Your Business From Cyber Attacks", "lead_generation"),
    "renewal": ("Your Health Insurance Policy Renewal", "customer"),
    "seasonal": ("New Year, New Coverage", "campaign"),
    "guide": ("Complete Guide to Health Insurance for Young Families", "educational"),
    "premium_minimal": ("Elite Health Cover", "premium"),
    "luxury_editorial": ("An Exclusive Wellness Partnership", "premium"),
}


def build_mock_content(topic: str, category: str) -> CampaignContent:
    return CampaignContent(
        topic=topic,
        category=category,
        campaign_intent="preview_demo",
        hero_headline=topic,
        subheadline="Insurance Intelligence, Simplified.",
        intro=f"Discover how BeyondSure makes {topic.lower()} simple, transparent, and reliable.",
        benefits=[
            Benefit(title="Comprehensive Cover", description="Broad protection tailored to your needs.", icon_hint="shield"),
            Benefit(title="Fast Claims", description="Streamlined claims processing when it matters most.", icon_hint="clock"),
            Benefit(title="Transparent Pricing", description="Clear terms, no hidden costs.", icon_hint="wallet"),
        ],
        features=[
            Feature(name="Cashless Network", description="Wide network of partner hospitals and service providers."),
            Feature(name="Digital Policy Management", description="Manage everything from the BeyondSure app."),
        ],
        statistics=[
            Statistic(value="10,000+", description="partner network locations", source=MOCK_SOURCE_NOTE),
            Statistic(value="24/7", description="claims support availability", source=MOCK_SOURCE_NOTE),
            Statistic(value="4.6/5", description="average customer service rating", source=MOCK_SOURCE_NOTE),
        ],
        problem="Many customers discover coverage gaps only when it's too late to fix them.",
        pain_points=[
            "Confusing policy documents",
            "Slow, opaque claims processing",
            "Limited hospital or repair networks",
        ],
        solution="BeyondSure simplifies coverage with clear terms and a wide service network.",
        steps=[
            Step(step_number=1, title="Check eligibility", description="Answer a few quick questions."),
            Step(step_number=2, title="Compare plans", description="See tailored recommendations."),
            Step(step_number=3, title="Get covered", description="Complete your purchase in minutes."),
        ],
        myths_facts=[
            MythFact(myth="All policies are basically the same.", fact="Coverage terms vary widely between plans -- always read the fine print."),
            MythFact(myth="Claims always take weeks to process.", fact="Many straightforward claims are settled within a few business days."),
            MythFact(myth="Pre-existing conditions are never covered.", fact="Many plans cover pre-existing conditions after a waiting period."),
        ],
        expert_insight="Reviewing your coverage annually is one of the simplest ways to avoid costly gaps.",
        offer=Offer(
            headline="Special pricing this month",
            details="Available on select plans for new and renewing customers.",
            terms="Subject to underwriting approval. Standard policy terms apply.",
            expiry_text="Offer valid for a limited period.",
        ),
        urgency_text="Limited period offer",
        testimonial=Testimonial(
            quote="The process was simple and the support team was genuinely helpful when I needed them.",
            attribution="Verified Policyholder",
        ),
        checklist=[
            ChecklistItem(label="Keep ID proof handy", detail="Required for verification during purchase."),
            ChecklistItem(label="Review your existing coverage", detail="Avoid unnecessary duplicate policies."),
            ChecklistItem(label="Note your renewal date", detail="Set a reminder to avoid a coverage lapse."),
        ],
        key_takeaway="Don't wait for a claim to find out what your policy actually covers.",
        faq=[
            FAQItem(question="Who is this plan suitable for?", answer="Most individuals and families looking for reliable, transparent coverage."),
            FAQItem(question="How long does approval take?", answer="Typically a few business days, subject to standard checks."),
            FAQItem(question="Can I cover pre-existing conditions?", answer="Many plans cover them after a waiting period -- check your plan details."),
        ],
        insights=[
            "Reviewing your coverage annually helps you catch gaps before they become expensive.",
            "Bundling related policies often simplifies claims handling and paperwork.",
            "Comparing network size matters as much as comparing premiums.",
        ],
        story="A policyholder recently relied on their coverage during an unexpected event and found the claims process straightforward and well-supported.",
        cta=CTA(label="Explore Plans", url=BRAND["website"]),
        secondary_cta=CTA(label="Talk to an advisor", url=BRAND["website"]),
        disclaimer="Coverage subject to policy terms, conditions, and underwriting approval.",
    )


def main():
    os.makedirs(PREVIEWS_DIR, exist_ok=True)
    for template_key, (topic, category) in PREVIEW_TARGETS.items():
        content = build_mock_content(topic, category)
        html = render_email(template_key, content)
        out_path = os.path.join(PREVIEWS_DIR, f"{template_key}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
