"""Parse CGA_CORS_ORIGINS into exact origins + optional regex.

Starlette ``allow_origins`` does not treat ``*`` inside an origin string as a
wildcard. Chrome extension IDs are dynamic in unpacked loads, so
``chrome-extension://*`` is expanded to ``allow_origin_regex``.
"""

from __future__ import annotations


# Chrome extension IDs are 32 lowercase a-p chars; allow a-z for leniency in dev.
_CHROME_EXTENSION_ORIGIN_RE = r"chrome-extension://[a-z]+"


def parse_cors_origins(raw: str) -> tuple[list[str], str | None]:
    exact: list[str] = []
    regex_parts: list[str] = []
    for part in raw.split(","):
        origin = part.strip()
        if not origin:
            continue
        if origin in {"chrome-extension://*", "chrome-extension://.*"}:
            regex_parts.append(_CHROME_EXTENSION_ORIGIN_RE)
        else:
            exact.append(origin)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_exact: list[str] = []
    for o in exact:
        if o not in seen:
            seen.add(o)
            unique_exact.append(o)
    unique_regex = list(dict.fromkeys(regex_parts))
    combined = "|".join(f"(?:{r})" for r in unique_regex) if unique_regex else None
    return unique_exact, combined
