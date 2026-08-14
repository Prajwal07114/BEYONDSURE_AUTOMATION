"""
streamlit_app.py

BeyondSure AI Email Generator

Workflow:

1. User enters campaign topic
2. System validates Healthcare / Insurance domain
3. System finds 5 relevant + structurally different templates
4. Five HTML previews are shown
5. User selects one template
6. Groq generates the final campaign content
7. Final email is rendered using the selected template
8. User can regenerate the email without selecting a template again
"""

from pathlib import Path

import streamlit as st

from config import BRAND, CAMPAIGN_CATEGORIES
from template_registry import TEMPLATE_REGISTRY, list_templates
from template_selector import select_templates
from generator import generate_campaign_content
from renderer import render_email


# ============================================================================
# DOMAIN VALIDATION
# ============================================================================

ALLOWED_DOMAIN_KEYWORDS = [
    # Healthcare
    "health",
    "healthcare",
    "hospital",
    "doctor",
    "medical",
    "medicine",
    "clinic",
    "patient",
    "diagnosis",
    "treatment",
    "surgery",
    "wellness",
    "opd",
    "pharmacy",
    "dental",
    "diagnostic",
    "checkup",
    "telemedicine",

    # Insurance
    "insurance",
    "policy",
    "premium",
    "claim",
    "coverage",
    "insured",
    "insurer",
    "life insurance",
    "health insurance",
    "motor insurance",
    "car insurance",
    "vehicle insurance",
    "travel insurance",
    "home insurance",
    "term insurance",
]


def is_allowed_domain(topic: str) -> bool:
    """Allow only Healthcare and Insurance related topics."""

    topic_lower = topic.lower().strip()

    return any(
        keyword in topic_lower
        for keyword in ALLOWED_DOMAIN_KEYWORDS
    )


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

DEFAULT_SESSION_STATE = {
    "recommended_templates": None,
    "preview_topic": None,
    "selected_template": None,
    "selected_category": None,
    "last_html": None,
    "last_topic": None,
    "last_template": None,
}


for key, default_value in DEFAULT_SESSION_STATE.items():

    if key not in st.session_state:
        st.session_state[key] = default_value


# ============================================================================
# CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="BeyondSure AI Email Generator",
    page_icon="Email",
    layout="wide",
)


# ============================================================================
# PATHS
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent

TEMPLATES_DIR = BASE_DIR / "templates"

PREVIEW_GALLERY_DIR = BASE_DIR / "preview-gallery"


# ============================================================================
# CSS
# ============================================================================

st.markdown(
    """
    <style>

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1600px;
    }

    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.25rem;
    }

    .template-name {
        font-size: 1.15rem;
        font-weight: 700;
        margin-top: 0.5rem;
    }

    .template-category {
        font-size: 0.85rem;
        color: #6b7280;
        margin-bottom: 0.5rem;
    }

    .selected-box {
        padding: 1rem;
        border-radius: 12px;
        border: 2px solid #22c55e;
        background: #f0fdf4;
        margin: 1rem 0;
    }

    .preview-box {
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 8px;
        background: white;
    }

    .step-title {
        font-size: 1.3rem;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_template_preview_path(template_key: str):
    """
    Find the HTML preview for a template.

    Supported locations:

        preview-gallery/<template_key>.html
        preview-gallery/<number>-<template_key>.html
        templates/<template_key>.html
    """

    if PREVIEW_GALLERY_DIR.exists():

        direct_path = (
            PREVIEW_GALLERY_DIR
            / f"{template_key}.html"
        )

        if direct_path.exists():
            return direct_path

        matches = list(
            PREVIEW_GALLERY_DIR.glob(
                f"*{template_key}*.html"
            )
        )

        if matches:
            return matches[0]

    if TEMPLATES_DIR.exists():

        direct_path = (
            TEMPLATES_DIR
            / f"{template_key}.html"
        )

        if direct_path.exists():
            return direct_path

        matches = list(
            TEMPLATES_DIR.glob(
                f"*{template_key}*.html"
            )
        )

        if matches:
            return matches[0]

    return None


def load_template_preview(template_key: str):
    """
    Load an existing static HTML preview.

    No LLM call is made here.
    """

    preview_path = get_template_preview_path(
        template_key
    )

    if preview_path is None:
        return None

    try:

        return preview_path.read_text(
            encoding="utf-8"
        )

    except Exception:

        return None


def find_five_templates(
    topic: str,
    campaign_type=None,
    target_audience=None,
):
    """
    Ask the deterministic selector for five
    relevant and structurally diverse templates.
    """

    return select_templates(
        topic=topic,
        campaign_type=campaign_type,
        target_audience=target_audience,
        count=5,
    )


def normalize_template_data(template_data):
    """
    Normalize selector output.

    Supports:

        ("template_key", "category")

    and:

        {
            "key": "...",
            "category": "..."
        }
    """

    if isinstance(template_data, tuple):

        template_key = template_data[0]

        category = (
            template_data[1]
            if len(template_data) > 1
            else "promotional"
        )

        return template_key, category

    if isinstance(template_data, dict):

        template_key = template_data.get(
            "key",
            template_data.get(
                "template_key"
            ),
        )

        category = template_data.get(
            "category",
            "promotional",
        )

        return template_key, category

    return None, "promotional"


# ============================================================================
# HEADER
# ============================================================================

st.markdown(
    '<div class="hero-title">BeyondSure AI Email Generator</div>',
    unsafe_allow_html=True,
)

st.caption(BRAND["tagline"])


# ============================================================================
# TABS
# ============================================================================

tab_generate, tab_gallery = st.tabs(
    [
        "Generate Email",
        "Template Gallery",
    ]
)


# ============================================================================
# GENERATE EMAIL TAB
# ============================================================================

with tab_generate:

    st.subheader("Campaign Details")

    # ------------------------------------------------------------------------
    # INPUTS
    # ------------------------------------------------------------------------

    topic = st.text_input(
        "Campaign Topic",
        placeholder="e.g. Health Insurance",
        key="campaign_topic",
    )

    target_audience = st.text_input(
        "Target Audience (optional)",
        placeholder="e.g. Young families, 25-40",
        key="target_audience",
    )

    category_options = (
        ["Auto Detect"]
        + [
            c.replace("_", " ").title()
            for c in CAMPAIGN_CATEGORIES
        ]
    )

    category_choice = st.selectbox(
        "Campaign Type",
        category_options,
        index=0,
        key="campaign_type",
    )

    # ------------------------------------------------------------------------
    # STEP 1
    # ------------------------------------------------------------------------

    st.markdown(
        '<div class="step-title">Step 1: Find Designs</div>',
        unsafe_allow_html=True,
    )

    find_templates_clicked = st.button(
        "Show 5 Unique Templates",
        type="primary",
        use_container_width=True,
    )

    # ------------------------------------------------------------------------
    # FIND TEMPLATES
    # ------------------------------------------------------------------------

    if find_templates_clicked:

        # --------------------------------------------------------------------
        # BASIC VALIDATION
        # --------------------------------------------------------------------

        if not topic or len(topic.strip()) < 3:

            st.error(
                "Please enter a campaign topic "
                "with at least 3 characters."
            )

            st.stop()

        # --------------------------------------------------------------------
        # DOMAIN VALIDATION
        # --------------------------------------------------------------------

        if not is_allowed_domain(topic):

            st.error(
                "Template cannot be generated."
            )

            st.warning(
                "This AI Email Generator supports only "
                "Healthcare and Insurance related campaigns."
            )

            st.info(
                "Try topics such as Health Insurance, OPD Services, "
                "Hospital Care, Insurance Renewal, Medical Checkup, "
                "or Insurance Claims."
            )

            st.stop()

        # --------------------------------------------------------------------
        # CATEGORY
        # --------------------------------------------------------------------

        manual_category = None

        if category_choice != "Auto Detect":

            manual_category = (
                category_choice
                .lower()
                .replace(" ", "_")
            )

        # --------------------------------------------------------------------
        # SELECT FIVE TEMPLATES
        # --------------------------------------------------------------------

        with st.spinner(
            "Finding the best 5 unique designs..."
        ):

            try:

                recommended_templates = find_five_templates(
                    topic=topic.strip(),
                    campaign_type=manual_category,
                    target_audience=(
                        target_audience.strip()
                        or None
                    ),
                )

            except Exception as exc:

                st.error(
                    f"Template selection failed: {exc}"
                )

                st.stop()

        if not recommended_templates:

            st.error(
                "No templates were found."
            )

            st.stop()

        # --------------------------------------------------------------------
        # SAVE RECOMMENDATIONS
        # --------------------------------------------------------------------

        st.session_state[
            "recommended_templates"
        ] = recommended_templates

        st.session_state[
            "preview_topic"
        ] = topic.strip()

        # --------------------------------------------------------------------
        # RESET PREVIOUS SELECTION
        # --------------------------------------------------------------------

        st.session_state[
            "selected_template"
        ] = None

        st.session_state[
            "selected_category"
        ] = None

        st.session_state[
            "last_html"
        ] = None

        st.session_state[
            "last_topic"
        ] = None

        st.session_state[
            "last_template"
        ] = None


    # =========================================================================
    # STEP 2: SHOW FIVE PREVIEWS
    # =========================================================================

    if st.session_state.get(
        "recommended_templates"
    ):

        st.divider()

        st.markdown(
            '<div class="step-title">'
            "Step 2: Choose Your Email Design"
            "</div>",
            unsafe_allow_html=True,
        )

        st.caption(
            "Five structurally different designs "
            "were selected for your campaign. "
            "Groq has NOT been called yet."
        )

        templates = st.session_state[
            "recommended_templates"
        ]

        # --------------------------------------------------------------------
        # SHOW 5 PREVIEWS
        # --------------------------------------------------------------------

        for row_start in range(
            0,
            len(templates),
            3,
        ):

            row_templates = templates[
                row_start:row_start + 3
            ]

            cols = st.columns(
                len(row_templates),
                gap="large",
            )

            for local_index, (
                col,
                template_data,
            ) in enumerate(
                zip(
                    cols,
                    row_templates,
                )
            ):

                index = (
                    row_start
                    + local_index
                )

                template_key, category = (
                    normalize_template_data(
                        template_data
                    )
                )

                if not template_key:
                    continue

                metadata = TEMPLATE_REGISTRY.get(
                    template_key,
                    {},
                )

                display_name = metadata.get(
                    "display_name",
                    template_key.replace(
                        "_",
                        " ",
                    ).title(),
                )

                description = metadata.get(
                    "description",
                    "",
                )

                with col:

                    st.markdown(
                        f"### {display_name}"
                    )

                    st.caption(
                        str(category)
                        .replace("_", " ")
                        .title()
                    )

                    if description:

                        st.caption(
                            description
                        )

                    # --------------------------------------------------------
                    # PREVIEW
                    # --------------------------------------------------------

                    preview_html = (
                        load_template_preview(
                            template_key
                        )
                    )

                    if preview_html:

                        st.components.v1.html(
                            preview_html,
                            height=600,
                            scrolling=True,
                        )

                    else:

                        st.warning(
                            "Preview HTML not found."
                        )

                        st.code(
                            template_key
                        )

                    # --------------------------------------------------------
                    # SELECT TEMPLATE
                    # --------------------------------------------------------

                    if st.button(
                        "Use This Template",
                        key=(
                            "use_template_"
                            f"{template_key}_"
                            f"{index}"
                        ),
                        type="secondary",
                        use_container_width=True,
                    ):

                        st.session_state[
                            "selected_template"
                        ] = template_key

                        st.session_state[
                            "selected_category"
                        ] = category

                        st.session_state[
                            "last_html"
                        ] = None

                        st.session_state[
                            "last_topic"
                        ] = None

                        st.session_state[
                            "last_template"
                        ] = None

                        st.rerun()


    # =========================================================================
    # SELECTED TEMPLATE
    # =========================================================================

    if st.session_state.get(
        "selected_template"
    ):

        selected_template = (
            st.session_state[
                "selected_template"
            ]
        )

        selected_category = (
            st.session_state[
                "selected_category"
            ]
        )

        selected_metadata = (
            TEMPLATE_REGISTRY.get(
                selected_template,
                {},
            )
        )

        selected_name = (
            selected_metadata.get(
                "display_name",
                selected_template,
            )
        )

        st.divider()

        st.markdown(
            f"""
            <div class="selected-box">
                <strong>Selected Template</strong><br>
                {selected_name}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # --------------------------------------------------------------------
        # STEP 3
        # --------------------------------------------------------------------

        st.markdown(
            '<div class="step-title">'
            "Step 3: Generate Final Email"
            "</div>",
            unsafe_allow_html=True,
        )

        st.caption(
            "Groq is called only after you select a template."
        )

        generate_final_clicked = st.button(
            "Generate Final Email",
            type="primary",
            use_container_width=True,
        )

        if generate_final_clicked:

            final_topic = st.session_state.get(
                "preview_topic",
                topic.strip(),
            )

            # ----------------------------------------------------------------
            # GROQ
            # ----------------------------------------------------------------

            with st.spinner(
                "Generating campaign content with Groq..."
            ):

                try:

                    content = generate_campaign_content(
                        topic=final_topic,
                        category=selected_category,
                        template_key=selected_template,
                        target_audience=(
                            target_audience.strip()
                            or None
                        ),
                    )

                except Exception as exc:

                    st.error(
                        f"Content generation failed: {exc}"
                    )

                    st.stop()

            # ----------------------------------------------------------------
            # RENDER
            # ----------------------------------------------------------------

            with st.spinner(
                "Rendering final email..."
            ):

                try:

                    html = render_email(
                        selected_template,
                        content,
                    )

                except Exception as exc:

                    st.error(
                        f"Email rendering failed: {exc}"
                    )

                    st.stop()

            # ----------------------------------------------------------------
            # SAVE RESULT
            # ----------------------------------------------------------------

            st.session_state[
                "last_html"
            ] = html

            st.session_state[
                "last_topic"
            ] = final_topic

            st.session_state[
                "last_template"
            ] = selected_template

            st.success(
                "Final email generated successfully."
            )


    # =========================================================================
    # FINAL EMAIL PREVIEW
    # =========================================================================

    if st.session_state.get(
        "last_html"
    ):

        st.divider()

        st.subheader(
            "Generated Email"
        )

        st.components.v1.html(
            st.session_state[
                "last_html"
            ],
            height=800,
            scrolling=True,
        )

        # --------------------------------------------------------------------
        # DOWNLOAD FILE NAME
        # --------------------------------------------------------------------

        file_slug = (
            "beyondsure_"
            + st.session_state[
                "last_topic"
            ].lower().replace(
                " ",
                "_",
            )
            + "_"
            + st.session_state[
                "last_template"
            ]
            + ".html"
        )

        # --------------------------------------------------------------------
        # ACTION BUTTONS
        # --------------------------------------------------------------------

        col_regenerate, col_download = st.columns(2)

        with col_regenerate:

            regenerate_clicked = st.button(
                "Regenerate Email",
                type="secondary",
                use_container_width=True,
            )

        with col_download:

            st.download_button(
                "Download HTML",
                data=st.session_state[
                    "last_html"
                ],
                file_name=file_slug,
                mime="text/html",
                use_container_width=True,
            )

        # --------------------------------------------------------------------
        # REGENERATE EMAIL
        # --------------------------------------------------------------------

        if regenerate_clicked:

            final_topic = st.session_state.get(
                "last_topic",
                st.session_state.get(
                    "preview_topic",
                    topic.strip(),
                ),
            )

            selected_template = st.session_state.get(
                "last_template"
            )

            selected_category = st.session_state.get(
                "selected_category"
            )

            if not selected_template:

                st.error(
                    "Please select a template before regenerating."
                )

                st.stop()

            with st.spinner(
                "Regenerating email with Groq..."
            ):

                try:

                    # --------------------------------------------------------
                    # CALL GROQ AGAIN
                    # --------------------------------------------------------

                    content = generate_campaign_content(
                        topic=final_topic,
                        category=selected_category,
                        template_key=selected_template,
                        target_audience=(
                            target_audience.strip()
                            or None
                        ),
                    )

                    # --------------------------------------------------------
                    # RENDER NEW EMAIL
                    # --------------------------------------------------------

                    html = render_email(
                        selected_template,
                        content,
                    )

                    # --------------------------------------------------------
                    # REPLACE OLD EMAIL
                    # --------------------------------------------------------

                    st.session_state[
                        "last_html"
                    ] = html

                    st.session_state[
                        "last_topic"
                    ] = final_topic

                    st.session_state[
                        "last_template"
                    ] = selected_template

                    st.success(
                        "Email regenerated successfully."
                    )

                    st.rerun()

                except Exception as exc:

                    st.error(
                        f"Regeneration failed: {exc}"
                    )

        # --------------------------------------------------------------------
        # RAW HTML
        # --------------------------------------------------------------------

        with st.expander(
            "View Raw HTML"
        ):

            st.code(
                st.session_state[
                    "last_html"
                ],
                language="html",
            )


# ============================================================================
# TEMPLATE GALLERY TAB
# ============================================================================

with tab_gallery:

    st.subheader(
        "Template Gallery"
    )

    st.caption(
        f"{len(TEMPLATE_REGISTRY)} "
        "structurally unique templates."
    )

    templates = list_templates()

    cols_per_row = 3

    for i in range(
        0,
        len(templates),
        cols_per_row,
    ):

        row = templates[
            i:i + cols_per_row
        ]

        cols = st.columns(
            len(row),
            gap="large",
        )

        for col, template in zip(
            cols,
            row,
        ):

            metadata = TEMPLATE_REGISTRY[
                template["key"]
            ]

            with col:

                st.markdown(
                    f"### {template['display_name']}"
                )

                st.caption(
                    template["category"]
                    .replace(
                        "_",
                        " ",
                    )
                    .title()
                )

                st.write(
                    metadata.get(
                        "description",
                        "",
                    )
                )

                # ------------------------------------------------------------
                # GALLERY PREVIEW
                # ------------------------------------------------------------

                preview_html = (
                    load_template_preview(
                        template["key"]
                    )
                )

                if preview_html:

                    with st.expander(
                        "View Preview"
                    ):

                        st.components.v1.html(
                            preview_html,
                            height=500,
                            scrolling=True,
                        )

                else:

                    st.caption(
                        "Preview not available."
                    )

                st.divider()