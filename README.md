# BFRPG MUD

A text-based multiplayer roleplaying game built with FastAPI.

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
│   └── routes/               # API endpoints
├── static/                   # Frontend assets
├── .env                      # Environment variables
├── requirements.txt          # Dependencies
└── README.md
```

## License

MIT 