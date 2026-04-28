from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from fastapi import Request
from pathlib import Path
from app.routers import auth, pets, routines, logs, admin, billing, analytics, integrations
from app.middleware.rate_limit import limiter
from app.observability import add_observability, configure_logging, configure_sentry

app = FastAPI(
    title="LaNature API",
    description="""
    Comprehensive pet care management platform with scheduling, reminders, and analytics.

    ## Features
    - **Pet Management**: Create, update, and manage pet profiles with images
    - **Routine Scheduling**: Set up daily, weekly, and monthly care routines
    - **Task Logging**: Track completed tasks and monitor pet care
    - **Analytics**: Real-time metrics on task completion and pet care trends
    - **User Authentication**: Secure JWT-based authentication with role-based access
    - **Rate Limiting**: Protection against brute force attacks
    - **Image Handling**: Automatic image resizing and optimization

    ## Authentication
    All endpoints (except `/auth/register` and `/auth/login`) require a Bearer token:
    ```
    Authorization: Bearer {your_jwt_token}
    ```

    ## Rate Limits
    - **Login**: 5 requests/minute per IP
    - **Register**: 3 requests/hour per IP
    - **General**: 100 requests/minute per user
    """,
    version="2.0.0",
    contact={
        "name": "LaNature Support",
        "url": "https://lanature.app",
        "email": "support@lanature.app",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)

# ================== CORS CONFIGURATION ==================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],                    # Accepts any domain
    allow_credentials=False,                # ⚠️ Must be False when using "*"
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.state.limiter = limiter
configure_logging()
configure_sentry()
add_observability(app)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Custom handler for rate limit exceeded errors."""
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests. Please try again later.",
        }
    )

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(pets.router, prefix="/api/v1/pets", tags=["pets"])
app.include_router(routines.router, prefix="/api/v1/routines", tags=["routines"])
app.include_router(logs.router, prefix="/api/v1/logs", tags=["logs"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(billing.router, prefix="/api/v1/billing", tags=["billing"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(integrations.router, prefix="/api/v1/integrations", tags=["integrations"])

# Mount static files for image uploads (Phase 5)
uploads_dir = Path("./uploads")
uploads_dir.mkdir(exist_ok=True)
app.mount("/api/v1/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

@app.get("/")
def root():
    return {"message": "LaNature API"}

@app.get("/health")
def health():
    return {"status": "ok"}
