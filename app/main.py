from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import students, ai


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables are created in SQLite database upon startup
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Students Database CRUD Application",
    description=(
        "Backend API built with FastAPI and SQLite for managing student records "
        "(Create, Read, Update, Delete) with an optional Ollama AI natural language extension.\n\n"
        "Developed for EWB Edu Tech Pvt. Ltd. Internship Project Assignment."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend integrations or testing tools
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(students.router)
app.include_router(ai.router)


@app.get("/", tags=["System"])
def root():
    return {
        "project": "Students Database CRUD Application",
        "organization": "EWB Edu Tech Pvt. Ltd.",
        "status": "online",
        "documentation": "/docs",
        "endpoints": {
            "students": "/students",
            "ai_query": "/ai/query",
            "ai_status": "/ai/status"
        }
    }


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy"}
