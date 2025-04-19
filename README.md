# BFRPG MUD - Basic Fantasy Role-Playing Game Multi-User Dungeon

A text-based multi-user dungeon (MUD) game based on the Basic Fantasy Role-Playing Game system.

## 🚀 Features

- **Character Creation**: Create and customize characters based on BFRPG rules
- **Text-based Exploration**: Navigate a fantasy world through text commands
- **Combat System**: Turn-based combat with dice rolls and BFRPG mechanics
- **Inventory Management**: Collect, equip, and manage items
- **Hireling System**: Recruit NPCs to join your adventure
- **Multi-User Experience**: Interact with other players in the game world

## 🛠️ Technology Stack

- **Backend**: Python (FastAPI), SQLAlchemy, Pydantic
- **Frontend**: JavaScript (vanilla), HTML/CSS
- **Database**: PostgreSQL (with SQLite fallback for development/testing)
- **Test Framework**: `pytest` with `httpx` for API tests
- **Infrastructure**: Docker, GitHub Actions (CI)

## 🔧 Setup & Installation

### Prerequisites

- Python 3.9+
- PostgreSQL (for production) or SQLite (for development)
- Node.js and npm (for frontend development)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/bfrpg_mud.git
   cd bfrpg_mud
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv env
   # On Windows:
   env\Scripts\activate
   # On Unix or MacOS:
   source env/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (or use the defaults in `.env`):
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

7. Access the application:
   - MUD UI: http://localhost:8000/
   - API documentation: http://localhost:8000/docs

### Running with Docker

```bash
docker-compose up -d
```

## 🧪 Testing

Run tests with pytest:

```bash
pytest
```

Run tests with coverage report:

```bash
pytest --cov=app
```

## 📚 Development Guidelines

### Code Style

- Follow **PEP8** for formatting
- Use **type hints** for all functions
- Group imports: stdlib → third-party → local

### Project Structure

- All endpoints in `/app/routes/`
- Models in `/app/models.py` or `/app/models/`
- DB config in `/app/database.py`
- Constants and enums in `/app/constants.py`

### Git Workflow

- Branch naming: `feature/`, `bugfix/`, `test/`, or `refactor/` prefix
- Commits: Present-tense, e.g. `Add journal endpoint`
- PRs must link to issues

## 📝 API Documentation

API documentation is available at `/docs` endpoint when the server is running.

## 📖 Game Documentation

- [Game Rules](docs/RULES.md)
- [Command Reference](docs/COMMANDS.md)
- [Character Guide](docs/CHARACTERS.md)

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Basic Fantasy Role-Playing Game (BFRPG) creators and community
- Contributors to the project
