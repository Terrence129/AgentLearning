"""Optional web surface for the capstone (week 9).

The course's core dependencies do not include FastAPI. This module therefore
guards the import: importing ``agentlab.web`` must always work, and only
``create_app`` needs the ``web`` extra. Install it with::

    # Windows (PowerShell)
    .\\.venv\\Scripts\\python.exe -m pip install -e ".[web]"

    # macOS / Linux
    uv sync --extra web

The routes are deliberately thin: the platform already owns the lifecycle and the
audit trail, so the UI only renders a decision and forwards an approval. Every
route is a TODO until you implement the capstone platform; until then the app
starts and returns a clear "not implemented" response instead of crashing.
"""

from agentlab.web.app import FASTAPI_AVAILABLE, create_app

__all__ = ["FASTAPI_AVAILABLE", "create_app"]
