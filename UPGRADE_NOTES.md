# Upgrade Notes: 23-Template Baseline → 32-Template Upgrade

This document records what changed when the existing BeyondSure AI Email
Generator was upgraded to support 30+ genuinely unique templates with
intent-based selection. Nothing here replaces the original architecture --
every change is additive and backward-compatible.

---

## 1. What was inspected before any change was made

- **Architecture**: `app.py` (FastAPI) → `template_selector.py` → `generator.py`
  (Groq) → `models.py` (Pydantic) → `renderer.py` (Jinja2) → HTML. Confirmed
  and preserved exactly.
- **Template selection**: `template_selector.py` used ordered keyword rules
  against topic + audience text, first match wins, with manual override and
  a `product_showcase` default fallback.
- **Groq integration**: `generator.py` calls the Groq chat completions API,
  extracts JSON from the response, retries up to `MAX_LLM_RETRIES` times
  with a tightened prompt on failure, and validates the result against
  `CampaignContent`.
- **Pydantic models**: `models.py` defines `CampaignContent` with mostly
  optional fields, plus sub-models (`Benefit`, `Feature`, `Statistic`,
  `MythFact`, `Step`, `Testimonial`, `Offer`, `ChecklistItem`, `CTA`).
- **Jinja2 rendering**: `renderer.py` resolves template files **only**
  through `template_registry.TEMPLATE_REGISTRY` (never a raw user-supplied
  path), using `StrictUndefined` so any missing variable fails loudly rather
  than rendering blank.
- **FastAPI endpoints**: `POST /generate-email`, `GET /templates`,
  `GET /health` -- all preserved with the exact same request/response
  shapes.
- **Preview system**: `scripts_generate_previews.py` rendered 10
  representative templates into `previews/` using mock data.
- **Existing templates**: 23 templates across 8 categories (promotional,
  lead_generation, awareness, educational, campaign, customer, corporate,
  premium), sharing common header/footer/button Jinja2 macros from
  `templates/_base/macros.html`.
- **Tests**: `tests/test_templates.py` -- 119 tests (23 templates × 5
  topics + registry/evidence checks), all passing before this upgrade began.

Verification command used: `pytest tests/ -q` → 119 passed (baseline).

---

## 2. Files changed (existing files, additive edits only)

| File | Change | Why |
|---|---|---|
| `models.py` | Added `FAQItem` model; added optional `faq`, `insights`, `story` fields to `CampaignContent` | New templates (FAQ, Expert Insight) need structured content the old schema didn't carry. All additions are `Optional`, so existing callers/content that don't set them are unaffected. |
| `prompts.py` | Added `faq`, `insights`, `story` entries to `CONTENT_SCHEMA_HINT` | So the LLM knows it can populate these new optional fields when relevant. No existing hint entries removed or changed. |
| `template_registry.py` | Added 9 new entries (see §3) | Registers the new templates so `renderer.py`'s registry-only lookup can find them. No existing entries modified. |
| `template_selector.py` | Added new keyword rules for the 9 new templates; reordered a couple of urgency/offer rules so `discount_campaign` and `limited_offer` don't collide | Lets intent-based selection route to the new templates. Every original rule is still present and still fires for the same inputs it did before. |
| `tests/test_templates.py` | Extended the mock-content fixture with `faq`, `insights`, `story` values; import `FAQItem` | The existing test loop already parametrizes over `TEMPLATE_REGISTRY.keys()`, so it automatically picked up all 9 new templates once the fixture could populate their fields. |
| `scripts_generate_previews.py` | Extended mock-content fixture the same way (for consistency) | Keeps the original 10-template preview script working without errors if it's re-run. |
| `README.md` | Updated template count/catalog table, testing numbers, preview-regeneration instructions, added upgrade banner | Documentation accuracy. |

**Nothing was deleted. No function signatures changed. No API request/response field was removed or renamed.**

---

## 3. Files added (new)

| File | Purpose |
|---|---|
| `templates/promotional/feature_focus.html` | New template #24 (see catalog) |
| `templates/promotional/service_explainer.html` | New template |
| `templates/lead_generation/lead_capture.html` | New template |
| `templates/awareness/expert_insight.html` | New template |
| `templates/educational/faq.html` | New template |
| `templates/campaign/new_feature_launch.html` | New template |
| `templates/campaign/discount_campaign.html` | New template |
| `templates/customer/re_engagement.html` | New template |
| `templates/premium/executive_brief.html` | New template |
| `generate_gallery.py` | Renders **all 32** templates into `preview-gallery/` + builds `preview-gallery/index.html`, a browsable gallery grid (name, category, purpose, example topic, link to full preview). Separate from and additive to the original `scripts_generate_previews.py`, which still works unchanged. |
| `preview-gallery/` (32 HTML files + `index.html`) | Generated output of the above -- committed so the gallery is viewable without running Python first. |
| `UNIQUENESS_AUDIT.md` | Structural uniqueness audit table across all 32 templates (hero structure, section structure, CTA placement, visual composition). |
| `UPGRADE_NOTES.md` | This file. |

---

## 4. Existing functionality preserved

- **FastAPI app** (`app.py`): identical routes, identical request/response
  models, identical error handling. `GET /templates` now simply returns 32
  entries instead of 23 -- the response *shape* (`TemplateListResponse`) is
  unchanged.
- **Groq integration** (`generator.py`): completely untouched. Same client
  setup, same retry logic, same JSON extraction, same evidence filtering
  call.
- **Pydantic validation** (`models.py`): all original fields, validators,
  and required/optional structure preserved. Only additive optional fields
  were introduced.
- **Jinja2 rendering** (`renderer.py`): untouched. Still resolves paths only
  via `TEMPLATE_REGISTRY`, still uses `StrictUndefined`, still injects the
  same `brand`/`content`/`year` context.
- **Evidence / fact-checking** (`evidence.py`): completely untouched.
  `filter_verified_statistics()` still strips any statistic missing a
  `source` before content is returned, for both old and new templates.
- **Streamlit UI** (`streamlit_app.py`): untouched code-wise. It reads
  `TEMPLATE_REGISTRY` dynamically, so the gallery tab and template dropdown
  automatically show all 32 templates without any code change.
- **Environment variable conventions**: `.env.example` and `config.py`
  unchanged (`GROQ_API_KEY`, `GROQ_MODEL`, `MAX_LLM_RETRIES`, etc.).

---

## 5. How template selection works now

`template_selector.py` is still a deterministic, ordered keyword-rule
engine (no extra LLM call needed for this step -- fast, free, auditable),
now covering all 32 templates. The key behavior the upgrade brief asked
for -- **topic ≠ template** -- was already true in the baseline and remains
true: the same underlying subject can resolve to different templates
depending on phrasing/intent:

```
"Health Insurance"                          → product_showcase   (general promotion)
"Why You Need Health Insurance"             → editorial          (awareness)
"5 Health Insurance Myths"                  → myth_vs_fact       (myth-busting education)
"Renew Your Health Insurance"               → renewal            (customer lifecycle)
"Get a Health Insurance Quote"              → quote_generation   (lead generation)
"Health Insurance Offer Ends Tomorrow"      → urgency            (urgency campaign)
"Health Insurance: Common Questions"        → faq                (objection handling)
"Flat 20% Off Health Insurance"             → discount_campaign  (discount promotion)
"Now With Instant Claim Approval"           → new_feature_launch (feature launch)
"We Miss You -- Reactivate Your Plan"       → re_engagement      (win-back)
```

Manual override (`{"template": "expert_insight"}`) always takes priority
and is validated against `TEMPLATE_REGISTRY` before use.

---

## 6. Total number of unique templates

**32**, up from 23 -- exceeds the 30+ requirement.

## 7. How each template differs

See `UNIQUENESS_AUDIT.md` for the full comparison table across hero
structure, section order, CTA placement, and visual composition for all 32
templates, plus a discussion of the closest "could-have-collapsed" pairs
(e.g. Limited-Time Offer vs Discount Campaign, Guide vs How It Works vs
Service Explainer, Premium Minimal vs Luxury Editorial vs Executive Brief)
and why each pair is structurally distinct.

---

## 8. Verification performed after the upgrade

```
pytest tests/ -q          → 164 passed (32 templates × 5 topics + checks)
uvicorn app:app ...       → boots cleanly; GET /templates returns 32 entries
python generate_gallery.py → renders all 32 templates + index.html without error
```

Visual QA: rendered PNG screenshots of `feature_focus`, `faq`,
`executive_brief`, and `discount_campaign` (the four templates most likely
to resemble an existing one) were inspected side-by-side against their
closest existing counterparts and confirmed structurally distinct, not a
recolor.
