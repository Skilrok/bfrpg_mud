1. [Player Characters](https://www.basicfantasy.org/srd/char-creation.html)
2. [6Equipment](https://www.basicfantasy.org/srd/equipment.html)

[Basic Fantasy RPG, 4th edition](https://www.basicfantasy.org/srd/)

[Toggle dark mode](https://www.basicfantasy.org/srd/equipment.html "Toggle dark mode")

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

- [Money](https://www.basicfantasy.org/srd/equipment.html#money)
- [Misc. Equipment](https://www.basicfantasy.org/srd/equipment.html#misc.-equipment)
  - [Equipment Explanations](https://www.basicfantasy.org/srd/equipment.html#equipment-explanations)
- [Weapons](https://www.basicfantasy.org/srd/equipment.html#weapons)
- [Weapon Size](https://www.basicfantasy.org/srd/equipment.html#weapon-size)
- [Missile Weapon Ranges](https://www.basicfantasy.org/srd/equipment.html#missile-weapon-ranges)
- [Armor and Shields](https://www.basicfantasy.org/srd/equipment.html#armor-and-shields)
- [Beasts of Burden](https://www.basicfantasy.org/srd/equipment.html#beasts-of-burden)

# 6Equipment

## Money [Anchor](https://www.basicfantasy.org/srd/equipment.html\#money)

Monetary values are usually expressed in gold pieces. In addition to gold coins, there are coins made of platinum, silver, electrum (an alloy of gold and silver), and copper. They are valued as follows:

1 platinum piece (pp)= 5 gold pieces (gp)

1 gold piece (gp)= 10 silver pieces (sp)

1 electrum piece (ep)= 5 silver pieces (sp)

1 silver piece (sp)= 10 copper pieces (cp)

For game purposes, assume that one gold piece weighs 1/10th of a pound, and that five coins will “fit” in a cubic inch of storage space (this isn’t literally accurate, but works well enough when applied to a box or chest).

First level characters generally begin the game with 3d6 x 10 gp (unless the GM decides otherwise).

```sourceCode javascript
import { generalDice } from "./custom.js"

viewof goldRoll = Inputs.button("Roll Starting Gold", {value: 0, reduce: () => (10 * generalDice(3,6,0))})
```

```javascript hljs
  import {generalDice as generalDice} from "./custom.js"

```

Roll Starting Gold

goldRoll = 0

**Starting Gold**: 0

## Misc. Equipment [Anchor](https://www.basicfantasy.org/srd/equipment.html\#misc.-equipment)

This list represents common adventuring equipment at average prices. Prices and availability may vary. Weights are expressed in pounds. Items marked \* weigh very little; ten such items weigh one pound. Items marked \*\* have almost no weight and should not usually be counted.

| Item | Price | Weight |
| --- | --- | --- |
| Backpack | 4 gp | \* |
| Belt Pouch | 1 gp | \* |
| Bit and bridle | 15 sp | 3 |
| Candles, 12 | 1 gp | \* |
| Chalk, small bag of pieces | 2 gp | \* |
| Cloak | 2 gp | 1 |
| Clothing, common outfit | 4 gp | 1 |
| Glass bottle or vial | 1 gp | \* |
| Grappling Hook | 2 gp | 4 |
| Holy Symbol | 25 gp | \* |
| Holy Water, per vial | 10 gp | \* |
| Horseshoes & shoeing | 1 gp | 10 |
| Ink, per jar | 8 gp | ½ |
| Iron Spikes, 12 | 1 gp | 1 |
| Ladder, 10 ft. | 1 gp | 20 |
| Lantern | 5 gp | 2 |
| Lantern, Bullseye | 14 gp | 3 |
| Lantern, Hooded | 8 gp | 2 |
| Manacles (without padlock) | 6 gp | 4 |
| Map or scroll case | 1 gp | ½ |
| Mirror, small metal | 7 gp | \* |
| Oil (per flask) | 1 gp | 1 |
| Padlock (with 2 keys) | 12 gp | 1 |
| Paper (per sheet) | 1 gp | \*\* |
| Pole, 10’ wooden | 1 gp | 10 |
| Quill | 1 sp | \*\* |
| Quill Knife | 1 gp | \* |
| Quiver or Bolt case | 1 gp | 1 |
| Rations, Dry, one week | 10 gp | 14 |
| Rope, Hemp (per 50 ft.) | 1 gp | 5 |
| Rope, Silk (per 50 ft.) | 10 gp | 2 |
| Sack, Large | 1 gp | \* |
| Sack, Small | 5 sp | \* |
| Saddle, Pack | 5 gp | 15 |
| Saddle, Riding | 10 gp | 35 |
| Saddlebags, pair | 4 gp | 7 |
| Spellbook (128 pages) | 25 gp | 1 |
| Tent, Large (ten men) | 25 gp | 20 |
| Tent, Small (one man) | 5 gp | 10 |
| Thieves’ picks and tools | 25 gp | 1 |
| Tinderbox, flint and steel | 3 gp | 1 |
| Torches, 6 | 1 gp | 1 |
| Whetstone | 1 gp | 1 |
| Whistle | 1 gp | \*\* |
| Wineskin/Waterskin | 1 gp | 2 |
| Winter blanket | 1 gp | 3 |

### Equipment Explanations [Anchor](https://www.basicfantasy.org/srd/equipment.html\#equipment-explanations)

A **Backpack** will hold a maximum 40 pounds or 3 cubic feet of goods. Some items may be lashed to the outside, and thus count toward the weight limit but not the volume limit. A Halfling’s backpack holds at most 30 pounds and/or 1½ cubic feet, but costs the same as a full-sized item.

A **Candle** will shed light over a 5’ radius, with dim light extending 5’ further. A normal candle will burn about 3 turns per inch of height.

**Chalk** is useful for “blazing a trail” through a dungeon or ruin.

**Holy Water** is explained in the [Encounter section](https://www.basicfantasy.org/srd/combat.html#holy-water).

**Iron Spikes** are useful for spiking doors closed (or spiking them open) and may be used as crude pitons in appropriate situations.

A **Lantern** will provide light covering a 30’ radius; dim light will extend about 20’ further. A lantern will consume a flask of oil in 18+1d6 turns. A **Hooded Lantern** allows the light to be hidden or revealed as the user pleases; in all other ways it performs as an ordinary lantern. A **Bullseye Lantern** projects a cone of light 30’ long and 30’ wide at the widest point, with dim light extending an additional 20’ beyond that point. This type of lantern is generally hooded.

A **Map or Scroll Case** is a tubular oiled leather case used to carry maps, scrolls, or other paper items. The case will have a water-resistant (but not waterproof) cap which slides over the end, and a loop to allow the case to be hung from a belt or bandolier. A standard scroll case can hold up to 10 sheets of paper, or a single scroll of up to seven spells.

A **Mirror** is useful in a dungeon environment for many reasons; for instance, it is the only way to look at a Medusa without being turned to stone. Mirrors are also useful for looking around corners, and can be used outdoors to send signals using reflected sunlight.

A **Quiver** is an open container used to hold arrows. A **Bolt Case** is a similar sort of container for crossbow bolts. In either case, the standard capacity is 20 missiles. The length of a quiver or bolt case must match the length of the ammunition for it to be useful; therefore, there are longbow and shortbow quivers and light and heavy crossbow bolt cases. The price is the same for all types.

**Dry Rations** may consist of dry bread, hard cheese, dried fruit, nuts, beans, jerky, or any other food which will not “go bad” in less than about a month (if not longer). Dry rations are generally sold in quantities sufficient for one character for a week, and are packaged in waxed or oiled cloth to protect them.

**Hemp Rope** is ½ inch in diameter and has a breaking strength of 1,600 pounds. Safe working load for a rope is normally one-quarter of the breaking strength. One or more knots in a rope cut the breaking strength in half. This does not affect the safe working load, because knots are figured into the listed one-quarter ratio.

**Silk Rope** is about 3/8 inch in diameter and has a breaking strength of 1,600 pounds, although it weighs considerably less than hemp rope. The notes regarding rope strength given for hemp rope, above, apply here also.

A **Large Sack** will hold at most 40 pounds or 4 cubic feet of goods.

A **Small Sack** will hold at most 20 pounds or 2 cubic feet of goods.

A pair of **Saddlebags** will hold at most 10 pounds or 1 cubic foot of goods (divided evenly between both bags).

**Thieves’ Picks and Tools** are required for the use of Thief abilities such as opening locks and removing traps. These abilities may not be usable without appropriate tools, or may be used at a penalty at the option of the Game Master.

A **Tinderbox** is generally purchased with a **flint and steel**; the flint, a piece of hard rock, is struck vigorously against a C-shaped piece of high-carbon steel. When done correctly, hot sparks will fly from the flint and steel into the tinder, hopefully starting a fire. The best tinder is a dried piece of prepared tinder fungus, carried in the tinderbox to keep it dry; char cloth, hemp rope, or even very dry grass can substitute if prepared tinder fungus is not available. The time required to start a fire should be determined by the GM according to the prevailing conditions; under ideal conditions, starting a fire with a flint, steel and tinder takes about a turn.

A **Torch** sheds light over a 30’ radius, with dim light extending about 20’ further, and burns for 1d4+4 turns. Of course, a torch is also useful for setting flammable materials (such as cobwebs or oil) alight.

A **Whetstone** is used to sharpen and maintain edged weapons such as swords, daggers, and axes.

**Wineskin/Waterskin** is a container for drinking water or wine; though generally water is taken into a dungeon or wilderness environment. The standard waterskin holds one quart of liquid, which is the minimum amount required by a normal character in a single day. If adventuring in the desert or other hot, dry areas, a character may need as much as ten times this amount. Note that the given 2 pound weight is for a full skin; an empty skin has negligible weight.

## Weapons [Anchor](https://www.basicfantasy.org/srd/equipment.html\#weapons)

| Weapon | Price | Size | Weight | Dmg. |
| --- | --- | --- | --- | --- |
| **Axes** |  |  |  |  |
| Hand Axe | 4 gp | S | 5 | 1d6 |
| Battle Axe | 7 gp | M | 7 | 1d8 |
| Great Axe | 14 gp | L | 15 | 1d10 |
| **Bows** |  |  |  |  |
| Shortbow | 25 gp | M | 2 |  |
| Shortbow Arrow | 1 sp |  | \* | 1d6 |
| Silver† Shortbow Arrow | 2 gp |  | \* | 1d6 |
| Longbow | 60 gp | L | 3 |  |
| Longbow Arrow | 2 sp |  | \* | 1d8 |
| Silver† Longbow Arrow | 4 gp |  | \* | 1d8 |
| Light Crossbow | 30 gp | M | 7 |  |
| Light Quarrel | 2 sp |  | \* | 1d6 |
| Silver† Light Quarrel | 5 gp |  | \* | 1d6 |
| Heavy Crossbow | 50 gp | L | 14 |  |
| Heavy Quarrel | 4 sp |  | \* | 1d8 |
| Silver† Heavy Quarrel | 10 gp |  | \* | 1d8 |
| **Daggers** |  |  |  |  |
| Dagger | 2 gp | S | 1 | 1d4 |
| Silver† Dagger | 25 gp | S | 1 | 1d4 |
| **Swords** |  |  |  |  |
| Shortsword | 6 gp | S | 3 | 1d6 |
| Longsword/Scimitar | 10 gp | M | 4 | 1d8 |
| Two-Handed Sword | 18 gp | L | 10 | 1d10 |
| **Hammers and Maces** |  |  |  |  |
| Warhammer | 4 gp | S | 6 | 1d6 |
| Mace | 6 gp | M | 10 | 1d8 |
| Maul | 10 gp | L | 16 | 1d10 |
| **Other Weapons** |  |  |  |  |
| Club/Cudgel/Walking Staff | 2 sp | M | 1 | 1d4 |
| Quarterstaff | 2 gp | L | 4 | 1d6 |
| Pole Arm | 9 gp | L | 15 | 1d10 |
| Sling | 1 gp | S | \* |  |
| Bullet | 1 sp |  | \* | 1d4 |
| Stone | n/a |  | \* | 1d3 |
| Spear | 5 gp | M | 5 |  |
| Thrown (one handed) |  |  |  | 1d6 |
| Melee (one handed) |  |  |  | 1d6 |
| Melee (two handed) |  |  |  | 1d8 |

\\* These items weigh little individually. Ten of these items weigh one pound.

† Silver tip or blade, for use against lycanthropes

## Weapon Size [Anchor](https://www.basicfantasy.org/srd/equipment.html\#weapon-size)

[Humans](https://www.basicfantasy.org/srd/races.html#humans) and [Elves](https://www.basicfantasy.org/srd/races.html#elves) must wield Large weapons with both hands, but may use Small or Medium weapons in one hand. [Halflings](https://www.basicfantasy.org/srd/races.html#halflings) may not use Large weapons at all, and must use Medium weapons with both hands. [Dwarves](https://www.basicfantasy.org/srd/races.html#dwarves), due to their stocky, powerful builds, are able to use Medium weapons one-handed and some Large weapons in two hands, but Large weapons more than four feet in length are prohibited (specifically, two-handed swords, polearms, and longbows). Some weapons must be used with both hands by design (such as bows and crossbows) but the maximum size limits still apply.

The GM should apply similar limitations to weapon-armed monsters; for instance, kobolds and goblins are similar in size to Halflings, and thus should have similar weapon limits.

## Missile Weapon Ranges [Anchor](https://www.basicfantasy.org/srd/equipment.html\#missile-weapon-ranges)

| Weapon | Short (+1) | Medium (0) | Long (-2) |
| --- | --- | --- | --- |
| Longbow | 70 | 140 | 210 |
| Shortbow | 50 | 100 | 150 |
| Heavy Crossbow | 80 | 160 | 240 |
| Light Crossbow | 60 | 120 | 180 |
| Dagger | 10 | 20 | 30 |
| Hand Axe | 10 | 20 | 30 |
| Oil or Holy Water | 10 | 30 | 50 |
| Sling | 30 | 60 | 90 |
| Spear | 10 | 20 | 30 |
| Warhammer | 10 | 20 | 30 |

Missile weapon ranges are given in feet. In the wilderness, substitute yards for feet. If the target is as close as or closer than the Short range figure, the attacker receives a +1 attack bonus. If the target is further away than the Medium range figure, but not beyond the Long range figure, the attacker receives a -2 attack penalty.

## Armor and Shields [Anchor](https://www.basicfantasy.org/srd/equipment.html\#armor-and-shields)

| Armor Type | Price | Weight | AC |
| --- | --- | --- | --- |
| No Armor | 0 gp | 0 | 11 |
| Leather Armor | 20 gp | 15 | 13 |
| Chain Mail | 60 gp | 40 | 15 |
| Plate Mail | 300 gp | 50 | 17 |
| Shield | 7 gp | 5 | +1 |

## Beasts of Burden [Anchor](https://www.basicfantasy.org/srd/equipment.html\#beasts-of-burden)

Note: Statistics for the animals below are [here](https://www.basicfantasy.org/srd/monsters.html#beasts-of-burden).

| Item | Price |
| --- | --- |
| Horse, Draft | 120 gp |
| Horse, War | 200 gp |
| Horse, Riding | 75 gp |
| Pony\* | 40 gp |
| Pony, War\* | 80 gp |

\*Due to their small stature, Dwarves and Halflings generally ride ponies rather than horses.

## [Anchor](https://www.basicfantasy.org/srd/equipment.html\#section)

[5Character Classes](https://www.basicfantasy.org/srd/class.html)

[7Vehicles](https://www.basicfantasy.org/srd/vehicles.html)