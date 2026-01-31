from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, pets, routines, logs, admin

app = FastAPI(title="LaNature API", version="1.0.0")

@app.on_event("startup")
async def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables initialized successfully")
    except Exception as e:
        print(f"DB INIT ERROR: {e}")
        print("Application will continue, but database operations may fail")

# ================== CORS CONFIGURATION ==================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://lanature.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(pets.router, prefix="/api/v1/pets", tags=["pets"])
app.include_router(routines.router, prefix="/api/v1/routines", tags=["routines"])
app.include_router(logs.router, prefix="/api/v1/logs", tags=["logs"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

@app.get("/")
def root():
    return {"message": "LaNature API"}

@app.get("/health")
def health():
    return {"status": "ok"}
