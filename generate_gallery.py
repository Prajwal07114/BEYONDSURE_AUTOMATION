"""
generate_gallery.py

Upgrades the existing preview system into a full gallery covering EVERY
registered template (32, as of this upgrade). This is additive: the
original `previews/` folder and `scripts_generate_previews.py` (10
representative previews) are untouched -- this script produces a separate,
more complete `preview-gallery/` folder:

    preview-gallery/
        index.html                    <- gallery grid: name, purpose, example topic, link
        01-product_showcase.html      <- actual rendered HTML for each template
        02-product_spotlight.html
        ...

Run:
    python generate_gallery.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import BRAND
from models import (
    CampaignContent, Benefit, Feature, Statistic, MythFact, Step,
    Testimonial, Offer, ChecklistItem, CTA, FAQItem,
)
from template_registry import TEMPLATE_REGISTRY
from renderer import render_email

GALLERY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview-gallery")

MOCK_SOURCE_NOTE = "[Sample Statistic] -- illustrative preview data only, not a verified figure"

# One representative example topic per template, chosen to demonstrate the
# intent-based selection this template is meant to serve (see README /
# UPGRADE_NOTES for the full topic -> intent -> template mapping).
EXAMPLE_TOPICS = {
    "product_showcase": ("Cashless OPD Services", "General product promotion"),
    "product_spotlight": ("Introducing SmartHealth Cover", "Single-feature spotlight"),
    "feature_focus": ("Deep Dive: Instant Claim Approval", "Feature deep-dive"),
    "service_explainer": ("How Our Claims Service Works", "Service overview"),
    "limited_offer": ("Motor Insurance Offer Ends Tomorrow", "Limited-time promotion"),
    "discount_campaign": ("Flat 20% Off Motor Insurance", "Discount-led promotion"),
    "benefits_first": ("Why Choose BeyondSure Health Cover", "Benefits-led promotion"),

    "problem_solution": ("Protect Your Business From Cyber Attacks", "Problem-aware lead gen"),
    "quote_generation": ("Get a Health Insurance Quote", "Lead generation"),
    "consultation": ("Talk to a BeyondSure Advisor", "Consultation booking"),
    "lead_capture": ("Sign Up for Instant Coverage", "Fast lead capture"),

    "editorial": ("Why You Need Health Insurance", "Awareness / editorial"),
    "myth_vs_fact": ("5 Health Insurance Myths", "Myth-busting education"),
    "statistics": ("The State of Health Insurance in India", "Data-led awareness"),
    "expert_insight": ("What Advisors Wish You Knew", "Expert insight compilation"),

    "guide": ("Complete Guide to Family Health Insurance", "Educational guide"),
    "how_it_works": ("How Cashless OPD Works", "Process education"),
    "checklist": ("Documents Required Before You Buy", "Checklist education"),
    "faq": ("Health Insurance: Common Questions", "FAQ / objection handling"),

    "seasonal": ("New Year, New Coverage", "Seasonal campaign"),
    "urgency": ("Cyber Insurance Offer Ends Sunday", "Urgency campaign"),
    "announcement": ("Introducing BeyondSure Cyber Shield", "Product announcement"),
    "new_feature_launch": ("Now With Instant Claim Approval", "New feature launch"),

    "renewal": ("Renew Your Health Insurance", "Renewal reminder"),
    "cross_sell": ("Complete Your Cover With Cyber Insurance", "Cross-sell"),
    "upgrade": ("Upgrade Your Motor Insurance", "Policy upgrade"),
    "re_engagement": ("We Miss You -- Reactivate Your Plan", "Re-engagement"),

    "corporate": ("Cyber Protection for Your Business", "B2B corporate outreach"),
    "employee_benefits": ("Group Health Insurance for Your Workforce", "HR / employee benefits"),

    "premium_minimal": ("Elite Health Cover", "Premium minimal"),
    "luxury_editorial": ("An Exclusive Wellness Partnership", "Luxury editorial"),
    "executive_brief": ("Cyber Risk Briefing for Leadership", "Executive brief"),
}


def build_mock_content(topic: str, category: str) -> CampaignContent:
    return CampaignContent(
        topic=topic,
        category=category,
        campaign_intent="gallery_preview",
        hero_headline=topic,
        subheadline="Insurance Intelligence, Simplified.",
        intro=f"Discover how BeyondSure makes {topic.lower()} simple, transparent, and reliable.",
        benefits=[
            Benefit(title="Comprehensive Cover", description="Broad protection tailored to your needs.", icon_hint="shield"),
            Benefit(title="Fast Claims", description="Streamlined claims processing when it matters most.", icon_hint="clock"),
            Benefit(title="Transparent Pricing", description="Clear terms, no hidden costs.", icon_hint="wallet"),
            Benefit(title="Wide Network", description="Extensive partner network nationwide.", icon_hint="map"),
        ],
        features=[
            Feature(name="Cashless Network", description="Wide network of partner hospitals and service providers."),
            Feature(name="Digital Policy Management", description="Manage everything from the BeyondSure app."),
            Feature(name="Instant Claim Tracking", description="Real-time status updates from submission to settlement."),
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
            Step(step_number=4, title="Manage your policy", description="Everything in one place, anytime."),
        ],
        myths_facts=[
            MythFact(myth="All policies are basically the same.", fact="Coverage terms vary widely -- always read the fine print."),
            MythFact(myth="Claims always take weeks.", fact="Many straightforward claims settle within a few business days."),
            MythFact(myth="Pre-existing conditions are never covered.", fact="Many plans cover them after a waiting period."),
        ],
        expert_insight="Reviewing your coverage annually is one of the simplest ways to avoid costly gaps.",
        offer=Offer(
            headline="Special pricing this month",
            details="Available on select plans for new and renewing customers.",
            terms="[Sample Terms] Subject to underwriting approval. Standard policy terms apply.",
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
            FAQItem(question="Can I cover pre-existing conditions?", answer="Many plans cover them after a waiting period."),
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


def build_index_html(entries) -> str:
    cards = []
    for i, (key, meta, topic, purpose) in enumerate(entries, start=1):
        file_name = f"{i:02d}-{key}.html"
        cards.append(f"""
        <a class="card" href="{file_name}" target="_blank">
          <div class="card-category">{meta['type'].replace('_', ' ').title()}</div>
          <div class="card-title">{meta['display_name']}</div>
          <div class="card-purpose">{purpose}</div>
          <div class="card-topic">Example topic: &ldquo;{topic}&rdquo;</div>
          <div class="card-desc">{meta.get('description', '')}</div>
          <div class="card-link">View full preview &rarr;</div>
        </a>""")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>BeyondSure Template Gallery</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body {{ margin:0; padding:0; font-family: 'Helvetica Neue', Arial, sans-serif; background:#F4F6F9; color:#1F2937; }}
  header {{ background:#0A1F44; color:#fff; padding:32px 24px; text-align:center; }}
  header h1 {{ margin:0; font-size:24px; }}
  header p {{ margin:8px 0 0 0; color:#C7CDDB; font-size:14px; }}
  .grid {{ display:grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap:16px; padding:24px; max-width:1200px; margin:0 auto; }}
  .card {{ display:block; background:#fff; border-radius:10px; padding:18px 20px; text-decoration:none; color:inherit; border:1px solid #E5E9F0; transition:box-shadow .15s ease; }}
  .card:hover {{ box-shadow:0 4px 14px rgba(0,0,0,0.08); }}
  .card-category {{ font-size:10px; letter-spacing:1px; text-transform:uppercase; color:#00B8A9; font-weight:700; }}
  .card-title {{ font-size:16px; font-weight:700; margin-top:6px; color:#0B3D91; }}
  .card-purpose {{ font-size:12px; color:#6B7280; margin-top:4px; }}
  .card-topic {{ font-size:11px; color:#1F2937; margin-top:10px; font-style:italic; }}
  .card-desc {{ font-size:12px; color:#6B7280; margin-top:8px; line-height:18px; }}
  .card-link {{ font-size:12px; color:#0B3D91; font-weight:700; margin-top:12px; }}
  .count {{ text-align:center; padding: 8px 24px 0 24px; font-size:13px; color:#6B7280; }}
</style>
</head>
<body>
<header>
  <h1>BeyondSure Template Gallery</h1>
  <p>{len(entries)} structurally unique promotional email templates</p>
</header>
<div class="count">Click any card to open the fully rendered HTML preview in a new tab.</div>
<div class="grid">
{''.join(cards)}
</div>
</body>
</html>
"""


def main():
    os.makedirs(GALLERY_DIR, exist_ok=True)
    entries = []
    for key, meta in TEMPLATE_REGISTRY.items():
        topic, purpose = EXAMPLE_TOPICS.get(key, (f"BeyondSure {meta['display_name']}", meta["display_name"]))
        content = build_mock_content(topic, meta["type"])
        html = render_email(key, content)
        entries.append((key, meta, topic, purpose))
        idx = list(TEMPLATE_REGISTRY.keys()).index(key) + 1
        out_path = os.path.join(GALLERY_DIR, f"{idx:02d}-{key}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Wrote {out_path}")

    index_html = build_index_html(entries)
    index_path = os.path.join(GALLERY_DIR, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_html)
    print(f"Wrote {index_path}")
    print(f"\nGallery complete: {len(entries)} templates.")


if __name__ == "__main__":
    main()
