from __future__ import annotations

import os

# Must run before app/store import in test modules.
os.environ["CGA_DATABASE_URL"] = "sqlite:///:memory:"
os.environ["CGA_GUEST_RATE_LIMIT_PER_HOUR"] = "1000"

import pytest

from app.services.rate_limit import guest_limiter
from app.services.store import store
from app.services.emergency import clear_confirm_tokens


@pytest.fixture(autouse=True)
def reset_state():
    store.reset()
    guest_limiter.reset()
    clear_confirm_tokens()
    yield
    store.reset()
    guest_limiter.reset()
    clear_confirm_tokens()
