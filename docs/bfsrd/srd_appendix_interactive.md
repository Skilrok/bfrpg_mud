1. [Appendix](https://www.basicfantasy.org/srd/appendix_interactive.html)
2. [22Interactive tools](https://www.basicfantasy.org/srd/appendix_interactive.html)

[Basic Fantasy RPG, 4th edition](https://www.basicfantasy.org/srd/)

[Toggle dark mode](https://www.basicfantasy.org/srd/appendix_interactive.html "Toggle dark mode")

- [Preface](https://www.basicfantasy.org/srd/)

- Introduction
  - [1Introduction](https://www.basicfantasy.org/srd/whatIsThis.html)
- Player Characters
  - [2Player Characters](https://www.basicfantasy.org/srd/char-creation.html)

  - [3Character Abilities](https://www.basicfantasy.org/srd/abilities.html)

  - [4Character Races](https://www.basicfantasy.org/srd/races.html)

  - [5Character Classes](https://www.basicfantasy.org/srd/class.html)

  - [6Equipment](https://www.basicfantasy.org/srd/equipment.html)

  - [7Vehicles](https://www.basicfantasy.org/srd/vehicles.html)
- Magic
  - [8Spells](https://www.basicfantasy.org/srd/spells.html)

  - [9Spells, Alphabetical](https://www.basicfantasy.org/srd/allSpells.html)
- Adventure
  - [10Dungeon Adventures](https://www.basicfantasy.org/srd/dungeonAdventures.html)

  - [11Wilderness Adventures](https://www.basicfantasy.org/srd/wildAdventures.html)

  - [12Hirelings](https://www.basicfantasy.org/srd/hirelings.html)

  - [13Advancement](https://www.basicfantasy.org/srd/advancement.html)
- Encounters
  - [14Combat Encounters](https://www.basicfantasy.org/srd/combat.html)
- Monsters
  - [15Monsters Intro](https://www.basicfantasy.org/srd/monsters.html)

  - [16Monster Descriptions](https://www.basicfantasy.org/srd/monstersAll.html)

  - [17Monsters Index](https://www.basicfantasy.org/srd/monstersTab.html)
- Treasure
  - [18Treasure](https://www.basicfantasy.org/srd/treasure.html)

  - [19Magic Items](https://www.basicfantasy.org/srd/magicItems.html)
- GM Information
  - [20Managing Encounters](https://www.basicfantasy.org/srd/gm01.html)

  - [21Crafting Adventures](https://www.basicfantasy.org/srd/gm02.html)
- Appendix
  - [22Interactive tools](https://www.basicfantasy.org/srd/appendix_interactive.html)

  - [23Dungeon Maker](https://www.basicfantasy.org/srd/appendixMapmaker.html)

  - [24Character Sheet](https://www.basicfantasy.org/srd/char_sheet.html)

## Table of contents

- [Character Generation Helpers](https://www.basicfantasy.org/srd/appendix_interactive.html#character-generation-helpers)
  - [Character Abilities](https://www.basicfantasy.org/srd/appendix_interactive.html#character-abilities)
  - [Starting Gold](https://www.basicfantasy.org/srd/appendix_interactive.html#starting-gold)
  - [Buy Equipment](https://www.basicfantasy.org/srd/appendix_interactive.html#buy-equipment)

# 22Interactive tools

## Character Generation Helpers [Anchor](https://www.basicfantasy.org/srd/appendix_interactive.html\#character-generation-helpers)

### Character Abilities [Anchor](https://www.basicfantasy.org/srd/appendix_interactive.html\#character-abilities)

```sourceCode javascript
import {generalDice, calculateModifier} from "./custom.js"

viewof statrolls = Inputs.button("Roll Statistics", {reduce: () => [generalDice(3,6,0),generalDice(3,6,0),generalDice(3,6,0),generalDice(3,6,0),generalDice(3,6,0),generalDice(3,6,0)]}

)
```

```javascript hljs
  import {generalDice as generalDice, calculateModifier as calculateModifier} from "./custom.js"

```

Roll Statistics

statrolls = 0

| Ability | Value | Modifier |
| --- | --- | --- |
| Strength |  | +3 |
| Intelligence |  | +3 |
| Wisdom |  | +3 |
| Dexterity |  | +3 |
| Constitution |  | +3 |
| Charisma |  | +3 |

### Starting Gold [Anchor](https://www.basicfantasy.org/srd/appendix_interactive.html\#starting-gold)

```sourceCode javascript
viewof goldRoll = Inputs.button("Roll Gold (3d6 x 10)", {value: 0, reduce: () => {
  let temp = (10 * generalDice(3,6,0));
  set (viewof startingGold, temp);
  return temp}})
```

Roll Gold (3d6 x 10)

goldRoll = 0

**Starting Gold**: 0

### Buy Equipment [Anchor](https://www.basicfantasy.org/srd/appendix_interactive.html\#buy-equipment)

```sourceCode javascript
import { convertToGold } from "./custom.js"

function set(input, value) {
  input.value = value;
  input.dispatchEvent(new Event("input", {bubbles: true}));
}

viewof startingGold = Inputs.text({label: "Starting Gold: "})

spent = {
  if (myarray.length != 0){
      let pricesGP = myarray.map(x => x[1].split(" ")).map(x => convertToGold(Number(x[0]), x[1]))
      let total = pricesGP.reduce ((x,y) => x + y)
      return total
  } else {return 0}
}

remainingGold = Number(startingGold) - spent
```

```javascript hljs
  import {convertToGold as convertToGold} from "./custom.js"

```

set = ƒ(input, value)

Starting Gold:

startingGold = ""

spent = 0

remainingGold = 0

**Remaining Gold**: 0.0 gp

Click to select. Use Ctrl (Cmd) or Shift to select multiple.

```sourceCode javascript
data = {
  const d = await FileAttachment("equipment.json").json()
  return d
}

miscs =  data[0].map( x => [x["Item"], x["Price"]] )
weapons = data[1].map( x => [x["Weapon"], x["Price"]])
armor = data[2].map( x => [x["Armor Type"], x["Price"]])
animals = data[3].map( x => [x["Item"], x["Price"]])
allItems = miscs.concat(weapons.concat(armor.concat(animals)))
```

data = Array(4) \[Array(46), Array(30), Array(5), Array(5)\]

miscs = Array(46) \[Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), …\]

weapons = Array(30) \[Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), …\]

armor = Array(5) \[Array(2), Array(2), Array(2), Array(2), Array(2)\]

animals = Array(5) \[Array(2), Array(2), Array(2), Array(2), Array(2)\]

allItems = Array(86) \[Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), …\]

```sourceCode javascript
viewof search  = {
  let n = Inputs.search(allItems);
return n
}
```

86 results

search = Array(86) \[Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), Array(2), …\]

```sourceCode javascript
viewof items = Inputs.select(search, {multiple: true
, format: (x) => `${x[0]},   (${x[1]})`
} )
miscPrice = items.map(x => x[1])

miscItems = items.map(x => x[0])
```

Backpack, (4 gp)Belt Pouch, (1 gp)Bit and bridle, (15 sp)Candles, 12, (1 gp)Chalk, small bag of pieces, (2 gp)Cloak, (2 gp)Clothing, common outfit, (4 gp)Glass bottle or vial, (1 gp)Grappling Hook, (2 gp)Holy Symbol, (25 gp)Holy Water, per vial, (10 gp)Horseshoes & shoeing, (1 gp)Ink, per jar, (8 gp)Iron Spikes, 12, (1 gp)Ladder, 10 ft., (1 gp)Lantern, (5 gp)Lantern, Bullseye, (14 gp)Lantern, Hooded, (8 gp)Manacles (without padlock), (6 gp)Map or scroll case, (1 gp)Mirror, small metal, (7 gp)Oil (per flask), (1 gp)Padlock (with 2 keys), (12 gp)Paper (per sheet), (1 gp)Pole, 10’ wooden, (1 gp)Quill, (1 sp)Quill Knife, (1 gp)Quiver or Bolt case, (1 gp)Rations, Dry, one week, (10 gp)Rope, Hemp (per 50 ft.), (1 gp)Rope, Silk (per 50 ft.), (10 gp)Sack, Large, (1 gp)Sack, Small, (5 sp)Saddle, Pack, (5 gp)Saddle, Riding, (10 gp)Saddlebags, pair, (4 gp)Spellbook (128 pages), (25 gp)Tent, Large (ten men), (25 gp)Tent, Small (one man), (5 gp)Thieves’ picks and tools, (25 gp)Tinderbox, flint and steel, (3 gp)Torches, 6, (1 gp)Whetstone, (1 gp)Whistle, (1 gp)Wineskin/Waterskin, (1 gp)Winter blanket, (1 gp)Hand Axe, (4 gp)Battle Axe, (7 gp)Great Axe, (14 gp)Shortbow, (25 gp)Shortbow Arrow, (1 sp)Silver† Shortbow Arrow, (2 gp)Longbow, (60 gp)Longbow Arrow, (2 sp)Silver† Longbow Arrow, (4 gp)Light Crossbow, (30 gp)Light Quarrel, (2 sp)Silver† Light Quarrel, (5 gp)Heavy Crossbow, (50 gp)Heavy Quarrel, (4 sp)Silver† Heavy Quarrel, (10 gp)Dagger, (2 gp)Silver† Dagger, (25 gp)Shortsword, (6 gp)Longsword/Scimitar, (10 gp)Two-Handed Sword, (18 gp)Warhammer, (4 gp)Mace, (6 gp)Maul, (10 gp)Club/Cudgel/Walking Staff, (2 sp)Quarterstaff, (2 gp)Pole Arm, (9 gp)Sling, (1 gp)Bullet, (1 sp)Stone, (0 gp)Spear, (5 gp)No Armor, (0 gp)Leather Armor, (20 gp)Chain Mail, (60 gp)Plate Mail, (300 gp)Shield, (7 gp)Horse, Draft, (120 gp)Horse, War, (200 gp)Horse, Riding, (75 gp)Pony\*, (40 gp)Pony, War\*, (80 gp)

items = Array(0) \[\]

miscPrice = Array(0) \[\]

miscItems = Array(0) \[\]

```sourceCode javascript
mutable myarray = []

viewof b = Inputs.button("add selected", {
    reduce: () => mutable myarray = [...mutable myarray].concat(items) })
```

mutable myarray = Mutable {}

myarray = Array(0) \[\]

add selected

b = 0

```sourceCode javascript
viewof inventory = Inputs.select(myarray, {multiple:true
, format: (x) => `${x[0]},   (${x[1]})`
})
```

inventory = Array(0) \[\]

```sourceCode javascript
viewof c = Inputs.button("remove selected", {
    reduce: () => mutable myarray = [...mutable myarray].filter(item => !inventory.includes(item)) })
```

remove selected

c = 0

[21Crafting Adventures](https://www.basicfantasy.org/srd/gm02.html)

[23Dungeon Maker](https://www.basicfantasy.org/srd/appendixMapmaker.html)