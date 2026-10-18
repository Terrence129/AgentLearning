"""Shared pytest configuration.

The whole curriculum is designed to run offline. Tests marked ``network`` are
skipped unless you explicitly opt in -- that is what keeps CI green and your
test suite fast.
"""

from __future__ import annotations

import os

import pytest


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if os.getenv("AGENTLAB_ALLOW_NETWORK") == "1":
        return
    skip_network = pytest.mark.skip(reason="network test: set AGENTLAB_ALLOW_NETWORK=1 to run")
    for item in items:
        if "network" in item.keywords:
            item.add_marker(skip_network)
