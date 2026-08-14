"""
template_selector.py

Selects one or multiple templates for a campaign.

The recommendation system is deterministic and does NOT call an LLM.
It ranks templates by campaign intent and then applies a diversity filter
so the user receives genuinely different designs.
"""

from typing import List, Tuple, Optional

from template_registry import (
    is_valid_template,
    TEMPLATE_REGISTRY,
)


# ---------------------------------------------------------------------------
# Intent rules
# ---------------------------------------------------------------------------

RULES = [
    # Customer lifecycle
    (["renew", "renewal", "expiring", "expiry", "due for renewal"], "renewal"),
    (["upgrade", "enhance your cover", "increase sum insured", "higher cover"], "upgrade"),
    (["add-on", "cross-sell", "complete your cover", "also consider"], "cross_sell"),
    (["we miss you", "come back", "reactivate", "re-engagement"], "re_engagement"),

    # Offers / urgency
    (["% off", "discount", "flat off", "sale", "% discount"], "discount_campaign"),
    (["limited time", "offer ends", "last chance"], "limited_offer"),
    (["hurry", "few hours left", "closing soon", "final call", "act now"], "urgency"),
    (["festive", "diwali", "new year", "monsoon", "summer", "season"], "seasonal"),

    # Product launch
    (["new feature", "now with", "just added"], "new_feature_launch"),
    (["launch", "announcing", "introducing", "now available", "new product"], "announcement"),

    # Lead generation
    (["sign up now", "claim your spot", "reserve now", "join now"], "lead_capture"),
    (["get a quote", "quote generation", "instant quote", "compare plans"], "quote_generation"),
    (
        ["book a consultation", "talk to an advisor", "free consultation", "speak to expert"],
        "consultation",
    ),
    (
        ["protect your business", "risk of", "without insurance", "what happens if"],
        "problem_solution",
    ),

    # Awareness
    (
        ["myth", "misconception", "doesn't cover", "things you didn't know", "truth about"],
        "myth_vs_fact",
    ),
    (
        ["expert says", "expert insight", "according to experts", "advisor tips"],
        "expert_insight",
    ),
    (
        ["statistics", "data shows", "percent", "study finds", "report reveals"],
        "statistics",
    ),
    (
        ["did you know", "understanding", "explained", "why you need"],
        "editorial",
    ),

    # Educational
    (
        ["faq", "frequently asked", "common questions", "questions answered"],
        "faq",
    ),
    (
        ["how it works", "step by step", "process explained"],
        "how_it_works",
    ),
    (
        ["checklist", "things to check", "before you buy", "documents required"],
        "checklist",
    ),
    (
        ["guide", "everything you need to know", "complete guide"],
        "guide",
    ),

    # Corporate
    (
        ["employee benefit", "group insurance", "corporate policy", "for your workforce", "hr"],
        "employee_benefits",
    ),
    (
        ["for businesses", "b2b", "enterprise", "sme", "corporate"],
        "corporate",
    ),

    # Premium
    (
        ["premium plan", "elite", "exclusive", "luxury", "vip", "platinum"],
        "luxury_editorial",
    ),
    (
        ["executive", "leadership team", "board brief", "cxo"],
        "executive_brief",
    ),

    # Product / general
    (
        ["spotlight", "feature focus", "highlight"],
        "product_spotlight",
    ),
    (
        ["deep dive into", "focus on this feature"],
        "feature_focus",
    ),
    (
        ["how our service works", "service overview", "our process"],
        "service_explainer",
    ),
    (
        ["benefits of", "why choose", "advantages"],
        "benefits_first",
    ),
]


DEFAULT_TEMPLATE = "product_showcase"
DEFAULT_CATEGORY = "promotional"


# ---------------------------------------------------------------------------
# Template diversity metadata
# ---------------------------------------------------------------------------

# Templates are grouped by structural family.
# We deliberately avoid returning multiple templates from the same family
# when better alternatives are available.

DIVERSITY_GROUPS = {
    "hero_product": {
        "product_showcase",
        "product_spotlight",
        "feature_focus",
        "announcement",
        "new_feature_launch",
    },
    "benefits": {
        "benefits_first",
        "employee_benefits",
    },
    "offer": {
        "limited_offer",
        "discount_campaign",
        "urgency",
        "seasonal",
    },
    "editorial": {
        "editorial",
        "luxury_editorial",
        "premium_minimal",
    },
    "data": {
        "statistics",
        "expert_insight",
        "executive_brief",
    },
    "education": {
        "guide",
        "how_it_works",
        "checklist",
        "faq",
        "myth_vs_fact",
    },
    "lead": {
        "lead_capture",
        "quote_generation",
        "consultation",
        "problem_solution",
    },
    "customer": {
        "renewal",
        "upgrade",
        "cross_sell",
        "re_engagement",
    },
    "corporate": {
        "corporate",
        "employee_benefits",
    },
    "service": {
        "service_explainer",
    },
}


def _get_diversity_group(template_key: str) -> str:
    """Return structural family for a template."""

    for group, templates in DIVERSITY_GROUPS.items():
        if template_key in templates:
            return group

    return template_key


def _rank_candidates(
    topic: str,
    campaign_type: Optional[str] = None,
    target_audience: Optional[str] = None,
) -> List[Tuple[str, str, int]]:
    """
    Return candidate templates with relevance scores.
    """

    haystack = f"{topic} {target_audience or ''}".lower()

    scores = {}

    # Score templates based on keyword rules.
    for keywords, template_key in RULES:
        if any(keyword in haystack for keyword in keywords):
            scores[template_key] = scores.get(template_key, 0) + 100

    # Category relevance.
    if campaign_type:
        for key, meta in TEMPLATE_REGISTRY.items():
            if meta["type"] == campaign_type:
                scores[key] = scores.get(key, 0) + 30

    # Topic-specific semantic hints.
    topic_lower = topic.lower()

    if "health" in topic_lower or "insurance" in topic_lower:
        for key in [
            "product_showcase",
            "benefits_first",
            "editorial",
            "statistics",
            "premium_minimal",
            "problem_solution",
            "guide",
        ]:
            scores[key] = scores.get(key, 0) + 15

    if "offer" in topic_lower or "promotion" in topic_lower:
        for key in [
            "limited_offer",
            "discount_campaign",
            "urgency",
            "product_spotlight",
            "benefits_first",
        ]:
            scores[key] = scores.get(key, 0) + 20

    if "how" in topic_lower:
        for key in [
            "how_it_works",
            "guide",
            "checklist",
            "service_explainer",
            "editorial",
        ]:
            scores[key] = scores.get(key, 0) + 20

    if "myth" in topic_lower:
        scores["myth_vs_fact"] = scores.get("myth_vs_fact", 0) + 100
        scores["faq"] = scores.get("faq", 0) + 40
        scores["editorial"] = scores.get("editorial", 0) + 30

    if "business" in topic_lower or "corporate" in topic_lower:
        for key in [
            "corporate",
            "employee_benefits",
            "executive_brief",
            "problem_solution",
            "statistics",
        ]:
            scores[key] = scores.get(key, 0) + 30

    # Ensure every template is available as a fallback.
    for key in TEMPLATE_REGISTRY:
        scores.setdefault(key, 0)

    ranked = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return [
        (key, TEMPLATE_REGISTRY[key]["type"], score)
        for key, score in ranked
    ]


# ---------------------------------------------------------------------------
# Original single-template API
# ---------------------------------------------------------------------------

def select_template(
    topic: str,
    campaign_type: Optional[str] = None,
    target_audience: Optional[str] = None,
    manual_template: Optional[str] = None,
) -> Tuple[str, str]:
    """
    Backward-compatible single-template selector.
    """

    if manual_template:
        if is_valid_template(manual_template):
            meta = TEMPLATE_REGISTRY[manual_template]
            return manual_template, meta["type"]

        raise ValueError(
            f"Unknown template override: {manual_template}"
        )

    candidates = _rank_candidates(
        topic=topic,
        campaign_type=campaign_type,
        target_audience=target_audience,
    )

    if candidates:
        template_key = candidates[0][0]
        return template_key, TEMPLATE_REGISTRY[template_key]["type"]

    return DEFAULT_TEMPLATE, DEFAULT_CATEGORY


# ---------------------------------------------------------------------------
# NEW: Multiple-template selector
# ---------------------------------------------------------------------------

def select_templates(
    topic: str,
    campaign_type: Optional[str] = None,
    target_audience: Optional[str] = None,
    count: int = 5,
    manual_template: Optional[str] = None,
) -> List[Tuple[str, str]]:
    """
    Return multiple relevant and structurally diverse templates.

    The function first ranks templates by relevance, then prevents multiple
    recommendations from the same structural family when possible.

    Returns:
        [
            ("product_showcase", "promotional"),
            ("editorial", "awareness"),
            ...
        ]
    """

    if count < 1:
        raise ValueError("count must be at least 1")

    if manual_template:
        if not is_valid_template(manual_template):
            raise ValueError(
                f"Unknown template override: {manual_template}"
            )

        meta = TEMPLATE_REGISTRY[manual_template]
        return [(manual_template, meta["type"])]

    candidates = _rank_candidates(
        topic=topic,
        campaign_type=campaign_type,
        target_audience=target_audience,
    )

    selected = []
    used_groups = set()

    # First pass: maximize structural diversity.
    for template_key, category, _score in candidates:
        group = _get_diversity_group(template_key)

        if group in used_groups:
            continue

        selected.append((template_key, category))
        used_groups.add(group)

        if len(selected) >= count:
            break

    # Second pass: if we don't have enough, fill remaining slots.
    # This guarantees up to 5 options even when there are limited categories.
    if len(selected) < count:
        selected_keys = {key for key, _ in selected}

        for template_key, category, _score in candidates:
            if template_key in selected_keys:
                continue

            selected.append((template_key, category))

            if len(selected) >= count:
                break

    return selected[:count]
def select_templates(
    topic: str,
    campaign_type: Optional[str] = None,
    target_audience: Optional[str] = None,
    count: int = 5,
    manual_template: Optional[str] = None,
) -> List[Tuple[str, str]]:

    if count < 1:
        raise ValueError("count must be at least 1")

    if manual_template:
        if not is_valid_template(manual_template):
            raise ValueError(
                f"Unknown template override: {manual_template}"
            )

        meta = TEMPLATE_REGISTRY[manual_template]
        return [(manual_template, meta["type"])]

    candidates = _rank_candidates(
        topic=topic,
        campaign_type=campaign_type,
        target_audience=target_audience,
    )

    selected = []
    used_groups = set()

    # First: choose structurally different templates
    for template_key, category, _score in candidates:

        group = _get_diversity_group(template_key)

        if group in used_groups:
            continue

        selected.append(
            (template_key, category)
        )

        used_groups.add(group)

        if len(selected) >= count:
            break

    # Second: fill remaining slots if necessary
    if len(selected) < count:

        selected_keys = {
            key for key, _ in selected
        }

        for template_key, category, _score in candidates:

            if template_key in selected_keys:
                continue

            selected.append(
                (template_key, category)
            )

            if len(selected) >= count:
                break

    return selected[:count]