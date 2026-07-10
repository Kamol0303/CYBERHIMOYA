from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

from app import __version__
from app.config import settings
from app.cors_util import parse_cors_origins
from app.models.schemas import HealthResponse
from app.middleware_security import SecurityHeadersMiddleware
from app.routers import auth, consents, emergency, feed, ops, scan, scans
from app.services.feed import FEEDS_DIR, ensure_feed_files

TAGS_METADATA = [
    {"name": "auth", "description": "Register / login / profile (JWT)"},
    {"name": "consents", "description": "Privacy consents (opt-in modules)"},
    {"name": "scan", "description": "Defensive URL / QR / file-hash reputation"},
    {"name": "scans", "description": "Authenticated scan history"},
    {"name": "threat-feed", "description": "Signed IOC delta sync (ed25519)"},
    {"name": "emergency", "description": "Critical reporting — dry-run until AQ-039"},
    {"name": "me", "description": "Account profile / erasure"},
    {"name": "ops", "description": "Health / metrics"},
]

BEARER_SCHEME = {
    "type": "http",
    "scheme": "bearer",
    "bearerFormat": "JWT",
    "description": "Access token from POST /v1/auth/register or /v1/auth/token",
}


def _attach_bearer_openapi(fastapi_app: FastAPI) -> None:
    def custom_openapi():  # type: ignore[no-untyped-def]
        if fastapi_app.openapi_schema:
            return fastapi_app.openapi_schema
        schema = get_openapi(
            title=fastapi_app.title,
            version=fastapi_app.version,
            description=fastapi_app.description,
            routes=fastapi_app.routes,
            tags=fastapi_app.openapi_tags,
        )
        components = schema.setdefault("components", {})
        schemes = components.setdefault("securitySchemes", {})
        schemes["HTTPBearer"] = BEARER_SCHEME
        fastapi_app.openapi_schema = schema
        return fastapi_app.openapi_schema

    fastapi_app.openapi = custom_openapi  # type: ignore[method-assign]


app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description=(
        "Cyber Guardian AI — **defensive-only** API.\n\n"
        "Detection and local protective controls only. "
        "No intrusion tooling against third-party systems. "
        "Emergency dispatch remains dry-run until Legal resolves AQ-039 allowlists."
    ),
    openapi_tags=TAGS_METADATA,
    contact={"name": "Cyber Guardian AI", "url": "https://github.com/Kamol0303/CYBERHIMOYA"},
    license_info={"name": "Proprietary — defensive use only"},
)
_attach_bearer_openapi(app)

# chrome-extension://* in CGA_CORS_ORIGINS becomes allow_origin_regex (Starlette
# does not treat * inside allow_origins as a wildcard).
cors_origins, cors_origin_regex = parse_cors_origins(settings.cors_origins)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins else (["*"] if not cors_origin_regex else []),
    allow_origin_regex=cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = FastAPI(
    title=f"{settings.app_name} /v1",
    version=__version__,
    openapi_tags=TAGS_METADATA,
)
_attach_bearer_openapi(api)
api.include_router(auth.router)
api.include_router(auth.me_router)
api.include_router(consents.router)
api.include_router(scan.router)
api.include_router(scans.router)
api.include_router(feed.router)
api.include_router(emergency.router)
api.include_router(ops.router)
app.mount("/v1", api)

FEEDS_DIR.mkdir(parents=True, exist_ok=True)
ensure_feed_files()
app.mount("/cdn/feeds", StaticFiles(directory=str(FEEDS_DIR)), name="feed_cdn")


def _storage_label() -> str:
    url = settings.database_url
    if url.startswith("sqlite"):
        return "sqlite"
    if url.startswith("postgres"):
        return "postgresql"
    return "unknown"


@app.get("/health", response_model=HealthResponse, tags=["ops"])
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version=__version__,
        defensive_only=True,
        storage=_storage_label(),
    )


@app.get("/", tags=["ops"])
def root() -> dict:
    return {
        "name": settings.app_name,
        "version": __version__,
        "docs": "/docs",
        "api": "/v1",
        "feed_cdn": "/cdn/feeds",
        "defensive_only": True,
        "storage": _storage_label(),
    }
