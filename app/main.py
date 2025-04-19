import logging
import os
import traceback

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.config import configure_app_from_env
from app.database import get_db, init_db
from app.routers import auth, characters, combat, commands, hirelings, items, users
from app.routers import areas, exits, rooms
from app.websockets import WebSocketManager

logger = logging.getLogger(__name__)

# Load environment variables and configure the app
settings = configure_app_from_env()

# Create FastAPI app
app = FastAPI(
    title="BFRPG MUD API",
    description="Basic Fantasy RPG Multi-User Dungeon",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
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
app.include_router(commands.router, prefix="/api/commands", tags=["commands"])
app.include_router(areas.router, prefix="/api/areas", tags=["areas"])
app.include_router(rooms.router, prefix="/api/rooms", tags=["rooms"])
app.include_router(exits.router, prefix="/api/exits", tags=["exits"])

# Add WebSocket connection endpoint
ws_manager = WebSocketManager(app)

# Create static directory if it doesn't exist
static_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static"
)
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

# Create CSS directory if it doesn't exist
css_dir = os.path.join(static_dir, "css")
if not os.path.exists(css_dir):
    os.makedirs(css_dir)

# Create JS directory if it doesn't exist
js_dir = os.path.join(static_dir, "js")
if not os.path.exists(js_dir):
    os.makedirs(js_dir)

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")
# Mount CSS and JS directly for correct path resolution
app.mount("/css", StaticFiles(directory=css_dir), name="css")
app.mount("/js", StaticFiles(directory=js_dir), name="js")


# Startup event to initialize the database
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Initializing application...")
    await init_db()
    logger.info("Application initialized successfully")


@app.get("/")
async def root(request: Request):
    """Serve the MUD UI or return API info based on Accept header"""
    # Check if the client accepts HTML
    accept_header = request.headers.get("accept", "")
    if "text/html" in accept_header:
        # Serve login HTML UI
        try:
            with open(os.path.join(static_dir, "login.html"), "r") as f:
                return HTMLResponse(content=f.read())
        except FileNotFoundError:
            logger.error("login.html not found in static directory")
            return {"message": "Welcome to BFRPG MUD API (UI files not found)"}
    # Default to JSON response for API clients
    return {"message": "Welcome to BFRPG MUD API"}


@app.get("/index.html", response_class=HTMLResponse)
async def index_html():
    """Serve the MUD UI"""
    try:
        with open(os.path.join(static_dir, "index.html"), "r") as f:
            return f.read()
    except FileNotFoundError:
        logger.error("index.html not found in static directory")
        raise HTTPException(status_code=404, detail="UI file not found")


@app.get("/login.html", response_class=HTMLResponse)
async def login():
    """Serve the login page"""
    try:
        with open(os.path.join(static_dir, "login.html"), "r") as f:
            return f.read()
    except FileNotFoundError:
        logger.error("login.html not found in static directory")
        raise HTTPException(status_code=404, detail="Login page not found")


@app.get("/forgot-password.html", response_class=HTMLResponse)
async def forgot_password():
    """Serve the forgot password page"""
    try:
        with open(os.path.join(static_dir, "forgot-password.html"), "r") as f:
            return f.read()
    except FileNotFoundError:
        logger.error("forgot-password.html not found in static directory")
        raise HTTPException(status_code=404, detail="Forgot password page not found")


@app.get("/reset-password.html", response_class=HTMLResponse)
async def reset_password():
    """Serve the reset password page"""
    try:
        with open(os.path.join(static_dir, "reset-password.html"), "r") as f:
            return f.read()
    except FileNotFoundError:
        logger.error("reset-password.html not found in static directory")
        raise HTTPException(status_code=404, detail="Reset password page not found")


@app.get("/game.html", response_class=HTMLResponse)
async def game():
    """Serve the game UI"""
    try:
        with open(os.path.join(static_dir, "game.html"), "r") as f:
            return f.read()
    except FileNotFoundError:
        logger.error("game.html not found in static directory")
        raise HTTPException(status_code=404, detail="Game UI not found")


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "environment": settings.ENVIRONMENT}


@app.get("/debug")
async def debug_info(db=Depends(get_db)):
    """
    Debug endpoint to check if database connection is working
    and to see what tables exist in the database
    """
    # Only allow in development mode
    if settings.ENVIRONMENT != "development":
        raise HTTPException(
            status_code=403, detail="Debug endpoint only available in development mode"
        )

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
        users_column_info = [
            {"name": col["name"], "type": str(col["type"])} for col in users_columns
        ]

        # Get column info for characters table
        characters_columns = inspector.get_columns("characters")
        characters_column_info = [
            {"name": col["name"], "type": str(col["type"])}
            for col in characters_columns
        ]

        return {
            "database_connection": "working",
            "tables": tables,
            "user_count": user_count,
            "users_columns": users_column_info,
            "characters_columns": characters_column_info,
        }
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}


if __name__ == "__main__":
    import uvicorn

    # Use settings from configuration
    host = settings.HOST
    port = settings.PORT
    reload = settings.RELOAD if settings.ENVIRONMENT == "development" else False

    logger.info(f"Starting server on {host}:{port} (reload={reload})")
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)
