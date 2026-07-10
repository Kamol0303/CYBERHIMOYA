"""Password health (FR-050) — never store or log the password."""

from __future__ import annotations

import re

# Tiny common-password seed (defensive education only).
COMMON = {
    "password",
    "password1",
    "123456",
    "12345678",
    "qwerty",
    "admin",
    "letmein",
    "welcome",
    "iloveyou",
    "monkey",
    "dragon",
    "master",
    "login",
    "abc123",
    "passw0rd",
}


def assess_password(password: str) -> dict:
    score = 0
    reasons: list[dict[str, str]] = []
    length = len(password)
    if length >= 12:
        score += 35
    elif length >= 8:
        score += 20
        reasons.append({"code": "SHORT", "message_key": "pwd.short"})
    else:
        reasons.append({"code": "TOO_SHORT", "message_key": "pwd.too_short"})

    if re.search(r"[a-z]", password) and re.search(r"[A-Z]", password):
        score += 15
    else:
        reasons.append({"code": "CASE", "message_key": "pwd.case"})

    if re.search(r"\d", password):
        score += 15
    else:
        reasons.append({"code": "DIGIT", "message_key": "pwd.digit"})

    if re.search(r"[^A-Za-z0-9]", password):
        score += 20
    else:
        reasons.append({"code": "SYMBOL", "message_key": "pwd.symbol"})

    if password.lower() in COMMON:
        score = min(score, 15)
        reasons.append({"code": "COMMON", "message_key": "pwd.common"})

    score = max(0, min(100, score))
    if score >= 80:
        verdict = "strong"
    elif score >= 50:
        verdict = "fair"
    else:
        verdict = "weak"
    return {
        "score": score,
        "verdict": verdict,
        "reasons": reasons,
        "recommendations": [
            "use_passphrase",
            "enable_2fa",
            "unique_passwords",
        ]
        if verdict != "strong"
        else ["enable_2fa"],
    }
