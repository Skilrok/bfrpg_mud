# 🧱 BFRPG MUD UI Wireframe (Text-Based Layout)

```
+----------------------------------------------------------------------------------+
|                                  BFRPG MUD                                       |
|----------------------------------------------------------------------------------|
| [HP: 10/10] [XP: 0] [Level: 1] [Class: Fighter]     [Location: Dungeon Level 1] |
|----------------------------------------------------------------------------------|
| ROOM: The Goblin Watchpost                                                       |
|----------------------------------------------------------------------------------|
| The walls are rough-cut stone, damp and smelling of mildew. A narrow passage    |
| leads north, while a broken door gapes to the east. You see a pile of bones, a  |
| rusty dagger, and the twisted remains of a goblin sentry.                       |
|----------------------------------------------------------------------------------|
| Goblin Corpse: Decaying                                                          |
| Rusty Dagger: Can be grabbed                                                     |
| Exits: North, East                                                               |
|----------------------------------------------------------------------------------|
| > look dagger                                                                    |
| The dagger is heavily corroded but might still be useful.                       |
|----------------------------------------------------------------------------------|
| PLAYER CHAT:                                                                     |
| [Torma]: Anyone check the bones yet?                                             |
| [Elrik]: I'm grabbing the dagger                                                 |
| [You]: Anyone want to go east?                                                   |
|----------------------------------------------------------------------------------|
| JOURNAL: (Hidden - type 'read my journal' to open)                               |
|----------------------------------------------------------------------------------|
| >                                                                 (Command Line) |
|                                                                                  |
|   [↑ / ↓ for command history]    [TAB for autocomplete]   [Type 'help']          |
+----------------------------------------------------------------------------------+
```

---

## 🗂️ Interface Zones Explained

| Zone | Description |
|------|-------------|
| **Header Bar** | Game title and status stats (HP, XP, class, level, location) |
| **Room Title** | Bold identifier for the current location |
| **Room Description** | Flavor text describing the area |
| **Interactive Elements** | Highlighted exits, objects, corpses, items |
| **Command Feedback** | Where your recent actions/results appear |
| **Chat Panel** | Room-scoped chat when other players are present |
| **Journal Viewer** | Hidden by default; toggled with `read my journal` |
| **Command Line** | Where players type actions; supports history/autocomplete |

---

## 💡 Future Enhancements

- Toggle visibility of UI components (e.g., `:status`, `:journal`)
- Scrollback support for history
- Real-time message fade-in
- Dark mode / high-contrast toggle
- Tabbed journal entries or quest logs 