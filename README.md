# BeyondSure AI Promotional Email Generator

> **Upgrade note:** This project was upgraded from a 23-template baseline to
> **32 genuinely unique templates** with intent-based (not topic-based)
> template selection. See `UPGRADE_NOTES.md` for a full changelog and
> `UNIQUENESS_AUDIT.md` for the structural uniqueness audit. All existing
> functionality (FastAPI contract, Groq integration, Pydantic validation,
> Jinja2 rendering, evidence/fact-checking) was preserved unchanged.

An AI-powered pipeline that turns a campaign topic (e.g. *"Cashless OPD
Services"*) into a professional, responsive, brand-consistent HTML
promotional email — automatically selecting from **32 structurally unique
templates**, generating content with an LLM (Groq / Llama), validating that
content with Pydantic, and rendering it into a fixed HTML/Jinja2 template
that the LLM never touches directly.

This is a **new, standalone project**. It does not modify, depend on, or
merge with any existing BeyondSure email-generator codebase.

---

## 1. Architecture

```
                    USER
                     │
                     ▼
              Streamlit UI  ──────────────┐
                     │                    │ (or call API directly)
                     ▼                    ▼
                  FastAPI  ◄───────────────
                     │
                     ▼
             Campaign Analyzer / template_selector.py
                     │
                     ▼
              Template Selector  (keyword rules, manual override)
                     │
                     ▼
                Groq / Llama  (generator.py) ── content ONLY, never HTML/CSS
                     │
                     ▼
              Pydantic Validation  (models.py)  ── + evidence.py strips unsourced stats
                     │
                     ▼
             Template Registry  (template_registry.py) ── the ONLY source of template paths
                     │
                     ▼
                  Jinja2  (renderer.py)
                     │
                     ▼
              Final responsive HTML Email
                 /       \
                ▼         ▼
             Preview    Download (.html)
```

### The one non-negotiable architecture rule

**The LLM generates content only** — never HTML, CSS, JavaScript, brand
colors, company info, footer info, or URLs. Those are 100% controlled by
the application (`config.py`'s `BRAND` dict and the Jinja2 templates). The
LLM's output is JSON matching `models.CampaignContent`, nothing else.

```
Correct:    LLM → JSON content → Pydantic → Jinja2 → HTML
Incorrect:  LLM → HTML email
```

---

## 2. Project structure

```
beyondsure-ai-email-generator/
│
├── app.py                    # FastAPI app (POST /generate-email, GET /templates)
├── config.py                 # BRAND system + Groq config (single source of truth)
├── models.py                 # Pydantic schema for LLM content + API request/response
├── generator.py              # Groq API call, JSON extraction, retries, validation
├── renderer.py                # Jinja2 rendering, resolves paths ONLY via the registry
├── template_selector.py      # Deterministic keyword-based template auto-selection
├── template_registry.py      # The single authoritative template_key -> file mapping (32 entries)
├── evidence.py                # Enforces "no fabricated statistics" in code, not just prompt
├── prompts.py                 # System + user prompt construction for Groq
├── streamlit_app.py           # Streamlit UI: generate tab + template gallery tab
├── scripts_generate_previews.py  # Dev utility: regenerates previews/ (10 templates) with mock data
├── generate_gallery.py        # Dev utility: regenerates preview-gallery/ (ALL 32 templates) + index.html
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── UPGRADE_NOTES.md            # Changelog from the 23-template baseline to this 32-template upgrade
├── UNIQUENESS_AUDIT.md         # Structural uniqueness audit table for all 32 templates
│
├── templates/
│   ├── _base/macros.html          # Shared header/footer/button/doctype macros
│   ├── promotional/               # product_showcase, product_spotlight, feature_focus, service_explainer, limited_offer, benefits_first
│   ├── lead_generation/           # problem_solution, quote_generation, consultation, lead_capture
│   ├── awareness/                 # editorial, myth_vs_fact, statistics, expert_insight
│   ├── educational/               # guide, how_it_works, checklist, faq
│   ├── campaign/                  # seasonal, urgency, announcement, new_feature_launch, discount_campaign
│   ├── customer/                  # renewal, cross_sell, upgrade, re_engagement
│   ├── corporate/                 # corporate, employee_benefits
│   └── premium/                   # premium_minimal, luxury_editorial, executive_brief
│
├── previews/                  # 10 pre-generated representative preview emails (original preview system)
├── preview-gallery/            # NEW: full gallery -- all 32 templates + index.html grid
└── tests/
    └── test_templates.py      # 164 automated tests (32 templates × 5 topics + checks)
```

---

## 3. Setup

### Requirements
- Python 3.11
- A Groq API key (free tier available at https://console.groq.com)

### Install

```bash
git clone <this-repo>
cd beyondsure-ai-email-generator
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configure

```bash
cp .env.example .env
# then edit .env and set:
# GROQ_API_KEY=your_key_here
```

`.env` variables:

| Variable | Default | Purpose |
|---|---|---|
| `GROQ_API_KEY` | *(required)* | Your Groq API key |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model used for content generation |
| `MAX_LLM_RETRIES` | `2` | Retries on invalid/unparseable JSON |
| `LLM_TEMPERATURE` | `0.6` | Sampling temperature |
| `LLM_MAX_TOKENS` | `2000` | Max output tokens |

---

## 4. Running the app

### FastAPI (the integration surface for the BeyondSure admin bulk-email system)

```bash
uvicorn app:app --reload --port 8000
```

Docs: `http://localhost:8000/docs`

### Streamlit UI (standalone demo/interactive tool)

```bash
streamlit run streamlit_app.py
```

Streamlit calls the same Python pipeline directly (no HTTP hop needed for
local use); for a fully separated deployment, point it at the FastAPI
`/generate-email` endpoint instead via `requests`.

---

## 5. API reference

### `POST /generate-email`

**Automatic template selection:**
```json
{
  "topic": "Cashless OPD Services"
}
```

**Manual template selection:**
```json
{
  "topic": "Cashless OPD Services",
  "template": "product_showcase"
}
```

**Optional fields:**
```json
{
  "topic": "Cashless OPD Services",
  "target_audience": "Young professionals in metro cities",
  "campaign_type": "promotional"
}
```

**Response:**
```json
{
  "topic": "Cashless OPD Services",
  "category": "promotional",
  "template": "product_showcase",
  "content": { "...": "validated CampaignContent JSON" },
  "html": "<!DOCTYPE html>..."
}
```

### `GET /templates`

Returns every registered template (key, category, file, display name) —
useful for building a picker UI.

### `GET /health`

Liveness check.

### Example integration (curl)

```bash
curl -X POST http://localhost:8000/generate-email \
  -H "Content-Type: application/json" \
  -d '{"topic": "Motor Insurance Renewal"}'
```

---

## 6. Template catalog (32 templates)

| # | Key | Category | Layout idea |
|---|---|---|---|
| 1 | `product_showcase` | Promotional | Hero → 3 benefits → features → trust stats → CTA |
| 2 | `product_spotlight` | Promotional | Radial-gradient spotlight band → side-by-side benefit callouts |
| 3 | `limited_offer` | Promotional | Badge → huge offer → urgency bar → checklist benefits → terms |
| 4 | `benefits_first` | Promotional | 2×2 benefits grid first, product framing second |
| 5 | `feature_focus` | Promotional | Bordered pull-quote → large ghost-numbered feature list → single stat |
| 6 | `service_explainer` | Promotional | 4-up icon row → connected vertical-rail step sequence |
| 7 | `problem_solution` | Lead Generation | Pain points → transition → solution band → mini step timeline |
| 8 | `quote_generation` | Lead Generation | Dashed "quote card" with embedded 3-step strip |
| 9 | `consultation` | Lead Generation | Letter-style serif copy, advisor avatar card |
| 10 | `lead_capture` | Lead Generation | CTA appears immediately after the hero, before any body copy |
| 11 | `editorial` | Awareness | Magazine byline strip, pull-quote, long-form paragraphs |
| 12 | `myth_vs_fact` | Awareness | Alternating red MYTH / green REALITY panels |
| 13 | `statistics` | Awareness | One giant headline statistic → supporting data cards |
| 14 | `expert_insight` | Awareness | Numbered insight-card compilation (not one narrative) |
| 15 | `guide` | Educational | Table-of-contents strip → numbered sections |
| 16 | `how_it_works` | Educational | Horizontal step-timeline with connecting rail |
| 17 | `checklist` | Educational | Bordered "document" card with checkbox rows |
| 18 | `faq` | Educational | Stacked Q/A rows, accordion-styled |
| 19 | `seasonal` | Campaign | Full-bleed gradient banner, festive framing |
| 20 | `urgency` | Campaign | Dark high-contrast hero, red urgency strip |
| 21 | `announcement` | Campaign | Centered press-release style, pull quote |
| 22 | `new_feature_launch` | Campaign | Split hero: headline left, feature panel right |
| 23 | `discount_campaign` | Campaign | Diagonal two-color price/discount banner |
| 24 | `renewal` | Customer | Policy "statement card" with renewal action bar |
| 25 | `cross_sell` | Customer | "You have X / we recommend Y" split card |
| 26 | `upgrade` | Customer | Before/after tier comparison columns |
| 27 | `re_engagement` | Customer | "We miss you" narrative, single low-friction CTA |
| 28 | `corporate` | Corporate | Formal two-column letterhead, feature table |
| 29 | `employee_benefits` | Corporate | HR coverage-matrix table |
| 30 | `premium_minimal` | Premium | Extreme whitespace, single-column serif, text-link CTA |
| 31 | `luxury_editorial` | Premium | Dark-and-gold editorial spread, full-width feature band |
| 32 | `executive_brief` | Premium | Dense memo-style, numbered clauses, no cards/icons |

Every template is genuinely different in HTML structure, section order, and
CTA placement — not the same layout re-skinned with new colors. See
`preview-gallery/index.html` for a rendered visual gallery of every
template, and `UNIQUENESS_AUDIT.md` for the structural audit.

### Template selection logic

`template_selector.py` matches **campaign intent**, not just topic keywords
— the same topic can resolve to different templates depending on how it's
phrased:

```
"Health Insurance"                               → promotional / product_showcase
"Why You Need Health Insurance"                  → awareness   / editorial
"5 Health Insurance Myths"                       → awareness   / myth_vs_fact
"Renew Your Health Insurance"                    → customer    / renewal
"Get a Health Insurance Quote"                   → lead_generation / quote_generation
"Health Insurance Offer Ends Tomorrow"           → campaign    / urgency
"Health Insurance: Common Questions"             → educational / faq
```

Manual override (`"template": "myth_vs_fact"`) always takes priority, and is
validated against `TEMPLATE_REGISTRY` before use — unknown keys are
rejected with a 400, never used to build a filesystem path.

---

## 7. Evidence / anti-fabrication controls

Because these are regulated insurance marketing emails, invented statistics
are unacceptable. This is enforced in **code**, not only in the prompt:

- `models.Statistic` requires a non-empty `source` at construction time
  (Pydantic validator).
- `evidence.filter_verified_statistics()` is a second, independent pass in
  `generator.py` that strips any statistic missing a source before content
  is returned — defense in depth against a model that ignores instructions.
- The system prompt (`prompts.py`) explicitly instructs the model to prefer
  qualitative language over invented numbers, and to never fabricate named
  testimonials or false deadlines.

---

## 8. Testing

```bash
pytest tests/ -v
```

**Coverage:** 32 templates × 5 campaign topics (Health Insurance, Motor
Insurance, Cyber Insurance, Cashless OPD Services, Policy Renewal) = 160
render checks, plus registry/evidence/error-handling checks = **164 tests
total, all passing.**

Each render check verifies:
```
Template loads → Pydantic validation → Jinja2 rendering (StrictUndefined,
so no silently-blank variables) → HTML generated → CTA present → footer
present → brand present → no leaked {{ }} / {% %} syntax
```

These tests do **not** call the live Groq API (no network dependency, fully
deterministic) — they push a fully-populated, schema-valid mock
`CampaignContent` through the real renderer for every template. The Groq
call path itself is exercised via the `/generate-email` endpoint at runtime
once a `GROQ_API_KEY` is configured.

---

## 9. Regenerating preview files

**Original preview system (10 representative templates):**
```bash
python scripts_generate_previews.py
```
Regenerates the 10 files in `previews/` using realistic, clearly-labeled
mock data (see `MOCK_SOURCE_NOTE` in the script — mock statistics are never
presented as verified real data).

**Full gallery (all 32 templates, added in this upgrade):**
```bash
python generate_gallery.py
```
Regenerates `preview-gallery/` with one rendered HTML file per template
(`01-product_showcase.html` ... `32-executive_brief.html`) plus
`preview-gallery/index.html`, a browsable grid gallery page. Open
`preview-gallery/index.html` directly in any browser — each card links to
the corresponding fully-rendered preview email and opens it in a new tab.
Mock data is clearly labeled `[Sample Statistic]` / `[Sample Terms]` per the
project's evidence conventions — never presented as verified real data.

---

## 10. Security notes

- `renderer.py` **only** loads a template path that comes out of
  `template_registry.TEMPLATE_REGISTRY` — a user-supplied `template` key is
  used purely as a dict lookup, never concatenated into a filesystem path.
  Unknown keys raise a `KeyError` (surfaced as HTTP 400 by the API).
- Brand/legal identity (`config.BRAND`) is never sent to or accepted from
  the LLM.
- `GROQ_API_KEY` is read from environment/`.env` only; never logged, never
  returned in any API response.
- CORS is wide-open (`allow_origins=["*"]`) for easy integration during
  development — **tighten this in `app.py` before production deployment.**

---

## 11. Deploying to Render

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command (API):**
```
uvicorn app:app --host 0.0.0.0 --port $PORT
```

Set `GROQ_API_KEY` (and optionally `GROQ_MODEL`, `MAX_LLM_RETRIES`,
`LLM_TEMPERATURE`, `LLM_MAX_TOKENS`) as environment variables in the Render
dashboard — do not commit `.env`.

To deploy the Streamlit UI as a separate Render service, use:
```
streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0
```

---

## 12. Known limitations

- `template_selector.py` uses deterministic keyword rules rather than an
  LLM classification call — this is intentional (fast, free, auditable,
  no extra latency/cost per request) but means very unusual topic phrasing
  may fall back to the `product_showcase` default. Manual `template`
  override is always available as a fix.
- The Groq call in `generator.py` is synchronous; for high-throughput bulk
  sending, consider adding an async queue/worker layer in front of it.
- Preview thumbnails in the Streamlit gallery are text-only cards (name,
  category, description) rather than rendered image thumbnails, to avoid a
  headless-browser dependency in the base install. `scripts_generate_previews.py`
  can be adapted with `wkhtmltoimage`/Playwright if rendered image thumbnails are needed.
- `VERIFIED_STATISTICS_LIBRARY` in `evidence.py` is a small illustrative
  starter set — a production deployment should back this with an actual
  audited internal data table.
- CORS defaults to `*` for ease of local integration testing; restrict
  `allow_origins` before exposing the API publicly.
