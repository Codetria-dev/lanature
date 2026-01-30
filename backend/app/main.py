from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, pets, routines, logs, admin

app = FastAPI(title="LaNature API", version="1.0.0")

@app.on_event("startup")
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print("DB INIT ERROR:", e)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://lanature.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(pets.router, prefix="/api/v1/pets", tags=["pets"])
app.include_router(routines.router, prefix="/api/v1/routines", tags=["routines"])
app.include_router(logs.router, prefix="/api/v1/logs", tags=["logs"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

@app.get("/")
def root():
    return {"message": "LaNature API"}
