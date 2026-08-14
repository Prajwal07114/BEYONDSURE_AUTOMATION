"""
renderer.py

Renders a validated CampaignContent object into a final, self-contained HTML
email using Jinja2.

SECURITY: the template file path is ALWAYS resolved via
template_registry.get_template_meta() -- a user-supplied template key is only
ever used as a dict lookup, never concatenated into a path. Unknown keys
raise immediately.
"""

import datetime
from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateError

from config import BRAND, TEMPLATES_DIR
from models import CampaignContent
from template_registry import get_template_meta, is_valid_template

_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    undefined=StrictUndefined,  # fail loudly on undefined vars instead of silently rendering blank
    autoescape=True,
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_email(template_key: str, content: CampaignContent) -> str:
    """
    Renders the given validated content into the HTML for `template_key`.

    Raises:
        KeyError: if template_key is not registered.
        TemplateError: if rendering fails (e.g. a template references a
            variable that content doesn't provide and has no default).
    """
    if not is_valid_template(template_key):
        raise KeyError(f"Unknown template key: {template_key}")

    meta = get_template_meta(template_key)
    template = _env.get_template(meta["file"])

    context = {
        "brand": BRAND,
        "content": content,
        "year": datetime.datetime.now(datetime.timezone.utc).year,
    }

    try:
        html = template.render(**context)
    except TemplateError as exc:
        raise TemplateError(f"Failed to render template '{template_key}': {exc}") from exc

    return html
