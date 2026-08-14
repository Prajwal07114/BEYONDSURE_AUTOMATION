"""
app.py

FastAPI application exposing the BeyondSure AI Email Generator as an API,
so the BeyondSure admin bulk-email system (or any other client) can
integrate with it.

Endpoints:
    POST /generate-email     -> full pipeline: analyze -> select -> generate -> validate -> render
    GET  /templates          -> list every registered template (for building a picker UI)
    GET  /health             -> liveness check
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import TemplateError

from config import API_TITLE, API_VERSION
from models import GenerateEmailRequest, GenerateEmailResponse, TemplateListResponse
from template_selector import select_template
from template_registry import list_templates, is_valid_template
from generator import generate_campaign_content
from renderer import render_email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("beyondsure.app")

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="Generates professional, visually unique promotional HTML emails "
                 "for BeyondSure using AI-generated content and a validated template library.",
)

# CORS: open by default for easy integration; tighten allow_origins in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "service": API_TITLE, "version": API_VERSION}


@app.get("/templates", response_model=TemplateListResponse)
def get_templates():
    return {"templates": list_templates()}


@app.post("/generate-email", response_model=GenerateEmailResponse)
def generate_email(req: GenerateEmailRequest):
    # 1 & 2: understand topic + determine intent, 3: select template
    if req.template and not is_valid_template(req.template):
        raise HTTPException(status_code=400, detail=f"Unknown template key: {req.template}")

    try:
        template_key, category = select_template(
            topic=req.topic,
            campaign_type=req.campaign_type,
            target_audience=req.target_audience,
            manual_template=req.template,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # 4 & 5: generate + validate structured content via the LLM
    try:
        content = generate_campaign_content(
            topic=req.topic,
            category=category,
            template_key=template_key,
            target_audience=req.target_audience,
        )
    except RuntimeError as exc:
        logger.error("Content generation failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"Content generation failed: {exc}") from exc

    # 6 & 7: render into the fixed Jinja2 template -> final HTML email
    try:
        html = render_email(template_key, content)
    except (KeyError, TemplateError) as exc:
        logger.error("Rendering failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Rendering failed: {exc}") from exc

    return GenerateEmailResponse(
        topic=req.topic,
        category=category,
        template=template_key,
        content=content,
        html=html,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
