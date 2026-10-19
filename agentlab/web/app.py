"""Thin FastAPI surface for the capstone (week 9).

Design rules
------------
1. **Import-safe.** The course does not install FastAPI by default. Importing
   this module must always work; only ``create_app`` requires the ``web`` extra.
2. **Thin.** The platform owns the lifecycle (decisions, approval binding, audit).
   Routes translate HTTP <-> platform calls and nothing else.
3. **Graceful.** Before the capstone is built -- or when no platform is passed --
   every route answers ``501 not_implemented`` with a helpful detail instead of
   raising. The UI is explorable from day one.
4. **Ugly on purpose.** One string template, no build step, no JS framework. The
   point of week 9 is the governed runtime, not front-end tooling.
"""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any

from agentlab.capstone import CapstoneError, GoalRequest
from agentlab.capstone.decisions import decision_to_wire
from agentlab.errors import ConfigError

try:  # pragma: no cover - exercised only when the web extra is installed
    from fastapi import FastAPI, Request
    from fastapi.responses import HTMLResponse, JSONResponse
except ImportError:  # pragma: no cover - the default course environment
    FastAPI = None  # type: ignore[assignment,misc]
    Request = None  # type: ignore[assignment,misc]
    HTMLResponse = None  # type: ignore[assignment,misc]
    JSONResponse = None  # type: ignore[assignment,misc]

FASTAPI_AVAILABLE: bool = FastAPI is not None

INSTALL_HINT = (
    "FastAPI is not installed. Install the optional web extra from the repo root:  "
    "uv sync --extra web  (all platforms; Windows pip fallback: "
    r'.\.venv\Scripts\python.exe -m pip install -e ".[web]")'
)

INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Mini-SendOS</title>
  <style>
    body { font: 15px/1.5 system-ui, sans-serif; margin: 2rem auto; max-width: 60rem; padding: 0 1rem; }
    form { display: grid; gap: .5rem; margin: 1rem 0; }
    input, button { font: inherit; padding: .5rem; }
    pre { background: #f4f4f4; padding: 1rem; overflow: auto; border-radius: 6px; }
    .hint { color: #555; }
  </style>
</head>
<body>
  <h1>Mini-SendOS</h1>
  <p class="hint">Goal &rarr; typed decision &rarr; approval &rarr; execution &rarr; audit.
  This page renders the platform's typed decision; it never invents text.</p>
  <form id="goal-form">
    <input id="goal" value="Apply a 10% discount to order ORD-1" aria-label="Goal">
    <input id="tenant" value="acme" aria-label="Tenant">
    <input id="actor" value="analyst-1" aria-label="Actor">
    <button type="submit">Submit goal</button>
  </form>
  <pre id="out">No request yet.</pre>
  <p class="hint">API: POST /api/goal, POST /api/proposals,
  POST /api/proposals/{id}/approve, POST /api/proposals/{id}/execute, GET /api/audit.</p>
  <script>
    const out = document.getElementById("out");
    document.getElementById("goal-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const body = {
        goal: document.getElementById("goal").value,
        tenant_id: document.getElementById("tenant").value,
        actor_id: document.getElementById("actor").value,
      };
      const res = await fetch("/api/goal", {
        method: "POST", headers: {"content-type": "application/json"}, body: JSON.stringify(body),
      });
      out.textContent = JSON.stringify(await res.json(), null, 2);
    });
  </script>
</body>
</html>
"""


def _jsonable(value: Any) -> Any:
    """Convert dataclasses / datetimes / tuples into a JSON-safe structure."""
    if is_dataclass(value) and not isinstance(value, type):
        return {key: _jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_jsonable(item) for item in value]
    if hasattr(value, "isoformat") and not isinstance(value, str):
        return value.isoformat()
    return value


def _json_response(payload: Any, *, status_code: int = 200) -> Any:
    """FastAPI JSONResponse with a generic serialisation step."""
    safe = json.loads(json.dumps(_jsonable(payload), default=str))
    return JSONResponse(content=safe, status_code=status_code)


def _not_implemented(detail: str) -> Any:
    return JSONResponse(
        status_code=501,
        content={
            "status": "not_implemented",
            "detail": detail,
            "next": "Build the week 9 capstone: python scripts/demo_capstone.py prints what is missing.",
        },
    )


def create_app(platform: Any | None = None) -> Any:
    """Create the FastAPI app for ``platform`` (or a graceful stub app).

    Raises ``ConfigError`` when FastAPI is not installed. Passing ``platform=None``
    is supported: every data route returns ``501`` until a platform is wired in,
    which lets you see the UI before the runtime exists.
    """
    if not FASTAPI_AVAILABLE:
        raise ConfigError(INSTALL_HINT)

    app = FastAPI(title="Mini-SendOS", version="0.1.0")
    not_ready = "The capstone platform is not wired yet (pass create_app(platform=...))."

    @app.get("/", response_class=HTMLResponse)
    async def index() -> Any:
        return HTMLResponse(INDEX_HTML)

    @app.get("/health")
    async def health() -> Any:
        return _json_response({"status": "ok", "platform": "ready" if platform else "not_implemented"})

    async def _body(request: Any) -> dict[str, Any]:
        try:
            parsed = await request.json()
        except Exception:
            return {}
        return parsed if isinstance(parsed, dict) else {}

    @app.post("/api/goal")
    async def goal(request: Any) -> Any:
        if platform is None:
            return _not_implemented(not_ready)
        body = await _body(request)
        missing = [key for key in ("goal", "tenant_id", "actor_id") if not body.get(key)]
        if missing:
            return _json_response({"detail": f"missing fields: {', '.join(missing)}"}, status_code=422)
        try:
            decision = platform.submit_goal(
                GoalRequest(
                    goal=str(body["goal"]),
                    tenant_id=str(body["tenant_id"]),
                    actor_id=str(body["actor_id"]),
                )
            )
            return _json_response(decision_to_wire(decision))
        except NotImplementedError as exc:
            return _not_implemented(str(exc))

    @app.post("/api/proposals")
    async def propose(request: Any) -> Any:
        if platform is None:
            return _not_implemented(not_ready)
        body = await _body(request)
        try:
            proposal = platform.propose_action(
                GoalRequest(
                    goal=str(body.get("goal", "")),
                    tenant_id=str(body.get("tenant_id", "")),
                    actor_id=str(body.get("actor_id", "")),
                ),
                str(body.get("capability_id", "")),
                dict(body.get("arguments") or {}),
            )
            return _json_response(proposal, status_code=201)
        except NotImplementedError as exc:
            return _not_implemented(str(exc))
        except CapstoneError as exc:
            return _json_response({"detail": str(exc)}, status_code=409)

    @app.post("/api/proposals/{proposal_id}/approve")
    async def approve(proposal_id: str, request: Any) -> Any:
        if platform is None:
            return _not_implemented(not_ready)
        body = await _body(request)
        try:
            approval = platform.approve(
                proposal_id,
                approver_id=str(body.get("approver_id", "")),
                approved=bool(body.get("approved", False)),
            )
            return _json_response(approval)
        except NotImplementedError as exc:
            return _not_implemented(str(exc))
        except CapstoneError as exc:
            return _json_response({"detail": str(exc)}, status_code=409)

    @app.post("/api/proposals/{proposal_id}/execute")
    async def execute(proposal_id: str, request: Any) -> Any:
        if platform is None:
            return _not_implemented(not_ready)
        body = await _body(request)
        try:
            receipt = platform.execute(proposal_id, approval_id=str(body.get("approval_id", "")))
            return _json_response(receipt)
        except NotImplementedError as exc:
            return _not_implemented(str(exc))
        except CapstoneError as exc:
            return _json_response({"detail": str(exc)}, status_code=409)

    @app.get("/api/audit")
    async def audit() -> Any:
        if platform is None:
            return _not_implemented(not_ready)
        try:
            return _json_response(platform.audit_trail())
        except NotImplementedError as exc:
            return _not_implemented(str(exc))

    return app


def main() -> None:
    """Run the demo UI locally: ``python -m agentlab.web.app`` (requires the web extra)."""
    if not FASTAPI_AVAILABLE:
        raise ConfigError(INSTALL_HINT)
    import uvicorn  # local import: optional dependency, only needed for serving

    uvicorn.run(create_app(platform=None), host="127.0.0.1", port=8000)


if __name__ == "__main__":  # pragma: no cover
    main()
