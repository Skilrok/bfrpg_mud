1. [Player Characters](https://www.basicfantasy.org/srd/char-creation.html)
2. [3Character Abilities](https://www.basicfantasy.org/srd/abilities.html)

[Basic Fantasy RPG, 4th edition](https://www.basicfantasy.org/srd/)

[Toggle dark mode](https://www.basicfantasy.org/srd/abilities.html "Toggle dark mode")

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

- [Ability Scores](https://www.basicfantasy.org/srd/abilities.html#ability-scores)
  - [Stat Roller](https://www.basicfantasy.org/srd/abilities.html#stat-roller)
- [Hit Points and Hit Dice](https://www.basicfantasy.org/srd/abilities.html#hit-points-and-hit-dice)
- [Languages](https://www.basicfantasy.org/srd/abilities.html#languages)

# 3Character Abilities

## Ability Scores [Anchor](https://www.basicfantasy.org/srd/abilities.html\#ability-scores)

Each character will have a score ranging from 3 to 18 in each of the following abilities. A bonus or penalty is associated with each score, as shown on the table below. Each class has a [Prime Requisite](https://www.basicfantasy.org/srd/class.html#character-classes) ability score, which must be at least 9 in order for the character to become a member of that class; also, there are required minimum and maximum scores for each character race other than Humans, as described under [Character Races](https://www.basicfantasy.org/srd/races.html#character-races).

| Ability Score | Bonus/Penalty |
| --- | --- |
| 3 | -3 |
| 4-5 | -2 |
| 6-8 | -1 |
| 9-12 | 0 |
| 13-15 | +1 |
| 16-17 | +2 |
| 18 | +3 |

**Strength:** As the name implies, this ability measures the character’s raw physical power. Strength is the Prime Requisite for [Fighters](https://www.basicfantasy.org/srd/class.html#fighter). Apply the ability bonus or penalty for Strength to all attack and damage rolls in melee (hand to hand) combat. Note that a penalty here will not reduce damage from a successful attack below one point in any case (see the [Combat](https://www.basicfantasy.org/srd/combat.html#damage) section for details).

**Intelligence:** This is the ability to learn and apply knowledge. Intelligence is the Prime Requisite for [Magic-Users](https://www.basicfantasy.org/srd/class.html#magic-users). The ability bonus for Intelligence is added to the number of [languages](https://www.basicfantasy.org/srd/abilities.html#languages) the character is able to learn to read and write; if the character has an Intelligence penalty, he or she cannot read more than a word or two, and will only know his or her native language.

**Wisdom:** A combination of intuition, willpower and common sense. Wisdom is the Prime Requisite for [Clerics](https://www.basicfantasy.org/srd/class.html#cleric). The Wisdom bonus or penalty may apply to some saving throws vs. magical attacks, particularly those affecting the target’s will.

**Dexterity:** This ability measures the character’s quickness and balance as well as aptitude with tools. Dexterity is the Prime Requisite for [Thieves](https://www.basicfantasy.org/srd/class.html#thief). The Dexterity bonus or penalty is applied to all [attack rolls](https://www.basicfantasy.org/srd/combat.html#attacking-maneuvers) with missile (ranged) weapons, to the character’s [Armor Class](https://www.basicfantasy.org/srd/equipment.html#armor-and-shields) value, and to the character’s [Initiative](https://www.basicfantasy.org/srd/combat.html#initiative) die roll.

**Constitution:** A combination of general health and vitality. Apply the Constitution bonus or penalty to each hit die rolled by the character. Note that a penalty here will not reduce any hit die roll to less than 1 point.

**Charisma:** This is the ability to influence or even lead people; those with high Charisma are well-liked, or at least highly respected. Apply the Charisma bonus or penalty to reaction rolls. Also, the number of [retainers](https://www.basicfantasy.org/srd/hirelings.html#retainers) a character may hire, and the loyalty of those retainers, is affected by Charisma.

#### Stat Roller [Anchor](https://www.basicfantasy.org/srd/abilities.html\#stat-roller)

```sourceCode javascript
import { generalDice } from "./custom.js"

viewof statRolls = Inputs.button("Roll Stats", {value: null, reduce: () => [generalDice(3,6,0),generalDice(3,6,0),generalDice(3,6,0),generalDice(3,6,0),generalDice(3,6,0),generalDice(3,6,0)]})
```

```javascript hljs
  import {generalDice as generalDice} from "./custom.js"

```

Roll Stats

statRolls = null

```sourceCode javascript
import { calculateModifier } from "./custom.js"
{
    var x = ""
/*     if (statRolls != null){
        x = md`<br>${statRolls[0]} &emsp; (${calculateModifier(statRolls[0])})
        <br>${statRolls[1]} &emsp; (${calculateModifier(statRolls[1])})
        <br>${statRolls[2]} &emsp; (${calculateModifier(statRolls[2])})
        <br>${statRolls[3]} &emsp; (${calculateModifier(statRolls[3])})
        <br>${statRolls[4]} &emsp; (${calculateModifier(statRolls[4])})
        <br>${statRolls[5]} &emsp; (${calculateModifier(statRolls[5])})`
    } else {x = md`<br><b>Press button to roll stats<b>`} */

    if (statRolls != null) {
        x = html`<br><table style="max-width:20%;">
                    <tr>
                        <td>${statRolls[0]}</td>
                        <td>(${calculateModifier(statRolls[0])})</td>
                    </tr>
                    <tr>
                        <td>${statRolls[1]}</td>
                        <td>(${calculateModifier(statRolls[1])})</td>
                    </tr>
                    <tr>
                        <td>${statRolls[2]}</td>
                        <td>(${calculateModifier(statRolls[2])})</td>
                    </tr>
                    <tr>
                        <td>${statRolls[3]}</td>
                        <td>(${calculateModifier(statRolls[3])})</td>
                    </tr>
                    <tr>
                        <td>${statRolls[4]}</td>
                        <td>(${calculateModifier(statRolls[4])})</td>
                    </tr>
                    <tr>
                        <td>${statRolls[5]}</td>
                        <td>(${calculateModifier(statRolls[5])})</td>
                    </tr>
                `
    } else {x = md`<br><b>Press button to roll stats<b>`}

    return x
    }
```

```javascript hljs
  import {calculateModifier as calculateModifier} from "./custom.js"

```

**Press button to roll stats**

## Hit Points and Hit Dice [Anchor](https://www.basicfantasy.org/srd/abilities.html\#hit-points-and-hit-dice)

When a character is injured, he or she loses hit points from his or her current total. Note that this does not change the figure rolled, but rather reduces the current total; healing will restore hit points, up to but not exceeding the rolled figure.

When his or her hit point total reaches 0, your character may be dead. This may not be the end for the character; don’t tear up the character sheet.

First level characters begin play with a single hit die of the given type, plus the Constitution bonus or penalty, with a **minimum** of 1 hit point. Each time a character gains a level, the player should roll another hit die and add the character’s Constitution bonus or penalty, with the result again being a minimum of 1 point. Add this amount to the character’s maximum hit points figure. Note that, after 9th level, characters receive a fixed number of hit points each level, as shown in the [advancement table for the class](https://www.basicfantasy.org/srd/class.html#character-classes), and no longer add the Constitution bonus or penalty.

## Languages [Anchor](https://www.basicfantasy.org/srd/abilities.html\#languages)

All characters begin the game knowing their native language. In most campaign worlds, Humans all (or nearly all) speak the same language, often called “Common.” Each demi-human race has its own language, i.e. Elvish, Dwarvish, or Halfling, and members of the demi-human races begin play knowing both their own language and Common (or the local Human language if it isn’t called Common).

Characters with Intelligence of 13 or higher may choose to begin the game knowing one or more languages other than those given above; the number of additional languages that may be learned is equal to the Intelligence bonus (+1, +2, or +3). Characters may choose to learn other demi-human languages, as well as humanoid languages such as Orc, Goblin, etc. The GM will decide which humanoid languages may be learned. The player may choose to leave one or more bonus language “slots” open, to be filled during play. Some Game Masters may even allow player characters to learn exotic languages such as Dragon; also, “dead” or otherwise archaic languages might be allowed to more scholarly characters.

[2Player Characters](https://www.basicfantasy.org/srd/char-creation.html)

[4Character Races](https://www.basicfantasy.org/srd/races.html)