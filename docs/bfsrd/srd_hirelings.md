1. [Adventure](https://www.basicfantasy.org/srd/dungeonAdventures.html)
2. [12Hirelings](https://www.basicfantasy.org/srd/hirelings.html)

[Basic Fantasy RPG, 4th edition](https://www.basicfantasy.org/srd/)

[Toggle dark mode](https://www.basicfantasy.org/srd/hirelings.html "Toggle dark mode")

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

- [Retainers](https://www.basicfantasy.org/srd/hirelings.html#retainers)
- [Specialists](https://www.basicfantasy.org/srd/hirelings.html#specialists)
- [Mercenaries](https://www.basicfantasy.org/srd/hirelings.html#mercenaries)

# 12Hirelings

Player characters will sometimes want or need to hire NPCs (Non-Player Characters) to work for them. There are several categories of NPCs available for hire, as follows:

### Retainers [Anchor](https://www.basicfantasy.org/srd/hirelings.html\#retainers)

A retainer is a close associate of his employer. Retainers are hired for a share of treasure (typically at least 15% of the employer’s income) plus support costs (weapons, armor, rations, and basic equipment provided by the employer). Retainers are typically very loyal and are willing to take reasonable risks; in particular, they are the only sort of hireling who will generally accompany a player character into a dungeon, lair, or ruin.

Hiring a retainer is more involved than hiring other NPCs. First, the player character must advertise for a retainer, typically by hiring a crier, posting notices in public places, or asking (and possibly paying) NPCs such as innkeepers or taverners to direct potential retainers to the player character. It is up to the Game Master to rule on what must be done, and how successful these activities are.

If the player character is successful, one or more NPCs will present themselves to be interviewed. The Game Master should play out the interview with the player, and after all offers have been made and all questions asked, a reaction roll should be made. To check the potential retainer’s reaction, the Game Master rolls 2d6 and adds the player character’s Charisma bonus. In addition, the Game Master may apply any adjustments he or she feels are appropriate (a bonus of +1 for higher-than-average pay or the offer of a magic item such as a **sword +1**, or a penalty if the player character offers poor terms). The roll is read as follows:

```sourceCode javascript
import {generalTableSelect2, highlightTableRowRet} from "./custom.js"

viewof reaction = Inputs.button("Roll on Table", {value: 0, reduce: () => highlightTableRowRet("#reaction-roll", generalTableSelect2([2,6,0],[[2,2],[3,5],[6,8],[9,11],[12,12]]))})
md`2d6: ${reaction}`
```

```javascript hljs
  import {generalTableSelect2 as generalTableSelect2, highlightTableRowRet as highlightTableRowRet} from "./custom.js"

```

Roll on Table

reaction = 0

2d6: 0

| **Adjusted Die Roll** | **Result** |
| --- | --- |
| 2 or less | Refusal, -1 on further rolls |
| 3-5 | Refusal |
| 6-8 | Try again |
| 9-11 | Acceptance |
| 12 or more | Acceptance, +1 to Loyalty |

**Refusal, -1 on further rolls** means that all further reaction rolls made toward that player character in the given town or region will be at a penalty of -1 due to unkind words said by the NPC to his fellows. If the player character tries again in a different town, the penalty does not apply.

If a **Try again** result is rolled, the potential retainer is reluctant, and needs more convincing; the player character must “sweeten” the deal in order to get an additional roll, such as by offering more pay, a magic item, etc. If the player character makes no better offer, treat **Try again** as a **Refusal** result.

**Loyalty:** All retainers have a Loyalty score, which is generally 7 plus the employer’s Charisma bonus (or penalty). The Loyalty score is used just as the Morale score of monsters or mercenaries is used.

If a Loyalty check roll made in combat is a natural 2, the Loyalty of the retainer increases by +1 point. Note that a Loyalty of 12 is fanatical… the retainer will do virtually anything the player character asks, and never flee in combat. However, the Game Master should still apply penalties when the player character instructs the retainer to do something which appears very risky, making a failed check possible.

In addition, the Game Master should roll a Loyalty check for each retainer at the end of each adventure, after treasure is divided, to determine if the retainer will remain with the player character. The GM may apply adjustments to this roll, probably no more than two points plus or minus, if the retainer is particularly well or poorly paid.

**Maximum Number of Retainers:** A player character may hire at most 4 retainers, adjusted by the character’s Charisma bonus or penalty. Any attempts to hire more than this number of retainers will be met with automatic refusals.

**Level of Retainers:** Normally, potential retainers will be one-half the level of the employer (or less). So, a first level character cannot hire retainers, second level PCs can only hire first level characters, and so on. Of course, there is no way for the retainers to directly know the level of the PC employer, nor for the employer to know the level of the potential retainer; but the Game Master should usually enforce this rule for purposes of game balance. It shouldn’t be surprising that first level characters can’t hire retainers, as they have no reputation to speak of yet.

**Experience for Retainers:** Unlike other hired NPCs, retainers do gain experience just as other adventurers do; however, as they are under the command of a player character, only one-half of a share of XP is allocated to each retainer. See [Character Advancement](https://www.basicfantasy.org/srd/advancement.html#advancement).

### Specialists [Anchor](https://www.basicfantasy.org/srd/hirelings.html\#specialists)

Specialists are NPCs who may be hired by player characters to perform various tasks. Specialists do not go on adventures or otherwise risk their lives fighting monsters, disarming traps, or any of the other dangerous things player characters and retainers may do. Rather, specialists perform services the player characters usually can’t perform for themselves, like designing and erecting castles, training animals, or operating ships.

A player character is limited in the number of specialists he or she can hire only by the amount of money they cost; Charisma does not affect this.

**Alchemist:** _1,000 gp per month._ These characters are generally hired for one of two reasons: to make potions, or to assist a Magic-User with magical research.

An alchemist can produce a potion, given the required materials and a sample or a written formula for the potion, in the same time and for the same cost as a Magic-User. They may also research new potions, but at twice the cost in time and materials as a Magic-User. Review the rules for [Magical Research](https://www.basicfantasy.org/srd/gm01.html#magical-research) for details.

Alternately, a Magic-User seeking to create certain magic items may employ an alchemist as an assistant. In this case, the alchemist adds 15% to the Magic-User’s chance of success.

**Animal Trainer:** _250 to 750 gp per month._ Characters wishing to ride hippogriffs or employ carnivorous apes as guards will need the assistance of an animal trainer. The lowest cost above is for an average animal trainer, able to train one type of “normal” animal such as carnivorous apes; those able to train more than one sort of animal, or to train monstrous creatures such as hippogriffs, are more expensive to hire. The Game Master must decide how long it takes to train an animal; in some cases, animal training may take years, a fact the player characters may find inconvenient as well as expensive. A single animal trainer can train and manage no more than 5 animals at a time, though in most cases once an animal is fully trained, if it is put into service right away the animal trainer won’t be needed to handle it any longer.

**Armorer (or Weaponsmith):** _100 to 500 gp per month._ Characters hiring mercenaries, or having armed and armored followers to take care of, will need the services of an armorer. In general, for every 50 Fighters employed, one armorer is required to care for their gear. The armorer’s equipment is not included in the costs given above, but the cost to maintain his apprentices is included; most such characters will have 1d4 apprentices assisting.

Higher priced armorers or weaponsmiths may be hired to assist in making magic weapons or armor; in this case, the character hired will be a specialist, an expert in making one particular type of armor or weapon, and will command a higher price (as shown above). Such characters will rarely agree to do the mundane work of maintaining weapons and armor for a military unit.

**Engineer:** _750 gp per month._ Any player character wishing to build a fortress, a ship, or any other mundane construction will need an engineer. Large projects may require several engineers, at the GM’s option.

**Savant:** _1,500 gp per month._ Savants are experts in ancient and obscure knowledge. Many savants have particular interests in very limited or focused areas (for example, “Elven migrations of the 2nd age”), but even these will know or have access to a lot of facts. The listed cost is the minimum required to maintain a savant with his library, collections, etc. If the savant’s patron asks a difficult question, there may be additional costs for materials or research to answer it.

**Ship’s Crew:** _Special._ A crew for a waterborne vessel involves several types of characters. At the very least, a complement of sailors and a Captain are needed; rowers will be needed aboard galleys, and a Navigator is required aboard ships going out of sight of land.

Costs per month for each sort of character are given below:

| Seaman Type | Cost |
| --- | --- |
| Captain | 300 gp |
| Navigator | 200 gp |
| Sailor | 10 gp |
| Rower | 3 gp |

In general, all such characters are normal men, and are not armored; they will usually be armed with clubs, daggers, or shortswords. Player characters with appropriate backgrounds may act as Captain, but unless experienced as a ship’s captain, they will have difficulty commanding respect from the regular sailors (lower the Morale of such regular sailors by -2 if led by an inexperienced Captain).

### Mercenaries [Anchor](https://www.basicfantasy.org/srd/hirelings.html\#mercenaries)

Mercenaries are hired warriors. They are generally hired in units as small as platoons: 32 to 48 Fighters, divided into two to four squads of soldiers; each squad is led by a corporal, while the platoon is led by a lieutenant plus a sergeant. Platoons are joined together into companies, each generally consisting of two to five platoons and led by a captain with a sergeant as his assistant (called a **first sergeant**).

As mercenaries are almost always veteran troops, the average mercenary is a 1st level Fighter; 10% of corporals and 50% of sergeants are 2nd level. A mercenary lieutenant will generally be 2nd level, while a captain will be 2nd to 4th level and his first sergeant will be 2nd or 3rd level. Larger mercenary units will usually be beyond the reach of player characters until they have reached fairly high levels, and are left to the Game Master to detail.

Mercenaries will virtually never go into a dungeon, lair, or ruin, at least until it has been fully cleared. Rather, they are used in outdoor military engagements; high level player characters may hire mercenaries to defend or help defend their castles or other holdings.

Mercenaries housed in a player character’s stronghold require 200 square feet each but cost 25% less per month, as this is covered by their room and board. (Elven mercenaries, however, require 500 square feet of space each in order to reduce their pay, as they demand better living conditions.) See the **Stronghold** section for more details.

Statistics are given below for the most common sorts of mercenaries; the statistics are for first level characters, and should be adjusted when higher level characters are indicated (as given above). In particular, multiply the given cost of each mercenary by his or her level. Listed costs are in gold pieces per month.

| Type of Mercenary | Cost | Equipment | Morale |
| --- | --- | --- | --- |
| Light Foot, Human | 2 | Leather Armor, Shield, and Longsword | 8 |
| Light Foot, Elf | 8 | Leather Armor, Shield, and Longsword | 8 |
| Light Foot, Orc | 1 | Leather Armor and Spear | 7 |
| Heavy Foot, Human | 3 | Chainmail, Shield, and Longsword | 8 |
| Heavy Foot, Dwarf | 6 | Chainmail, Shield, and Shortsword | 9 |
| Heavy Foot, Orc | 2 | Chainmail, Shield, and Shortsword | 8 |
| Archer, Human | 5 | Leather Armor, Shortbow, and Shortsword | 8 |
| Archer, Elf | 15 | Chainmail, Shortbow, and Shortsword | 8 |
| Archer, Orc | 3 | Leather Armor, Shortbow, and Shortsword | 8 |
| Crossbowman, Human | 5 | Chainmail, Crossbow, and Shortsword | 8 |
| Crossbowman, Dwarf | 12 | Platemail, Crossbow, and Shortsword | 9 |
| Longbowman, Human | 9 | Chainmail, Longbow, and Shortsword | 8 |
| Longbowman, Elf | 20 | Chainmail, Longbow, and Longsword | 8 |
| Light Horseman, Human | 10 | Leather Armor, Shield, Lance, and Longsword | 8 |
| Light Horseman, Elf | 22 | Leather Armor, Lance, Shortbow, and Longsword | 8 |
| Medium Horseman, Human | 15 | Chainmail, Shield, Lance, and Longsword | 8 |
| Medium Horseman, Elf | 33 | Chainmail, Lance, Shortbow, and Longsword | 9 |
| Heavy Horseman, Human | 20 | Platemail, Shield, Lance, and Longsword | 8 |

[11Wilderness Adventures](https://www.basicfantasy.org/srd/wildAdventures.html)

[13Advancement](https://www.basicfantasy.org/srd/advancement.html)