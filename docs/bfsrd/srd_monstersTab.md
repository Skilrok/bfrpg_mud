1. [Monsters](https://www.basicfantasy.org/srd/monsters.html)
2. [17Monsters Index](https://www.basicfantasy.org/srd/monstersTab.html)

[Basic Fantasy RPG, 4th edition](https://www.basicfantasy.org/srd/)

[Toggle dark mode](https://www.basicfantasy.org/srd/monstersTab.html "Toggle dark mode")

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

# 17Monsters Index

Select search field(s). Hold `shift` or drag mouse to select multiple.

Monster name is always part of the search field.

```sourceCode javascript
data = {
  const d = await FileAttachment("monsters.json").json()
  return d
}
```

data = Array(251) \[Object, Object, Object, Object, Object, Object, Object, Object, Object, Object, Object, Object, Object, Object, Object, Object, Object, Object, Object, Object, …\]

```sourceCode javascript
cols = Object.keys(data[0])
cols2 = cols.slice(1)
```

cols = Array(11) \["Name", "Armor Class:", "Hit Dice:", "No. of Attacks:", "Damage:", "Movement:", "No. Appearing:", "Save As:", "Morale:", "Treasure Type:", "XP:"\]

cols2 = Array(10) \["Armor Class:", "Hit Dice:", "No. of Attacks:", "Damage:", "Movement:", "No. Appearing:", "Save As:", "Morale:", "Treasure Type:", "XP:"\]

```sourceCode javascript
viewof theseCols =  Inputs.select(cols2, {multiple:true, value:cols2})
```

Armor Class:Hit Dice:No. of Attacks:Damage:Movement:No. Appearing:Save As:Morale:Treasure Type:XP:

theseCols = Array(10) \["Armor Class:", "Hit Dice:", "No. of Attacks:", "Damage:", "Movement:", "No. Appearing:", "Save As:", "Morale:", "Treasure Type:", "XP:"\]

```sourceCode javascript
viewof search  = {
  let n = Inputs.search(data,{
  columns:[cols[0]].concat(theseCols)
});
return n
}
```

251 results

search = Array(251) \[Object, Object, Object, Object, Object, Object, Object, Object, Object, Object, Object, Object, Object, Object, Object, Object, Object, Object, Object, Object, …\]

```sourceCode javascript
// import { jQuery as $ } from "@ddspog/useful-libs"

Inputs.table(search, {width:"auto",
format:{
    Name: id => htl.html`<a href=#\ onclick="test('${id}')">${id}</a>`
}})
```

|  | Name | Armor Class: | Hit Dice: | No. of Attacks: | Damage: | Movement: | No. Appearing: | Save As: | Morale: | Treasure Type: | XP: |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | [Ant, Giant](https://www.basicfantasy.org/srd/monstersTab.html#\) | 17 | 4 | 1 bite | 2d6 | 60’ (10’) | 2d6, Lair 4d6 | Fighter: 4 | 7 on first sighting, 12 after engaged | U or special | 240 |
|  | [Ant, Huge](https://www.basicfantasy.org/srd/monstersTab.html#\) | 15 | 2 |  | 1d10 bite | 50’ | 3d6, Lair 4d8 | Fighter: 2 |  |  | 75 |
|  | [Ant, Large](https://www.basicfantasy.org/srd/monstersTab.html#\) | 13 | 1 |  | 1d6 bite | 40’ | 4d6, Lair 4d10 | Fighter: 1 |  |  | 25 |
|  | [Antelope](https://www.basicfantasy.org/srd/monstersTab.html#\) | 13 | 1 to 4 | 1 butt | 1d4 or 1d6 or 1d8 | 80’ (10’) | Wild 3d10 | Fighter: 1 to 4 (as Hit Dice) | 5 (7) | None | 25 - 240 |
|  | [Ape, Carnivorous](https://www.basicfantasy.org/srd/monstersTab.html#\) | 14 | 4 | 2 claws | 1d4/1d4 | 40’ | 1d6, Wild 2d4, Lair 2d4 | Fighter: 4 | 7 | None | 240 |
|  | [Assassin Vine](https://www.basicfantasy.org/srd/monstersTab.html#\) | 15 | 6 | 1 entangle + special | 1d8 + special | 5’ | 1d4+1 | Fighter: 6 | 12 | U | 500 |
|  | [Barkling](https://www.basicfantasy.org/srd/monstersTab.html#\) | 15 (11) | 1/2 (1d4 HP) | 1 bite or 1 weapon | 1d4 bite, or by weapon | 20’ Unarmored, 40’ | 3d4, Wild 4d6, Lair 5d10 | Normal Man | 7 (9) | P, Q each, C, K in Lair | 10 |
|  | [Basilisk, Common](https://www.basicfantasy.org/srd/monstersTab.html#\) | 16 | 6\*\* | 1 bite/1 gaze | 1d10/petrification | 20’ (10’) | 1d6, Wild 1d6, Lair 1d6 | Fighter: 6 | 9 | F | 610 |
|  | [Basilisk, Greater\*](https://www.basicfantasy.org/srd/monstersTab.html#\) | 17 | 8\*\*\* | 1 bite/ 1 gaze | 1d12 + poison, bite, petrification gaze | 20’ (10’) | 1 | Fighter: 8 | 10 | F, K | 1,085 |
|  | [Bat](https://www.basicfantasy.org/srd/monstersTab.html#\) | 14 | 1 Hit Point | 1 special | Confusion | 30’ Fly 40’ | 1d100, Wild 1d100, Lair 1d100 | Normal Man | 6 | None | 10 |
|  | [Giant Bat](https://www.basicfantasy.org/srd/monstersTab.html#\) | 14 | 2 | 1 bite | 1d4 | 10’ Fly 60’ (10’) | 1d10, Wild 1d10, Lair 1d10 | Fighter: 2 | 8 | None | 75 |
|  | [Bear, Black](https://www.basicfantasy.org/srd/monstersTab.html#\) | 14 | 4 | 2 claws/1 bite + hug | 1d4/1d4/1d6 + 2d6 hug | 40’ | 1d4, Wild 1d4, Lair 1d4 | Fighter: 4 | 7 | None | 240 |
|  | [Bear, Cave](https://www.basicfantasy.org/srd/monstersTab.html#\) | 15 | 7 | 2 claws/1 bite + hug | 1d8/1d8/2d6 + 2d8 hug | 40’ | 1d2, Wild 1d2, Lair 1d2 | Fighter: 7 | 9 | None | 670 |
|  | [Bear, Grizzly (or Brown)](https://www.basicfantasy.org/srd/monstersTab.html#\) | 14 | 5 | 2 claws/1 bite + hug | 1d4/1d4/1d8 + 2d8 hug | 40’ | 1, Wild 1d4, Lair 1d4 | Fighter: 5 | 8 | None | 360 |
|  | [Bear, Polar](https://www.basicfantasy.org/srd/monstersTab.html#\) | 14 | 6 | 2 claws/1 bite + hug | 1d6/1d6/1d10 + 2d8 hug | 40’ | 1, Wild 1d2, Lair 1d2 | Fighter: 6 | 8 | None | 500 |
|  | [Bee, Giant](https://www.basicfantasy.org/srd/monstersTab.html#\) | 13 | 1/2\* (1d4 HP)\* | 1 sting | 1d4 + poison | 10’ Fly 50’ | 1d6, Wild 1d6, Lair 5d6 | Fighter: 1 | 9 | Special | 13 |
|  | [Beetle, Giant Bombardier](https://www.basicfantasy.org/srd/monstersTab.html#\) | 16 | 2\* | 1 bite + special | 1d6 + special | 40’ | 1d8, Wild 2d6, Lair 2d6 | Fighter: 2 | 8 | None | 100 |
|  | [Beetle, Giant Fire](https://www.basicfantasy.org/srd/monstersTab.html#\) | 16 | 1+2 | 1 bite | 2d4 | 40’ | 1d8, Wild 2d6, Lair 2d6 | Fighter: 1 | 7 | None | 25 |
|  | [Beetle, Giant Oil](https://www.basicfantasy.org/srd/monstersTab.html#\) | 16 | 2 | 1 bite + spray (see below) | 2d4 bite, special spray | 40’ | 1d8, Wild 2d6, Lair 2d6 | Fighter: 2 | 8 | None | 100 |
|  | [Beetle, Giant Tiger](https://www.basicfantasy.org/srd/monstersTab.html#\) | 17 | 3+1 | 1 bite | 2d6 | 60’ (10’) | 1d6, Wild 2d4, Lair 2d4 | Fighter: 3 | 9 | U | 145 |
|  | [Black Pudding\*](https://www.basicfantasy.org/srd/monstersTab.html#\) | 14 | 10\* (+9) | 1 pseudopod | 3d8 | 20’ | 1 | Fighter: 10 | 12 | None | 1,390 |
|  | [Blink Dog](https://www.basicfantasy.org/srd/monstersTab.html#\) | 15 | 4\* | 1 bite | 1d6 | 40’ | 1d6, Wild 1d6, Lair 1d6 | Fighter: 4 | 6 | C | 280 |
|  | [Blood Rose](https://www.basicfantasy.org/srd/monstersTab.html#\) | 13 | 2\* to 4\* | 1 to 3 + blood drain | 1d6, 1d6/round blood drain | 1’ | Wild 1d8 | Fighter: 2 | 12 | None | 100 - 280 |

##### [Anchor](https://www.basicfantasy.org/srd/monstersTab.html\#exampleModalLabel)

...


Close

[16Monster Descriptions](https://www.basicfantasy.org/srd/monstersAll.html)

[18Treasure](https://www.basicfantasy.org/srd/treasure.html)