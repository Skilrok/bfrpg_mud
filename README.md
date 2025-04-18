# BFRPG MUD

A text-based multiplayer dungeon roleplaying game built with FastAPI and a classic terminal-style UI.

## Current Status (April 2024)

- ✅ Authentication system with JWT tokens
- ✅ User account management
- ✅ Character system with races, classes, and abilities
- ✅ Terminal-style UI with retro effects
- ✅ Login and registration pages
- ✅ Basic game interface
- 🔄 Hireling system (in progress)
- 🔄 Inventory system (in progress)
- 🔄 WebSocket real-time communication (in progress)

## Next Steps

1. Implement game command API
2. Complete character creation interface
3. Implement WebSocket for real-time updates
4. Build basic room navigation system
5. Develop combat mechanics

## Features

- User account management
- Character creation and progression
- Room-based exploration
- Real-time chat system
- Turn-based combat
- Player journal system

## Setup

1. Create a virtual environment:
```bash
python -m venv env
```

2. Activate the virtual environment:
- Windows:
```bash
.\env\Scripts\activate
```
- Unix/MacOS:
```bash
source env/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
The game interface will be at `http://localhost:8000/static/login.html`

## API Documentation

Once the server is running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative API docs: `http://localhost:8000/redoc`

## Project Structure

```
bfrpg-mud/
├── env/                      # Virtual environment
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI entry point
│   ├── models.py             # SQLAlchemy models
│   ├── schemas.py            # Pydantic schemas
│   ├── database.py           # DB configuration
│   ├── utils.py              # Utility functions
│   └── routers/              # API endpoints
│       ├── auth.py           # Authentication
│       ├── users.py          # User management
│       ├── characters.py     # Character management
│       ├── items.py          # Item system
│       ├── hirelings.py      # Hireling system
│       └── websocket.py      # WebSocket communication
├── static/                   # Frontend assets
│   ├── login.html            # Login/register page
│   └── game.html             # Main game interface
├── tests/                    # Test suite
├── alembic/                  # Database migrations
├── docs/                     # Documentation
├── .env                      # Environment variables
├── requirements.txt          # Dependencies
└── README.md
```

## License

MIT 