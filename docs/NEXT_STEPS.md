# BFRPG MUD - Next Development Steps

This document outlines the immediate development tasks needed to make progress on the BFRPG MUD project.

## 1. Backend Development

### Priority 1: Game Command API
- [ ] Create the `/api/game/command` endpoint to process game commands
- [ ] Build a command router that handles different command types
- [ ] Implement basic commands:
  - [ ] `look` - View the current room
  - [ ] `inventory` - View character inventory
  - [ ] `stats` - View character stats
  - [ ] `help` - Show available commands
  - [ ] `go/move` - Basic movement commands

### Priority 2: Character Management
- [ ] Implement character creation endpoint
- [ ] Add character selection functionality
- [ ] Create character stat generation (according to BFRPG rules)
- [ ] Implement character progression/leveling

### Priority 3: Fix WebSocket Implementation
- [ ] Fix JWT import issue in websocket.py
- [ ] Implement proper event handling via WebSockets
- [ ] Add real-time updates for game events
- [ ] Create room-based message broadcasting

### Priority 4: Room System
- [ ] Design room database schema
- [ ] Implement room loading and state management
- [ ] Create connections between rooms
- [ ] Add room-based events and interactions

## 2. Frontend Development

### Priority 1: Character Creation Interface
- [ ] Create a character creation form
- [ ] Implement race and class selection
- [ ] Add ability score assignment interface
- [ ] Design character preview

### Priority 2: Game Command Interface Improvements
- [ ] Add command autocomplete
- [ ] Implement command history navigation
- [ ] Create formatted output for different command types
- [ ] Add visual indicators for game events

### Priority 3: Game State UI Elements
- [ ] Implement health/stat indicators
- [ ] Create inventory visualization
- [ ] Add mini-map for navigation
- [ ] Design status indicators for effects

## 3. Testing and Fixes

### Priority 1: Fix Test Suite
- [ ] Address failing tests in test_game_api_integration.py
- [ ] Fix SQLite thread issues in tests
- [ ] Implement proper test fixtures for UI testing
- [ ] Create mocks for WebSocket testing

### Priority 2: Database Fixes
- [ ] Ensure proper schema for all tables
- [ ] Fix ORM configuration issues
- [ ] Implement proper migrations for schema changes
- [ ] Ensure proper indexes for performance

## 4. Documentation

### Priority 1: API Documentation
- [ ] Document all endpoints in OpenAPI format
- [ ] Create usage examples for each endpoint
- [ ] Document WebSocket events and payload formats

### Priority 2: User Documentation
- [ ] Create a player guide
- [ ] Document available commands
- [ ] Write tutorials for new players

## 5. Deployment

### Priority 1: Local Development Environment
- [ ] Ensure consistent setup process works across platforms
- [ ] Document all dependencies
- [ ] Create development database seeding

### Priority 2: Prepare for Production
- [ ] Configure Docker setup
- [ ] Set up PostgreSQL for production
- [ ] Implement proper logging
- [ ] Configure environment variables for production 