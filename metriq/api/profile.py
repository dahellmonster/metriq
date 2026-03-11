# --------------------------------------------------
# Metriq Profile / API Key Management
# --------------------------------------------------

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import os
import secrets

router = APIRouter()

# --------------------------------------------------
# Template configuration
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Location of environment file
ENV_PATH = "/opt/metriq/.env"


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def read_api_key():
    """
    Read the current API key from environment variables.
    """
    return os.getenv("METRIQ_API_KEY")


def generate_api_key():
    """
    Generate a new secure API key.
    """
    return secrets.token_hex(32)


def write_api_key(new_key):
    """
    Update the API key in the .env file and reload
    it into the running environment.
    """

    lines = []

    if os.path.exists(ENV_PATH):

        with open(ENV_PATH) as f:
            lines = f.readlines()

    found = False

    for i, line in enumerate(lines):

        if line.startswith("METRIQ_API_KEY="):

            lines[i] = f"METRIQ_API_KEY={new_key}\n"

            found = True

    if not found:

        lines.append(f"METRIQ_API_KEY={new_key}\n")

    with open(ENV_PATH, "w") as f:

        f.writelines(lines)

    # Reload key into environment
    os.environ["METRIQ_API_KEY"] = new_key


# --------------------------------------------------
# Profile page
# --------------------------------------------------

@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):

    key = read_api_key()

    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "api_key": key
        }
    )


# --------------------------------------------------
# Regenerate API key
# --------------------------------------------------

@router.post("/profile/regenerate")
async def regenerate():

    new_key = generate_api_key()

    write_api_key(new_key)

    return {
        "status": "ok",
        "new_key": new_key
    }