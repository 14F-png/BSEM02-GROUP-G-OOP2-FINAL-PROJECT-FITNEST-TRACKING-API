from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import engine, Base
from Router import auth_router, workouts, nutrition, progress, goals, admin
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FITTRACKER API SYSTEM",
    description="""

### Welcome To our FitTrackerAPI System
The FitNest Tracker API is a high-performance, secure backend application built to help users log workouts, monitor body metrics, and track their overall fitness journey over time.
Designed with a modular and scalable architecture, it provides a robust foundation for building modern web or mobile fitness applications.
### Tech Stack - Framework: FastAPI
** Database **: PostgreSQL + SQLAlchemy ORM- **Auth**: OAuth2 + JWT (python-jose) + bcrypt- **Docs**: Swagger UI (`/docs`) & ReDoc (`/redoc`)
""",
    version="1.0.0",
    contact={
        "name": "FitTrack Team",
        "email": "fittrack@limkokwing.edu.sl"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(workouts)
app.include_router(nutrition)
app.include_router(progress)
app.include_router(goals)
app.include_router(admin)

@app.get("/", tags=["Root"])
async def root():
    """Welcome endpoint — confirms the API is running."""
    return {
        "message": "Welcome to FitTrack API ",
        "docs": "/docs",
        "redoc": "/redoc",
        "version": "1.0.0",
        "sdg": "SDG 3 — Good Health and Well-Being",
    }
@app.get("/health", tags=["Root"])
async def health_check():
    """Health check endpoint for deployment monitoring."""
    return {"status": "healthy", "service": "FitTrack API"}

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Add this AFTER your routers
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/app", tags=["Root"])
async def serve_app():
    return FileResponse("FitTrackPro.html")