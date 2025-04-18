from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from app.database import get_db
from app.routers import auth, users, characters, items, combat, hirelings

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="BFRPG MUD API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(characters.router, prefix="/api/characters", tags=["characters"])
app.include_router(items.router, prefix="/api/items", tags=["items"])
app.include_router(combat.router, prefix="/api/combat", tags=["combat"])
app.include_router(hirelings.router, prefix="/api/hirelings", tags=["hirelings"])


@app.get("/")
async def root():
    return {"message": "Welcome to BFRPG MUD API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    uvicorn.run("app.main:app", host=host, port=port, reload=debug)
