# BFRPG MUD - TODO List

## Database Issues

### Completed ✅
- Convert character inventory from JSON field to proper relationship table (CharacterItem)
- Fix hireling relationship to characters (rename master_id to character_id)
- Add AC bonus column to items table for shield items

### In Progress 🔄
- [ ] Review other database schema issues (missing columns in areas table)
- [ ] Create proper database migrations with Alembic
- [ ] Ensure consistent SQLite schema between dev and production environments

### Pending 📋
- [ ] Fix areas endpoints
- [ ] Fix rooms endpoints
- [ ] Fix characters endpoints
- [ ] Fix commands endpoints
- [ ] Document all API endpoints

## Authentication
- [x] Fix admin user creation
- [x] Test admin login
- [ ] Fix authentication for API endpoints (currently returning 401 Unauthorized)
- [ ] Implement `/api/users/me` endpoint

## Game Commands
- [x] Update movement commands to use Exit model
- [x] Fix "look" command to display exits from both models
- [ ] Fix command execution API endpoint authorization
- [ ] Test command execution through API

## API Endpoints
- [x] Fix character-hireling relationship endpoint (/api/characters/{character_id}/hirelings)
- [ ] Fix areas endpoints
- [ ] Fix rooms endpoints
- [ ] Fix characters endpoints
- [ ] Fix commands endpoints
- [ ] Document all API endpoints

## Testing
- [ ] Create integration tests for game commands
- [ ] Create tests for API endpoints
- [ ] Fix failing tests

## Deployment
- [ ] Create Docker container
- [ ] Set up CI/CD pipeline
- [ ] Create deployment documentation

## Future Features
- [x] Implement inventory system with proper database relationships
- [x] Implement AC bonus for shield items
- [ ] Implement NPC interactions
- [ ] Implement combat system
- [ ] Add more areas and rooms
- [ ] Create web UI for game

## Next Steps
1. Fix the room system's character location persistence issues
2. Complete the authentication system by resolving Pydantic model compatibility issues
3. Implement the remaining API endpoints
4. Add comprehensive test coverage
5. Complete documentation for all endpoints and systems
