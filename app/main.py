from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from dotenv import load_dotenv
import traceback
from app.database import get_db
from app.routers import auth, users, characters, items, combat, hirelings, commands
from app.websockets import WebSocketManager

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
app.include_router(commands.router, prefix="/api/commands", tags=["commands"])
app.include_router(commands.router, prefix="/api/game", tags=["game"])

# Add WebSocket connection endpoint
ws_manager = WebSocketManager(app)

# Create static directory if it doesn't exist
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
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

@app.get("/")
async def root(request: Request):
    """Serve the MUD UI or return API info based on Accept header"""
    # Check if the client accepts HTML
    accept_header = request.headers.get("accept", "")
    if "text/html" in accept_header:
        # Serve login HTML UI
        with open("static/login.html", "r") as f:
            return HTMLResponse(content=f.read())
    # Default to JSON response for API clients
    return {"message": "Welcome to BFRPG MUD API"}

@app.get("/index.html", response_class=HTMLResponse)
async def index_html():
    """Serve the MUD UI"""
    with open("static/index.html", "r") as f:
        return f.read()

@app.get("/login.html", response_class=HTMLResponse)
async def login():
    """Serve the login page"""
    with open("static/login.html", "r") as f:
        return f.read()

@app.get("/forgot-password.html", response_class=HTMLResponse)
async def forgot_password():
    """Serve the forgot password page"""
    with open("static/forgot-password.html", "r") as f:
        return f.read()

@app.get("/reset-password.html", response_class=HTMLResponse)
async def reset_password():
    """Serve the reset password page"""
    with open("static/reset-password.html", "r") as f:
        return f.read()

@app.get("/game.html", response_class=HTMLResponse)
async def game():
    """Serve the game UI"""
    with open("static/game.html", "r") as f:
        return f.read()

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
