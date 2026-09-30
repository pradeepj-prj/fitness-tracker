from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text
from app.database import engine, Base, SessionLocal
from app.models import Settings
from app.routers import settings, entries, deficit, foods, weights, agent, auth
from app.security import auth_enabled, request_is_authenticated
from pathlib import Path

DEFAULT_PROFILES = {
    "vidhi": 1500.0,
    "pradeep": 2000.0,
}


def run_migrations():
    inspector = inspect(engine)

    food_entry_columns = {col["name"] for col in inspector.get_columns("food_entries")} if inspector.has_table("food_entries") else set()
    settings_columns = {col["name"] for col in inspector.get_columns("settings")} if inspector.has_table("settings") else set()

    with engine.begin() as conn:
        if inspector.has_table("food_entries") and "profile" not in food_entry_columns:
            conn.execute(text("ALTER TABLE food_entries ADD COLUMN profile VARCHAR(50) DEFAULT 'vidhi'"))
            conn.execute(text("UPDATE food_entries SET profile = 'vidhi' WHERE profile IS NULL OR profile = ''"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_food_entries_profile_logged_at ON food_entries (profile, logged_at)"))

        if inspector.has_table("settings") and "profile" not in settings_columns:
            conn.execute(text("ALTER TABLE settings ADD COLUMN profile VARCHAR(50) DEFAULT 'vidhi'"))
            conn.execute(text("UPDATE settings SET profile = 'vidhi' WHERE profile IS NULL OR profile = ''"))
            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uq_settings_profile ON settings (profile)"))

        if not inspector.has_table("weight_entries"):
            conn.execute(text("""
                CREATE TABLE weight_entries (
                    id INTEGER PRIMARY KEY,
                    profile VARCHAR(50) DEFAULT 'vidhi',
                    weight_kg FLOAT NOT NULL,
                    logged_at DATETIME NOT NULL,
                    created_at DATETIME,
                    note VARCHAR(255)
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_weight_entries_logged_at ON weight_entries (logged_at)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_weight_entries_profile_logged_at ON weight_entries (profile, logged_at)"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    run_migrations()
    db = SessionLocal()
    try:
        for profile, goal in DEFAULT_PROFILES.items():
            existing = db.query(Settings).filter(Settings.profile == profile).first()
            if not existing:
                db.add(Settings(profile=profile, daily_calorie_goal=goal))
        db.commit()
    finally:
        db.close()
    yield


app = FastAPI(
    title="Calorie Tracker API",
    description="Profile-aware calorie tracking with food database integration",
    version="1.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PUBLIC_PATHS = {"/health", "/login", "/auth/login"}


@app.middleware("http")
async def require_login(request: Request, call_next):
    path = request.url.path
    public = path in PUBLIC_PATHS or path.startswith("/docs") and not auth_enabled()
    if auth_enabled() and not public and not request_is_authenticated(request):
        browser_page = path == "/" or path.startswith(("/chat", "/dashboard"))
        wants_html = "text/html" in request.headers.get("accept", "")
        if browser_page or wants_html and not path.startswith(("/agent", "/entries", "/weights", "/settings", "/deficit", "/foods")):
            return RedirectResponse(url="/login", status_code=303)
        return JSONResponse({"detail": "Authentication required"}, status_code=401)
    return await call_next(request)


app.include_router(settings.router)
app.include_router(entries.router)
app.include_router(deficit.router)
app.include_router(foods.router)
app.include_router(weights.router)
app.include_router(agent.router)
app.include_router(auth.router)

STATIC_ROOT = Path(__file__).resolve().parent / "static"
CHAT_ROOT = Path(__file__).resolve().parent / "chat_static"


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/chat/")


@app.get("/health")
def health_check():
    return {"status": "healthy", "profiles": list(DEFAULT_PROFILES.keys()), "features": ["calories", "weights"]}


app.mount("/dashboard", StaticFiles(directory=STATIC_ROOT, html=True), name="dashboard")
app.mount("/chat", StaticFiles(directory=CHAT_ROOT, html=True), name="chat")
