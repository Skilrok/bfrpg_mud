# Inventory System Documentation

The BFRPG MUD inventory system allows characters to manage items, equip gear, and interact with objects in the game. This document provides an overview of the system and how to use it.

## Item Model

Items in the game are represented by the `Item` model with the following attributes:

- `id`: Unique identifier
- `name`: Display name of the item
- `description`: Text description
- `item_type`: Type of item (weapon, armor, potion, etc.)
- `value`: Value in gold pieces
- `weight`: Weight in pounds
- `properties`: JSON field for item-specific properties

## Item Types

The system supports various item types:

- `WEAPON`: Offensive items (swords, bows, daggers)
- `ARMOR`: Protective gear (leather, chainmail, plate)
- `SHIELD`: Defensive items held in the off-hand
- `POTION`: Consumable magic concoctions
- `SCROLL`: Single-use magic spells
- `WAND`: Magic items with charges
- `RING`: Magical jewelry
- `AMMUNITION`: Arrows, bolts, stones
- `TOOL`: Utility items (thieves' tools, rope)
- `CONTAINER`: Storage items (backpack, pouch)
- `CLOTHING`: Wearable items (cloak, boots)
- `FOOD`: Consumable nourishment
- `MISCELLANEOUS`: Various other items

## Character Inventory

Each character has an `inventory` field which is a JSON object structured as:

```json
{
  "item_id_1": {
    "item_id": 1,
    "quantity": 3,
    "equipped": false,
    "slot": null
  },
  "item_id_2": {
    "item_id": 2,
    "quantity": 1,
    "equipped": true,
    "slot": "main_hand"
  }
}
```

The keys are string representations of item IDs, and the values contain:

- `item_id`: Integer ID of the item
- `quantity`: Number of this item owned
- `equipped`: Whether the item is currently equipped
- `slot`: Which equipment slot the item occupies (if equipped)

## Character Equipment

Each character has an `equipment` field which is a JSON object mapping slots to item IDs:

```json
{
  "main_hand": 2,
  "body": 5,
  "off_hand": 8
}
```

## Equipment Slots

The system supports the following equipment slots:

- `main_hand`: Primary weapon/item
- `off_hand`: Shield or secondary weapon
- `body`: Armor
- `head`: Helmets, hats
- `hands`: Gloves
- `feet`: Boots
- `ring_1`: First ring
- `ring_2`: Second ring
- `neck`: Amulets, necklaces
- `back`: Cloaks
- `waist`: Belts
- `ammo`: Ammunition

## API Endpoints

### Items

- `GET /api/items/`: List all items
- `GET /api/items/{item_id}`: Get details for a specific item
- `POST /api/items/`: Create a new item
- `PUT /api/items/{item_id}`: Update an item
- `DELETE /api/items/{item_id}`: Delete an item

### Inventory Management

- `POST /api/items/inventory/{character_id}/add`: Add an item to inventory
- `POST /api/items/inventory/{character_id}/remove`: Remove an item from inventory
- `GET /api/items/inventory/{character_id}`: Get character's inventory
- `POST /api/items/inventory/{character_id}/equip`: Equip an item
- `POST /api/items/inventory/{character_id}/unequip`: Unequip an item

## Starting Equipment

When a character is created, they automatically receive starting equipment based on their class:

### Common Items (All Classes)
- Backpack
- Rations (5 days)
- Torches (3)
- Pouch

### Class-Specific Starting Equipment

**Fighter**
- Longsword
- Chain Mail
- Wooden Shield

**Cleric**
- Warhammer
- Chain Mail
- Wooden Shield

**Magic-User**
- Dagger
- Staff
- Leather Armor

**Thief**
- Shortsword
- Leather Armor
- Thieves' Tools

**Fighter/Magic-User (Elf)**
- Longsword
- Leather Armor
- Shortbow
- Arrows (20)

**Magic-User/Thief (Elf)**
- Dagger
- Thieves' Tools
- Leather Armor

## Item Properties

Item properties are stored in a flexible JSON field, allowing for different properties based on item type:

### Weapons
```json
{
  "damage": "1d8",
  "damage_type": "slashing",
  "range": "melee",
  "hands": 1
}
```

### Armor
```json
{
  "base_ac": 14,
  "dex_bonus": true,
  "max_dex_bonus": 2,
  "type": "medium"
}
```

### Potions
```json
{
  "effect": "healing",
  "healing": "1d8+2"
}
```

## Weight Management

Items have weight, and characters have a carrying capacity based on their Strength score. This affects movement speed and causes encumbrance penalties when carrying too much.

## Usage Examples

### Adding an Item to Inventory

```http
POST /api/items/inventory/1/add
{
  "item_id": 5,
  "quantity": 2
}
```

### Equipping an Item

```http
POST /api/items/inventory/1/equip
{
  "item_id": 5,
  "slot": "main_hand"
}
```

### Checking Detailed Inventory

```http
GET /api/items/inventory/1?include_details=true
``` 