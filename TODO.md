# BFRPG MUD - TODO List

## Database Issues
- [x] Add `is_admin` column to users table
- [ ] Review other database schema issues (missing columns in areas table)
- [ ] Create proper database migrations with Alembic
- [ ] Ensure consistent SQLite schema between dev and production environments

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
- [ ] Implement inventory system
- [ ] Implement NPC interactions
- [ ] Implement combat system
- [ ] Add more areas and rooms
- [ ] Create web UI for game 