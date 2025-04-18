1. [Adventure](https://www.basicfantasy.org/srd/dungeonAdventures.html)
2. [11Wilderness Adventures](https://www.basicfantasy.org/srd/wildAdventures.html)

[Basic Fantasy RPG, 4th edition](https://www.basicfantasy.org/srd/)

[Toggle dark mode](https://www.basicfantasy.org/srd/wildAdventures.html "Toggle dark mode")

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

- [Wilderness Movement Rates](https://www.basicfantasy.org/srd/wildAdventures.html#wilderness-movement-rates)
- [Overland Travel](https://www.basicfantasy.org/srd/wildAdventures.html#overland-travel)
- [Becoming Lost](https://www.basicfantasy.org/srd/wildAdventures.html#becoming-lost)
- [Waterborne Travel](https://www.basicfantasy.org/srd/wildAdventures.html#waterborne-travel)
- [Traveling by Air](https://www.basicfantasy.org/srd/wildAdventures.html#traveling-by-air)

# 11Wilderness Adventures

### Wilderness Movement Rates [Anchor](https://www.basicfantasy.org/srd/wildAdventures.html\#wilderness-movement-rates)

Movement rates when traveling in the wilderness are related directly to encounter movement rates, as shown on the table below:

| Encounter Movement (Ft per Rnd) | Wilderness Movement (Mls per Day) |
| --- | --- |
| 10’ | 6 |
| 20’ | 12 |
| 30’ | 18 |
| 40’ | 24 |
| 50’ | 30 |
| 60’ | 36 |
| 70’ | 42 |
| 80’ | 48 |
| 90’ | 54 |
| 100’ | 60 |
| 110’ | 66 |
| 120’ | 72 |

Naturally, any group traveling together moves at the rate of the slowest member.

### Overland Travel [Anchor](https://www.basicfantasy.org/srd/wildAdventures.html\#overland-travel)

The movement rates shown on the table above are figured based on an 8 hour day of travel through open, clear terrain. The terrain type will alter the rate somewhat, as shown on this table:

| **Terrain** | **Adjustment** |
| --- | --- |
| Jungle, Mountains, Swamp | ×1/3 |
| Desert, Forest, Hills | ×2/3 |
| Clear, Plains, Trail | ×1 |
| Road (Paved) | ×1 1/3 |

Characters may choose to perform a **forced march**, traveling 12 hours per day. If this is done, add an additional 50% to the distance traveled. Each day of forced march performed after the first inflicts 1d6 damage on the characters (and their animals, if any). A save vs. Death Ray with Constitution bonus applied is allowed to avoid this damage, but after this save is failed once, it is not rolled again for that character or creature. A day spent resting “restarts” the progression.

### Becoming Lost [Anchor](https://www.basicfantasy.org/srd/wildAdventures.html\#becoming-lost)

Though adventurers following roads, rivers, or other obvious landmarks are unlikely to become lost, striking out into trackless forest, windblown desert, and so on is another matter. Secretly roll a save vs. Death Ray, adjusted by the Wisdom of the party leader (i.e., whichever character seems to be leading). An Ability Roll against Wisdom may be rolled, if that optional rule is in use. The GM must determine the effects of failure

### Waterborne Travel [Anchor](https://www.basicfantasy.org/srd/wildAdventures.html\#waterborne-travel)

Travel by water may be done in a variety of boats or ships; see the table in the [Vehicles](https://www.basicfantasy.org/srd/vehicles.html#water-transportation) section for details. Travel distances are based on a 12 hour day of travel, rather than the usual 8 hours per day given above. Note that sailed ships may travel 24 hours per day (if a qualified navigator is aboard), and so may be able to cover twice the normal distance per day of travel. This is in addition to the multiplier given below. If the ship stops each night, as is done by some vessels traveling along a coastline as well as those vessels having less than the minimum number of regular crewmen on board, the two-times multiplier does not apply.

Movement of sailed ships varies depending on weather conditions, as shown on the following table. **Sailing** movement modifiers shown apply when sailing with the wind; sailing against the wind involves **tacking** (called “zigzagging” by landlubbers) which reduces movement rates as indicated on the table.

```sourceCode javascript
import {generalTableSelect, highlightTableRow} from "./custom.js"

Inputs.button("Roll on Table", {value: 0, reduce: () => highlightTableRow("#wind-direction", generalTableSelect([1,12,0],[[1,1],[2,2],[3,3],[4,4],[5,5],[6,6],[7,7],[8,8],[9,12]]))})
```

```javascript hljs
  import {generalTableSelect as generalTableSelect, highlightTableRow as highlightTableRow} from "./custom.js"

```

Roll on Table

| **d12** | **Wind Direction** |
| --- | --- |
| 1 | Northerly |
| 2 | Northeasterly |
| 3 | Easterly |
| 4 | Southeasterly |
| 5 | Southerly |
| 6 | Southwesterly |
| 7 | Westerly |
| 8 | Northwesterly |
| 9-12 | Prevailing wind direction for this locale |

```sourceCode javascript
Inputs.button("Roll on Table", {value: 0, reduce: () => highlightTableRow("#wind-condition", generalTableSelect([1,100,0],[[1,5],[6,13],[14,25],[26,40],[41,70],[71,85],[86,96],[97,100]]))})
```

Roll on Table

| **d%** | **Wind Conditions** | **Sailing** | **Tacking** |
| --- | --- | --- | --- |
| 01-05 | Becalmed | x0 | x0 |
| 06-13 | Very Light Breeze | x1/3 | x0 |
| 14-25 | Light Breeze | x1/2 | x1/3 |
| 26-40 | Moderate Breeze | x2/3 | x1/3 |
| 41-70 | Average Winds | x1 | x1/2 |
| 71-85 | Strong Winds | x1 1/3 | x2/3 |
| 86-96 | Very Strong Winds | x1 1/2 | x0 |
| 97-00 | Gale | x2 | x0 |

**Notes:**

**Becalmed:** Sailing ships cannot move. Oared ships may move at the given rowing movement rate.

**Very Strong Winds:** Sailing against the wind (tacking) is not possible.

**Gale:** Sailing against the wind is not possible, and ships exposed to a gale may be damaged or sunk; apply 2d8 points of damage to any such ship, per hour sailed.

### Traveling by Air [Anchor](https://www.basicfantasy.org/srd/wildAdventures.html\#traveling-by-air)

When traveling by air, overland movement rates are doubled, and all terrain effects are ignored. Most winged creatures must maintain at least one-third normal forward movement in order to remain airborne; however, devices such as **flying carpets** generally do not have this limitation.

[10Dungeon Adventures](https://www.basicfantasy.org/srd/dungeonAdventures.html)

[12Hirelings](https://www.basicfantasy.org/srd/hirelings.html)