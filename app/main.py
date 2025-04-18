from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from dotenv import load_dotenv
import traceback
from app.database import get_db
from app.routers import auth, users, characters, items, combat, hirelings, websocket

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
app.include_router(websocket.router, tags=["websocket"])

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the MUD UI"""
    with open("static/index.html", "r") as f:
        return f.read()


@app.get("/api")
async def api_root():
    """API root endpoint"""
    return {"message": "Welcome to BFRPG MUD API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/debug")
async def debug_info(db=Depends(get_db)):
    """
    Debug endpoint to check if database connection is working
    and to see what tables exist in the database
    """
    try:
        # Try to query the User model to see if the table exists
        from app.models import User
        user_count = db.query(User).count()
        
        # Get a list of all tables in the database
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        
        # Get column info for users table
        users_columns = inspector.get_columns("users")
        users_column_info = [{"name": col["name"], "type": str(col["type"])} for col in users_columns]
        
        # Get column info for characters table
        characters_columns = inspector.get_columns("characters")
        characters_column_info = [{"name": col["name"], "type": str(col["type"])} for col in characters_columns]
        
        return {
            "database_connection": "working",
            "tables": tables,
            "user_count": user_count,
            "users_columns": users_column_info,
            "characters_columns": characters_column_info
        }
    except Exception as e:
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    uvicorn.run("app.main:app", host=host, port=port, reload=debug)
