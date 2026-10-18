"""Guardrails, authority and governance (week 8).

Planned modules:

- ``injection.py``   -- detect/neutralise direct and indirect prompt injection
- ``sandbox.py``     -- confine tool execution (allowlists, subprocess, timeouts)
- ``authority.py``   -- who may do what, enforced independently of model output
- ``audit.py``       -- append-only action log with before/after evidence
- ``ratelimit.py``   -- quotas per tenant/user

The theme: the model proposes, the system disposes. Never let model output be
the last word on permissions, money, or destructive actions.
"""
