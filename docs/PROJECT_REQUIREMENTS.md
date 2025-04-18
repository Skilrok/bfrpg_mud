# 📜 Project Requirements Document
**Project Title:** BFRPG MUD  
**Created by:** [Your Name]  
**Last updated:** 2025-04-17  

---

## 1. 🧭 Vision Statement

This project seeks to revive the classic feel of text-based dungeon exploration games with a strict rules-based implementation of the Basic Fantasy RPG (BFRPG) system. Over time, it will evolve to include an expansive overworld map, handcrafted and procedural content, and immersive player features while preserving the structure and tone of early online RPGs.

---

## 2. 🎯 Target Audience

- Fans of classic MUDs and early online RPGs
- Players who enjoy dice-based mechanics and strict rule systems
- Gamers seeking collaborative exploration and roleplay in a minimal text interface
- Dungeons & Dragons enthusiasts, particularly those drawn to the Basic or OSR styles

---

## 3. ⚔️ Gameplay & Mechanics

### Rules System
- Based on **Basic Fantasy RPG (BFRPG)** core rules only
- Strict rule adherence for combat, spells, saves, etc.

### Game Flow
- **Real-time exploration**
- **Turn-based encounters** (combat, events, etc.)

### Supported Commands (initial)
- `move`, `cast`, `attack`, `talk`, `search`, `touch`, `grab`, `look`, `taste`
- Commands must be **extensible** via backend logic

### Classes & Races
- Only core BFRPG classes and races at launch

### Character Persistence
- User accounts with multiple characters
- One character = one account (exclusive relationship)
- Saved state includes: stats, inventory, XP, quest progress, location, death status

### Party System
- Group size: max 5 players
- Groups share XP and loot
- No friendly fire within group
- PvP allowed outside of groups

---

## 4. 🌍 Game World & Content

### World Layout
- Modular, handcrafted dungeons and overworld maps
- **25x25 tile grid per dungeon level**
- Players must map manually (no visual in-game maps)

### Content Types
- Hand-crafted maps, room descriptions, encounters
- Procedural elements (e.g., migrating monsters, environmental changes)
- AI-assisted content generation via external tools

### Content Sources
- Start with Basic Fantasy modules (e.g., *Morgansfort*, *Chaotic Caves*)
- Gradually expand to include homebrew

---

## 5. 🧑‍🤝‍🧑 Multiplayer Features

- Shared rooms enable local chat
- PvP and group PvE interactions
- Future party system: shared commands (e.g. `follow`, `assist`, `group say`)

---

## 6. 💾 Data & Persistence

### Data Stored
- Characters (alive & dead)
- Accounts and login info
- World state (including monster corpses, dungeon resets)
- Inventories, journals, and quest flags

### Journaling
- Players can `record in my journal` and `read my journal`
- Text is persistent and character-bound
- No formatting or markdown required

---

## 7. 🧰 Technical Stack

| Layer | Stack |
|-------|-------|
| Frontend | HTML / JavaScript |
| Backend | Python (FastAPI or Flask) |
| Database | SQLite for dev; PostgreSQL for production |
| Hosting | Cloud deployment (e.g., Render, Railway, DigitalOcean) |
| Real-Time | WebSockets (for chat and async game actions) |

---

## 8. 📈 Growth & Stretch Goals

### Short-Term
- Party system (co-op mechanics)
- Merchant economy (buy/sell, inventories)
- Journal system for player notes

### Long-Term
- Crafting system (alchemy, smithing)
- World events and quests
- Overland map with biome-specific encounters

---

## 9. 🧠 AI & Procedural Integration

- AI used during worldbuilding to generate:
  - Room flavor text
  - Random encounters
  - NPC dialogue and names
- No AI integration in real-time gameplay or decision-making

---

## 10. 📝 Notes & Assumptions

- Combat resolution must be deterministic and based strictly on BFRPG rules
- Mapping is intended to be external (paper or third-party tool)
- AI tools (like ChatGPT or Cursor) are permitted for development, not gameplay 

---

## 11. 🖥️ UI Design & Interface

### Overall Philosophy
- **Text-first approach**: Minimal graphics, focus on rich text descriptions
- **Command-line interface**: Primary interaction via text commands
- **Accessibility**: Interface should be usable with screen readers

### Interface Components
1. **Command Input**
   - Text input field at bottom of screen
   - Command history accessible via up/down arrows
   - Tab completion for common commands and targets

2. **Main Output Window**
   - Scrollable text area showing game responses
   - Color-coded text for different types of information
   - Timestamps for important events

3. **Status Panels**
   - Character stats (name, HP, attributes) in collapsible sidebar
   - Inventory summary showing equipped items
   - Party member status when in a group

4. **Minimalist Visual Elements**
   - Simple ASCII/Unicode art for critical scenes or maps
   - Color-coded text for different message types:
     - System messages (gray)
     - Combat (red)
     - Loot/items (green)
     - Environment descriptions (blue)
     - Chat (white)

### Layout
- Single-page application with responsive design
- Mobile-friendly with collapsible panels
- 80% screen space dedicated to main text output
- Dark mode by default with high-contrast option

### Technical Implementation
- Pure HTML/CSS for layout and styling
- JavaScript for dynamic content and WebSocket handling
- No heavy frameworks required
- Local storage for settings and command history

### Accessibility Features
- Keyboard shortcuts for all common actions
- Screen reader compatibility
- Configurable text size and contrast
- Optional sound cues for important events

### Future UI Enhancements
- Optional simple tile representation of nearby rooms
- Customizable themes
- Exportable character sheets
- Simple dice visualization for combat rolls 