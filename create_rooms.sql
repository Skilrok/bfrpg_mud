-- Create areas table if it doesn't exist
CREATE TABLE IF NOT EXISTS areas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    level_range TEXT,
    is_dungeon BOOLEAN DEFAULT 1,
    is_hidden BOOLEAN DEFAULT 0,
    properties TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create rooms table if it doesn't exist
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    room_type TEXT DEFAULT 'dungeon',
    area_id INTEGER REFERENCES areas(id),
    x INTEGER DEFAULT 0,
    y INTEGER DEFAULT 0,
    z INTEGER DEFAULT 0,
    is_dark BOOLEAN DEFAULT 0,
    exits TEXT DEFAULT '{}',
    properties TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create exits table if it doesn't exist
CREATE TABLE IF NOT EXISTS exits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    direction TEXT NOT NULL,
    name TEXT,
    description TEXT,
    source_room_id INTEGER NOT NULL REFERENCES rooms(id),
    destination_room_id INTEGER NOT NULL REFERENCES rooms(id),
    is_hidden BOOLEAN DEFAULT 0,
    is_locked BOOLEAN DEFAULT 0,
    properties TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_room_id, direction)
);

-- Create character_locations table if it doesn't exist
CREATE TABLE IF NOT EXISTS character_locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER UNIQUE REFERENCES characters(id),
    room_id INTEGER REFERENCES rooms(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the Starting Village area if it doesn't exist
INSERT OR IGNORE INTO areas (id, name, description, level_range, is_dungeon, is_hidden)
VALUES (1, 'Starting Village', 'A small village where new adventurers begin their journey.', '1-3', 0, 0);

-- Insert basic rooms if they don't exist
-- Village Square (Room 1)
INSERT OR IGNORE INTO rooms (id, name, description, room_type, area_id, x, y, z, is_dark)
VALUES (1, 'Village Square', 'The central square of the starting village. Paths lead in all directions. A tavern stands to the north, a market to the east, a blacksmith to the south, and a temple to the west.', 'town', 1, 0, 0, 0, 0);

-- Tavern (Room 2)
INSERT OR IGNORE INTO rooms (id, name, description, room_type, area_id, x, y, z, is_dark)
VALUES (2, 'Village Tavern', 'A cozy tavern with a roaring fireplace. Adventurers gather here to share tales and find work. The bartender nods at you as you enter.', 'town', 1, 0, 1, 0, 0);

-- Market (Room 3)
INSERT OR IGNORE INTO rooms (id, name, description, room_type, area_id, x, y, z, is_dark)
VALUES (3, 'Village Market', 'A bustling market with various stalls selling goods. Merchants call out to passersby, hawking their wares.', 'town', 1, 1, 0, 0, 0);

-- Blacksmith (Room 4)
INSERT OR IGNORE INTO rooms (id, name, description, room_type, area_id, x, y, z, is_dark)
VALUES (4, 'Village Blacksmith', 'The sound of hammering fills the air as the blacksmith works at the forge. Weapons and armor are displayed on the walls.', 'town', 1, 0, -1, 0, 0);

-- Temple (Room 5)
INSERT OR IGNORE INTO rooms (id, name, description, room_type, area_id, x, y, z, is_dark)
VALUES (5, 'Village Temple', 'A peaceful temple dedicated to various deities. Candles flicker in the dim interior, and a priest stands ready to offer healing and blessings.', 'town', 1, -1, 0, 0, 0);

-- Add exits between rooms
-- From Village Square (Room 1) to other rooms
INSERT OR IGNORE INTO exits (direction, name, description, source_room_id, destination_room_id)
VALUES ('north', 'Tavern Entrance', 'The door to the village tavern.', 1, 2);

INSERT OR IGNORE INTO exits (direction, name, description, source_room_id, destination_room_id)
VALUES ('east', 'Market Street', 'A path leading to the village market.', 1, 3);

INSERT OR IGNORE INTO exits (direction, name, description, source_room_id, destination_room_id)
VALUES ('south', 'Smithy Road', 'A path leading to the village blacksmith.', 1, 4);

INSERT OR IGNORE INTO exits (direction, name, description, source_room_id, destination_room_id)
VALUES ('west', 'Temple Path', 'A serene path leading to the village temple.', 1, 5);

-- Return paths back to Village Square (Room 1)
INSERT OR IGNORE INTO exits (direction, name, description, source_room_id, destination_room_id)
VALUES ('south', 'Exit to Village Square', 'The door leading back to the village square.', 2, 1);

INSERT OR IGNORE INTO exits (direction, name, description, source_room_id, destination_room_id)
VALUES ('west', 'Back to Village Square', 'The path leading back to the village square.', 3, 1);

INSERT OR IGNORE INTO exits (direction, name, description, source_room_id, destination_room_id)
VALUES ('north', 'Back to Village Square', 'The path leading back to the village square.', 4, 1);

INSERT OR IGNORE INTO exits (direction, name, description, source_room_id, destination_room_id)
VALUES ('east', 'Back to Village Square', 'The path leading back to the village square.', 5, 1);
