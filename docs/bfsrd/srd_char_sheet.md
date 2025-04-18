1. [Appendix](https://www.basicfantasy.org/srd/appendix_interactive.html)
2. [24Character Sheet](https://www.basicfantasy.org/srd/char_sheet.html)

[Basic Fantasy RPG, 4th edition](https://www.basicfantasy.org/srd/)

[Toggle dark mode](https://www.basicfantasy.org/srd/char_sheet.html "Toggle dark mode")

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

# 24Character Sheet

Upload Character Sheet:

```sourceCode javascript
viewof recordsFile = Inputs.file({accept: ".json"})
```

recordsFile = null

```sourceCode javascript
char = {
if (recordsFile != null){
    const data = recordsFile.json()

    return data
}}
```

char = undefined

```sourceCode javascript
function addButtonMaybe (id,button) {
    if (d3.select(id).empty()) {
        d3.select(button).on('click')()
    }
}

loadFile = {
    ////////////////////////////
if (char != undefined){

    // Name and basic info
    d3.select('#Name').attr('value',char.Name);
    d3.select('#charClass').select('dd').text(char.Class);
    d3.select('#charRace').select('dd').text(char.Race);
    d3.select('#charLevel').select('dd').text(char.Level);
    d3.select('#charExperience').select('dd').text(char.Experience);

    d3.select('#hp1').attr('value',char.HP);
    d3.select('#hp2').attr('value',char.MaxHP);
    d3.select('#ACinput').attr('value',char.AC);
    d3.select('#HDinput').attr('value',char.HD);

    d3.select('#BABbox').text(char.BAB);
    d3.select('#MovementBox').text(char.Movement);
    d3.select('#InitiativeBox').text(char.Initiative);

    // Abilities
    d3.select('#strNum').attr('value',char.Abilities.Str );
    d3.select('#dexNum').attr('value',char.Abilities.Dex );
    d3.select('#conNum').attr('value',char.Abilities.Con);
    d3.select('#wisNum').attr('value',char.Abilities.Wis );
    d3.select('#intNum').attr('value',char.Abilities.Int );
    d3.select('#chaNum').attr('value',char.Abilities.Cha );

    d3.select("#strMod").text(calculateModifier(char.Abilities.Str))
    d3.select("#dexMod").text(calculateModifier(char.Abilities.Dex))
    d3.select("#conMod").text(calculateModifier(char.Abilities.Con))
    d3.select("#intMod").text(calculateModifier(char.Abilities.Wis))
    d3.select("#wisMod").text(calculateModifier(char.Abilities.Int))
    d3.select("#chaMod").text(calculateModifier(char.Abilities.Cha))

    // Saves
    d3.select('#save-drpBox').attr('value',char.Saves.DRP );
    d3.select('#save-wandBox').attr('value',char.Saves.MW );
    d3.select('#save-parBox').attr('value',char.Saves.Par);
    d3.select('#save-dbBox').attr('value',char.Saves.DB);
    d3.select('#save-spellBox').attr('value',char.Saves.Spl);

    // Thieving skills
    d3.select('#thiefLocksInput ').attr('value',char.ThiefSkills.OpenLocks);
    d3.select('#thiefTrapInput ').attr('value',char.ThiefSkills.RemoveTraps);
    d3.select('#thiefPocketsInput ').attr('value',char.ThiefSkills.PickPockets);
    d3.select('#thiefSilentInput ').attr('value',char.ThiefSkills.MoveSilent);
    d3.select('#thiefClimbInput ').attr('value',char.ThiefSkills.ClimbWalls);
    d3.select('#thiefHideInput ').attr('value',char.ThiefSkills.Hide);
    d3.select('#thiefListenInput ').attr('value',char.ThiefSkills.Listen);

    // Langs and other skills

    const langs = char.Languages
    const oSkills = char.OtherSkills

    if (langs.length <= 1) {
        d3.select('#language1').attr('value',langs[0]);
    } else {
        d3.select('#language1').attr('value',langs[0]);
        langs.slice(1).forEach( (x,i) => {
            addButtonMaybe(('#language'+ String(i+2)), '#addInputButton')
            // d3.select('#addInputButton').on('click')()
            d3.select('#language' + String(i+2)).attr('value',x)
        });
    }

    if (oSkills.length <= 1) {
        d3.select('#skill1').attr('value',oSkills[0]);
    } else {
        d3.select('#skill1').attr('value',oSkills[0]);
        oSkills.slice(1).forEach( (x,i) => {
            addButtonMaybe(('#skill' + String(i+2)), '#addSkillButton')
            d3.select('#skill' + String(i+2)).attr('value',x)
        });
    }

    /// Attacks
    const weaponEq = char.WeaponEq

    if (weaponEq.length > 0) {
        d3.select('#weaponForm1').attr('value',weaponEq[0].name);
        d3.select('#attackForm1').attr('value',weaponEq[0].attack);
        d3.select('#damageForm1').attr('value',weaponEq[0].damage);
        d3.select('#rangeSForm1').attr('value',weaponEq[0].S);
        d3.select('#rangeMForm1').attr('value',weaponEq[0].M);
        d3.select('#rangeLForm1').attr('value',weaponEq[0].L);
        d3.select('#notesForm1').attr('value',weaponEq[0].notes);
        weaponEq.slice(1).forEach( (x,i) => {
            addButtonMaybe(('#weaponForm' + String(i+2)), '#addWeaponButton')
            // d3.select('#addWeaponButton').on('click')()
            d3.select('#weaponForm' + String(i+2)).attr('value',x.name);
            d3.select('#attackForm' + String(i+2)).attr('value',x.attack);
            d3.select('#damageForm' + String(i+2)).attr('value',x.damage);
            d3.select('#rangeSForm' + String(i+2)).attr('value',x.S);
            d3.select('#rangeMForm' + String(i+2)).attr('value',x.M);
            d3.select('#rangeLForm' + String(i+2)).attr('value',x.L);
            d3.select('#notesForm' + String(i+2)).attr('value',x.notes);
        })
    }

    // Ammo
    const ammoEq = char.AmmoEq
    if (ammoEq.length > 0) {
        d3.select('#ammoForm1').attr('value',ammoEq[0].name);
        d3.select('#countForm1').attr('value',ammoEq[0].count);
        d3.select('#ammoDmgForm1').attr('value',ammoEq[0].damage);
        d3.select('#ammo-notesForm1').attr('value',ammoEq[0].notes);
        ammoEq.slice(1).forEach( (x,i) => {
            addButtonMaybe(('#ammoForm' + String(i+2)), '#addAmmoButton')
            //d3.select('#addAmmoButton').on('click')()
            d3.select('#ammoForm' + String(i+2)).attr('value',x.name);
            d3.select('#countForm' + String(i+2)).attr('value',x.count);
            d3.select('#ammoDmgForm' + String(i+2)).attr('value',x.damage);
            d3.select('#ammo-notesForm' + String(i+2)).attr('value',x.notes);
        })
    }

    /// Turn Undead

    const turning = char.Turning

    turning.forEach( (x,i) => {
        d3.select('#turn'+ String(i + 1)).attr('value',x)
    })

    // spells
    const spells = char.Spells
    if (spells.length > 0) {
        d3.select('#spell-level-Form1').attr('value',spells[0].spellLvl);
        d3.select('#spell-name-Form1').attr('value',spells[0].spellName);
        d3.select('#spell-prep-Form1').attr('value',spells[0].prep);
        spells.slice(1).forEach( (x,i) => {
            addButtonMaybe(('#spell-level-Form' + String(i+2)), '#addSpellButton')
            //d3.select('#addSpellButton').on('click')()
            d3.select('#spell-level-Form' + String(i+2)).attr('value',x.spellLvl);
            d3.select('#spell-name-Form' + String(i+2)).attr('value',x.spellName);
            d3.select('#spell-prep-Form' + String(i+2)).attr('value',x.prep);
        })
    }

    // Currency
    d3.select('#PPbox').text(char.Equipment.Currency.pp)
    d3.select('#GPbox').text(char.Equipment.Currency.gp)
    d3.select('#EPbox').text(char.Equipment.Currency.ep)
    d3.select('#SPbox').text(char.Equipment.Currency.sp)
    d3.select('#CPbox').text(char.Equipment.Currency.cp)

        // Weapon Inventory
    const weaponsInv = char.Equipment.Weapons

    if (weaponsInv.length > 0) {
        d3.select('#itemMagical1').property('checked', weaponsInv[0].magic);
        d3.select('#itemEquipped1').property('checked', weaponsInv[0].equipped);
        d3.select('#itemName1').attr('value', weaponsInv[0].name);
        d3.select('#itemWeight1').attr('value',weaponsInv[0].weight).on('input')();
        weaponsInv.slice(1).forEach( (x,i) => {
            addButtonMaybe(('#itemMagical' + String(i+2)), '#addWeaponEqButton')
            //d3.select('#addWeaponEqButton').on('click')()
            d3.select('#itemMagical' + String(i+2)).property('checked',x.magic);
            d3.select('#itemEquipped' + String(i+2)).property('checked',x.equipped);
            d3.select('#itemName' + String(i+2)).attr('value',x.name);
            d3.select('#itemWeight' + String(i+2)).attr('value',x.weight)
        })
    }
    d3.select('#itemWeight1').attr('value',weaponsInv[0].weight).on('input')();

    // armor Inventory
    const armorInv = char.Equipment.Armor
    console.log("hellow world")
    console.log(char.Equipment.Armor)
    if (armorInv.length > 0) {
        d3.select('#armorMagical1').property('checked', armorInv[0].magic);
        d3.select('#armorEquipped1').property('checked', armorInv[0].equipped);
        d3.select('#armorName1').attr('value', armorInv[0].name);
        d3.select('#armorWeight1').attr('value',armorInv[0].weight).on('input')(); //trigger the input for weight sum
        armorInv.slice(1).forEach( (x,i) => {
            addButtonMaybe(('#armorMagical' + String(i+2)), '#addArmorEqButton')
            //d3.select('#addArmorEqButton').on('click')()
            d3.select('#armorMagical' + String(i+2)).property('checked',x.magic);
            d3.select('#armorEquipped' + String(i+2)).property('checked',x.equipped);
            d3.select('#armorName' + String(i+2)).attr('value',x.name);
            d3.select('#armorWeight' + String(i+2)).attr('value',x.weight).on('input')()
            ;
        })
    }

    // Misc Inventory
    const miscInv = char.Equipment.Misc

    if (miscInv.length > 0) {
        d3.select('#miscMagical1').property('checked', miscInv[0].magic);
        d3.select('#miscEquipped1').property('checked', miscInv[0].equipped);
        d3.select('#miscName1').attr('value', miscInv[0].name);
        d3.select('#miscWeight1').attr('value',miscInv[0].weight).on('input')(); //trigger the input for weight sum
        miscInv.slice(1).forEach( (x,i) => {
            addButtonMaybe(('#miscMagical' + String(i+2)), '#addItemEqButton')
            //d3.select('#addItemEqButton').on('click')()
            d3.select('#miscMagical' + String(i+2)).property('checked',x.magic);
            d3.select('#miscEquipped' + String(i+2)).property('checked',x.equipped);
            d3.select('#miscName' + String(i+2)).attr('value',x.name);
            d3.select('#miscWeight' + String(i+2)).attr('value',x.weight)
            ;
        })
    }
    d3.select('#miscWeight1').on('input')();

    /// notes
    const hirelings = char.Hirelings

    if (hirelings.length > 0) {
        d3.select('#hireling1').attr('value', hirelings[0]);
        hirelings.slice(1).forEach( (x,i) => {
            addButtonMaybe(('#hireling' + String(i+2)), '#addHirelingButton')
            //d3.select('#addHirelingButton').on('click')()
            d3.select('#hireling' + String(i+2)).attr('value',x);
        })
    }

    d3.select('#background').text(char.Background);
    d3.select('#miscNotes').text(char.MiscNotes);

}// if
///////////////////////////////////
}
```

addButtonMaybe = ƒ(id, button)

loadFile = undefined

## Character Details [Anchor](https://www.basicfantasy.org/srd/char_sheet.html\#character-details)

Class

Race

Level

Experience

HP **/**

AC

HD

* * *

Base Attack Bonus

Movement

Initiative

d4


d6


d8


d10


d12


d20


d100


```sourceCode javascript
dice100 = {

const popoverTriggerEl = document.querySelector('#d100');
let popoverVal = 0;

const popover = new bootstrap.Popover(popoverTriggerEl, {
  content: popoverVal,
  placement: 'top'
});

popoverTriggerEl.addEventListener('show.bs.popover', () => {
    const diceNumber = Number(document.getElementById("d100-number").value)
    popoverVal = generalDice(diceNumber,100,0); // replace with a call to your function

  popover.setContent({
    '.popover-body': popoverVal.toString()
  });
});
}

dice20 = {

const popoverTriggerEl = document.querySelector('#d20');
let popoverVal = 0;

const popover = new bootstrap.Popover(popoverTriggerEl, {
  content: popoverVal,
  placement: 'top'
});

popoverTriggerEl.addEventListener('show.bs.popover', () => {
    const diceNumber = Number(document.getElementById("d20-number").value)
  popoverVal = generalDice(diceNumber,20,0); // replace with a call to your function

  popover.setContent({
    '.popover-body': popoverVal.toString()
  });
});

}

dice12 = {

const popoverTriggerEl = document.querySelector('#d12');
let popoverVal = 0;

const popover = new bootstrap.Popover(popoverTriggerEl, {
  content: popoverVal,
  placement: 'top'
});

popoverTriggerEl.addEventListener('show.bs.popover', () => {
    const diceNumber = Number(document.getElementById("d12-number").value)
    popoverVal = generalDice(diceNumber,12,0); // replace with a call to your function

  popover.setContent({
    '.popover-body': popoverVal.toString()
  });
});

}

dice10 = {

const popoverTriggerEl = document.querySelector('#d10');
let popoverVal = 0;

const popover = new bootstrap.Popover(popoverTriggerEl, {
  content: popoverVal,
  placement: 'top'
});

popoverTriggerEl.addEventListener('show.bs.popover', () => {
    const diceNumber = Number(document.getElementById("d10-number").value)
    popoverVal = generalDice(diceNumber,10,0); // replace with a call to your function

  popover.setContent({
    '.popover-body': popoverVal.toString()
  });
});

}

dice8 = {

const popoverTriggerEl = document.querySelector('#d8');
let popoverVal = 0;

const popover = new bootstrap.Popover(popoverTriggerEl, {
  content: popoverVal,
  placement: 'top'
});

popoverTriggerEl.addEventListener('show.bs.popover', () => {
    const diceNumber = Number(document.getElementById("d8-number").value)
    popoverVal = generalDice(diceNumber,8,0); // replace with a call to your function

  popover.setContent({
    '.popover-body': popoverVal.toString()
  });
});

}

dice6 = {

const popoverTriggerEl = document.querySelector('#d6');
let popoverVal = 0;

const popover = new bootstrap.Popover(popoverTriggerEl, {
  content: popoverVal,
  placement: 'top'
});

popoverTriggerEl.addEventListener('show.bs.popover', () => {
    const diceNumber = Number(document.getElementById("d6-number").value)
  popoverVal = generalDice(diceNumber,6,0); // replace with a call to your function

  popover.setContent({
    '.popover-body': popoverVal.toString()
  });
});

}

dice4 = {

const popoverTriggerEl = document.querySelector('#d4');
let popoverVal = 0;

const popover = new bootstrap.Popover(popoverTriggerEl, {
  content: popoverVal,
  placement: 'top'
});

popoverTriggerEl.addEventListener('show.bs.popover', () => {
    const diceNumber = Number(document.getElementById("d4-number").value)
    popoverVal = generalDice(diceNumber,4,0); // replace with a call to your function

  popover.setContent({
    '.popover-body': popoverVal.toString()
  });
});

}
```

dice100 = undefined

dice20 = undefined

dice12 = undefined

dice10 = undefined

dice8 = undefined

dice6 = undefined

dice4 = undefined

- [Attributes](https://www.basicfantasy.org/srd/char_sheet.html#attributes)
- [Combat](https://www.basicfantasy.org/srd/combat.html#combat)
- [Spells](https://www.basicfantasy.org/srd/char_sheet.html#spells)
- [Equipment](https://www.basicfantasy.org/srd/char_sheet.html#equipment)
- [Notes](https://www.basicfantasy.org/srd/char_sheet.html#notes)

## Abilities [Anchor](https://www.basicfantasy.org/srd/char_sheet.html\#abilities)

Str( 0 )

Dex( 0 )

Con( 0 )

Int( 0 )

Wis( 0 )

Cha( 0 )

## Saving Throws [Anchor](https://www.basicfantasy.org/srd/char_sheet.html\#saving-throws)

Death Ray, Poison

Magic Wands

Paralysis / Petrification

Dragon Breath

Spells

## Thieving Skills [Anchor](https://www.basicfantasy.org/srd/char_sheet.html\#thieving-skills)

Open Locks

Remove Traps

Pick Pockets

Move Silently

Climb Walls

Hide

Listen

## Languages [Anchor](https://www.basicfantasy.org/srd/char_sheet.html\#languages)

Add Language

## Other Skills / Feats [Anchor](https://www.basicfantasy.org/srd/char_sheet.html\#other-skills-feats)

Add Skill

## Attacks [Anchor](https://www.basicfantasy.org/srd/char_sheet.html\#attacks)

Weapon or Spell

Attack

Damage

S+1

M+0

L-2

Notes

Add Weapon

Ammunition

Count

Damage

Notes

Add Ammo

## Turn Undead [Anchor](https://www.basicfantasy.org/srd/char_sheet.html\#turn-undead)

1 HD / Skeleton

2 HD / Zombie

3 HD / Ghoul

4 HD / Wight

5 HD / Wraith

6 HD / Mummy

7 HD / Spectre

8 HD / Vampire

9+ HD / Ghost

```sourceCode javascript
function addWeapon() {
      var inputContainer = d3.select('#attackContainer');
      var inputCount = inputContainer.selectAll('.grid').size();



    var inputGroup = inputContainer
      .append('div')
      .attr('class','grid g-0 justify-content-center').attr('style','--bs-gap:0;--bs-columns:13;')
      .attr('id','attack'+(inputCount + 1))

    inputGroup
    .html(`
      <div class="g-col-3">
        <input autocomplete="off" type="text" class="form-control form-control-sm weaponForm"  id="weaponForm${inputCount + 1}">
      </div>
      <div class="g-col-2">
        <input autocomplete="off" type="text" class="form-control form-control-sm attackForm" id="attackForm${inputCount + 1}">
      </div>
      <div class="g-col-2">
        <input autocomplete="off" type="text" class="form-control form-control-sm damageForm"  id="damageForm${inputCount + 1}">
      </div>
      <div class="g-col-1">
        <input autocomplete="off" type="text" class="form-control form-control-sm rangeSForm"  id="rangeSForm${inputCount + 1}">
      </div>
      <div class="g-col-1">
        <input autocomplete="off" type="text" class="form-control form-control-sm rangeMForm" id="rangeMForm${inputCount + 1}" >
      </div>
      <div class="g-col-1">
        <input autocomplete="off" type="text" class="form-control form-control-sm rangeLForm" id="rangeLForm${inputCount + 1}">
      </div>
      <div class="g-col-2">
        <input autocomplete="off" type="text" class="form-control form-control-sm notesForm"  id="notesForm${inputCount + 1}">
      </div>`)
    .append('div')
    .attr('class','g-col-1')
    .append('i')
    .attr('class', 'bi bi-x-lg mt-3 text-danger')
    .attr('style', 'cursor: pointer;')
    .attr('id', 'attackDel' + (inputCount + 1))
    .on('click', function() {
          inputGroup.remove();
        });

    console.log(inputCount)
    }

weapon = {
    const addInputButton = d3.select('#addWeaponButton');
    addInputButton.on('click', () => addWeapon() );


}
```

addWeapon = ƒ()

weapon = undefined

```sourceCode javascript
function addAmmo() {
      var inputContainer = d3.select('#ammoContainer');
      var inputCount = inputContainer.selectAll('.grid').size();

    var inputGroup = inputContainer
      .append('div')
      .attr('class','grid g-0 justify-content-center').attr('style','--bs-gap:0;--bs-columns:13;')
      .attr('id','ammo'+(inputCount + 1))

    inputGroup
    .html(`
    <div class="g-col-3">
        <input autocomplete="off" type="text" class="form-control form-control-sm ammoForm" id=ammoForm${inputCount + 1}>
    </div>
    <div class="g-col-1">
        <div class="form-outline">
            <input autocomplete="off" type="number" class="form-control form-control-sm countForm" value=0 id=countForm${inputCount + 1}>
        </div>
    </div>
    <div class="g-col-1">
        <input autocomplete="off" type="text" class="form-control form-control-sm ammoDmgForm"  id=ammoDmgForm${inputCount + 1}>
    </div>
    <div class="g-col-6">
        <div class="form-outline">
            <input autocomplete="off" type="text" class="form-control form-control-sm ammo-notesForm" id=ammo-notesForm${inputCount + 1}>
        </div>
    </div>
    `)
    .append('div')
    .attr('class','g-col-1')
    .append('i')
    .attr('class', 'bi bi-x-lg mt-3 text-danger')
    .attr('style', 'cursor: pointer;')
    .attr('id', 'ammoDel' + (inputCount + 1))
    .on('click', function() {
          inputGroup.remove();
        });

    }

ammo = {
    const addInputButton = d3.select('#addAmmoButton');
    addInputButton.on('click', () => addAmmo() );

}
```

addAmmo = ƒ()

ammo = undefined

Level

Name

Prep

Add Spell

```sourceCode javascript
function addSpell() {
      var inputContainer = d3.select('#spellContainer');
      var inputCount = inputContainer.selectAll('.grid').size();

    var inputGroup = inputContainer
      .append('div')
      .attr('class','grid align-content-center').attr('style','--bs-gap:0;--bs-columns:12;')
      .attr('id','spell'+(inputCount + 1))

    inputGroup
    .html(`
      <div class="g-col-2 g-col-sm-1">
        <input autocomplete="off" type="text" class="form-control text-center spell-level"  id="spell-level-Form${inputCount + 1}">
      </div>
      <div class="g-col-7 g-col-sm-8">
        <input autocomplete="off" type="text" class="form-control  spell-name"  id="spell-name-Form${inputCount + 1}">
      </div>
      <div class="g-col-2">
        <input autocomplete="off" type="number" class="form-control  spell-prep" id="spell-prep-Form${inputCount + 1}" value=0>
      </div>
    `)
    .append('div')
    .attr('class','g-col-1')
    .append('i')
    .attr('class', 'bi bi-x-lg mt-3 text-danger')
    .attr('style', 'cursor: pointer;')
    .attr('id', 'spellDel' + (inputCount + 1))
    .on('click', function() {
          inputGroup.remove();
        });

    }

spell = {
    const addInputButton = d3.select('#addSpellButton');
    addInputButton.on('click', () => addSpell() );

}
```

addSpell = ƒ()

spell = undefined

## Currency [Anchor](https://www.basicfantasy.org/srd/char_sheet.html\#currency)

PP

GP

EP

SP

CP

## Weapons [Anchor](https://www.basicfantasy.org/srd/char_sheet.html\#weapons)

M


E


Weapon


Weight


Add Weapon

## Armor [Anchor](https://www.basicfantasy.org/srd/char_sheet.html\#armor)

M


E


Armor / Shield


Weight


Add Armor

## Misc. [Anchor](https://www.basicfantasy.org/srd/char_sheet.html\#misc)

M


E


Item


Weight


Add Item

* * *

Total

```sourceCode javascript
function addWeaponEq() {
      var inputContainer = d3.select('#weaponEqContainer');
      var inputCount = inputContainer.selectAll('.grid').size();

    var inputGroup = inputContainer
      .append('div')
      .attr('class','grid align-content-center').attr('style','--bs-gap:0;--bs-columns:12;')
      .attr('id','weaponEq'+(inputCount + 1))

    inputGroup
    .html(`
        <div class="g-col-1 mt-2">
            <input autocomplete="off" class="form-check-input weaponsEqMag" type="checkbox" value=""  id="itemMagical${inputCount + 1}">
        </div>
        <div class="g-col-1 mt-2">
            <input autocomplete="off" class="form-check-input weaponsEqEq" type="checkbox" value="" id="itemEquipped${inputCount + 1}">
        </div>
        <div class="g-col-8">
            <input autocomplete="off" type="text" class="form-control form-control-sm weaponsEqName"  id="itemName${inputCount + 1}">
        </div>
        <div class="g-col-1">
            <input autocomplete="off" type="text" class="form-control form-control-sm weight weaponsEqWeight"
            onkeypress="return event.charCode >= 46 && event.charCode <= 57" id="itemWeight${inputCount + 1}">
        </div>
    `)
    .on("input", calcWeight)
    .append('div')
    .attr('class','g-col-1')
    .append('i')
    .attr('class', 'bi bi-x-lg mt-3 text-danger')
    .attr('style', 'cursor: pointer;')
    .attr('id', 'spellDel' + (inputCount + 1))
    .on('click', function() {
          inputGroup.remove();
          calcWeight();
        });

    }

weaponEq = {
    const addInputButton = d3.select('#addWeaponEqButton');
    addInputButton.on('click', () => addWeaponEq() );

}

function addArmorEq() {
      var inputContainer = d3.select('#armorEqContainer');
      var inputCount = inputContainer.selectAll('.grid').size();

    var inputGroup = inputContainer
      .append('div')
      .attr('class','grid align-content-center').attr('style','--bs-gap:0;--bs-columns:12;')
      .attr('id','armorEq'+(inputCount + 1))

    inputGroup
    .html(`
        <div class="g-col-1 mt-2">
            <input autocomplete="off" class="form-check-input armorMagical" type="checkbox" value=""  id="armorMagical${inputCount + 1}">
        </div>
        <div class="g-col-1 mt-2">
            <input autocomplete="off" class="form-check-input armorEquipped" type="checkbox" value="" id="armorEquipped${inputCount + 1}">
        </div>
        <div class="g-col-8">
            <input autocomplete="off" type="text" class="form-control form-control-sm armorName"  id="armorName${inputCount + 1}">
        </div>
        <div class="g-col-1">
            <input autocomplete="off" type="text" class="form-control form-control-sm weight armorWeight"
            onkeypress="return event.charCode >= 46 && event.charCode <= 57" id="armorWeight${inputCount + 1}">
        </div>
    `)
    .on("input", calcWeight)
    .append('div')
    .attr('class','g-col-1')
    .append('i')
    .attr('class', 'bi bi-x-lg mt-3 text-danger')
    .attr('style', 'cursor: pointer;')
    .attr('id', 'armorEqDel' + (inputCount + 1))
    .on('click', function() {
          inputGroup.remove();
          calcWeight();
        });

    }

armorEq = {
    const addInputButton = d3.select('#addArmorEqButton');
    addInputButton.on('click', () => addArmorEq() );

}

function addItemEq() {
      var inputContainer = d3.select('#miscEqContainer');
      var inputCount = inputContainer.selectAll('.grid').size();

    var inputGroup = inputContainer
      .append('div')
      .attr('class','grid align-content-center').attr('style','--bs-gap:0;--bs-columns:12;')
      .attr('id','miscEq'+(inputCount + 1))

    inputGroup
    .html(`
        <div class="g-col-1 mt-2">
            <input autocomplete="off" class="form-check-input miscMagical" type="checkbox" value=""  id="miscMagical${inputCount + 1}">
        </div>
        <div class="g-col-1 mt-2">
            <input autocomplete="off" class="form-check-input miscEquipped" type="checkbox" value="" id="miscEquipped${inputCount + 1}">
        </div>
        <div class="g-col-8">
            <input autocomplete="off" type="text" class="form-control form-control-sm miscName"  id="miscName${inputCount + 1}">
        </div>
        <div class="g-col-1">
            <input autocomplete="off" type="text" class="form-control form-control-sm weight miscWeight"
            onkeypress="return event.charCode >= 46 && event.charCode <= 57" id="miscWeight${inputCount + 1}">
        </div>
    `)
    .on("input", calcWeight)
    .append('div')
    .attr('class','g-col-1')
    .append('i')
    .attr('class', 'bi bi-x-lg mt-3 text-danger')
    .attr('style', 'cursor: pointer;')
    .attr('id', 'miscEqDel' + (inputCount + 1))
    .on('click', function() {
          inputGroup.remove();
          calcWeight();
        });

    }

miscEq = {
    const addInputButton = d3.select('#addItemEqButton');
    addInputButton.on('click', () => addItemEq() );

}
```

addWeaponEq = ƒ()

weaponEq = undefined

addArmorEq = ƒ()

armorEq = undefined

addItemEq = ƒ()

miscEq = undefined

```sourceCode javascript
function calcWeight () {
    const eq = d3.select('#equipment')
    const wArray = d3.selectAll('.weight')
    const totWField = d3.select('#totalWeight')

    var sum = 0

    wArray.each(function() {
        var value = +d3.select(this).property("value");
        sum += value;
      });

    totWField.property("value", sum);

}

totalW = {
    const eq = d3.select('#equipment');
    var inputs = eq.selectAll(".weight");

    inputs.on("input", calcWeight);
}
```

calcWeight = ƒ()

totalW = undefined

## Hirelings [Anchor](https://www.basicfantasy.org/srd/char_sheet.html\#hirelings)

Add Hireling

## Background [Anchor](https://www.basicfantasy.org/srd/char_sheet.html\#background-1)

## Misc. Notes [Anchor](https://www.basicfantasy.org/srd/char_sheet.html\#misc-notes)

```sourceCode javascript
function addHireling() {
      var inputContainer = d3.select('#hirelingsContainer');
      var inputCount = inputContainer.selectAll('.input-group').size();

      var inputGroup = inputContainer
        .append('div')
        .attr('class', 'input-group mb-2');

      inputGroup
        .append('input')
        .attr('autocomplete',"off")
        .attr('type', 'text')
        .attr('id', 'hireling' + (inputCount + 1))
        .attr('class', 'form-control rounded-start hirelings')
        .attr('placeholder', 'Hireling ' + (inputCount + 1));

      inputGroup
        .append('button')
        .attr('class', 'btn btn-danger delete-button rounded-end')
        .attr('type', 'button')
        .attr('id', 'hirelingDel' + (inputCount + 1))
        .text('-')
        .on('click', function() {
          inputGroup.remove();
        });
    }
hireling = {
      var addInputButton = d3.select('#addHirelingButton');
      addInputButton.on('click', () => addHireling() );
}
```

addHireling = ƒ()

hireling = undefined

```sourceCode javascript
import { calculateModifier, generalDice } from "./custom.js"
d3 = require('d3@7')

numberInputStr = d3.select("#strNum");
numberInputDex = d3.select("#dexNum");
numberInputCon = d3.select("#conNum");
numberInputInt = d3.select("#intNum");
numberInputWis = d3.select("#wisNum");
numberInputCha = d3.select("#chaNum");

outputStr = d3.select("#strMod");
outputDex = d3.select("#dexMod");
outputCon = d3.select("#conMod");
outputInt = d3.select("#intMod");
outputWis = d3.select("#wisMod");
outputCha = d3.select("#chaMod");

function updateOutput(inp, out) {
    const inputValue = inp.property("value");
    out.text(`( ${calculateModifier((Number(inputValue)))} )`);
}

b = {
outputStr.text(`( ${calculateModifier(Number(numberInputStr.property("value")))} )`)
outputDex.text(`( ${calculateModifier(Number(numberInputDex.property("value")))} )`)
outputCon.text(`( ${calculateModifier(Number(numberInputCon.property("value")))} )`)
outputInt.text(`( ${calculateModifier(Number(numberInputInt.property("value")))} )`)
outputWis.text(`( ${calculateModifier(Number(numberInputWis.property("value")))} )`)
outputCha.text(`( ${calculateModifier(Number(numberInputCha.property("value")))} )`)
}

a = {
numberInputStr.on("input", () => updateOutput(numberInputStr,outputStr));
numberInputDex.on("input", () => updateOutput(numberInputDex,outputDex));
numberInputCon.on("input", () => updateOutput(numberInputCon,outputCon));
numberInputInt.on("input", () => updateOutput(numberInputInt,outputInt));
numberInputWis.on("input", () => updateOutput(numberInputWis,outputWis));
numberInputCha.on("input", () => updateOutput(numberInputCha,outputCha));
}

function addInputField() {
      var inputContainer = d3.select('#inputContainer');
      var inputCount = inputContainer.selectAll('.input-group').size();

      var inputGroup = inputContainer
        .append('div')
        .attr('class', 'input-group mb-2');

      inputGroup
        .append('input')
        .attr('type', 'text')
        .attr('autocomplete',"off")
        .attr('id', 'language' + (inputCount + 1))
        .attr('class', 'form-control rounded-start lang')
        .attr('placeholder', 'Language ' + (inputCount + 1));

      inputGroup
        .append('button')
        .attr('class', 'btn btn-danger delete-button rounded-end')
        .attr('type', 'button')
        .attr('id', 'languageDel' + (inputCount + 1))
        .text('-')
        .on('click', function() {
          inputGroup.remove();
        });
    }
c = {
      var addInputButton = d3.select('#addInputButton');
      addInputButton.on('click', () => addInputField() );
}

function addSkill() {
      var inputContainer = d3.select('#inputContainerSkills');
      var inputCount = inputContainer.selectAll('.input-group').size();

      var inputGroup = inputContainer
        .append('div')
        .attr('class', 'input-group mb-2');

      inputGroup
        .append('input')
        .attr('autocomplete',"off")
        .attr('type', 'text')
        .attr('id', 'skill' + (inputCount + 1))
        .attr('class', 'form-control rounded-start oskill')
        .attr('placeholder', 'Skill ' + (inputCount + 1));

      inputGroup
        .append('button')
        .attr('class', 'btn btn-danger delete-button rounded-end')
        .attr('type', 'button')
        .attr('id', 'skillDel' + (inputCount + 1))
        .text('-')
        .on('click', function() {
          inputGroup.remove();
        });
    }
d = {
      var addInputButton = d3.select('#addSkillButton');
      addInputButton.on('click', () => addSkill() );

}

openLocks = {
    var but = d3.select('#thiefLocksButton');
    var out = d3.select('#thiefLocksOut');

    but.on('click', () => {
        var temp = generalDice(1,100,0);
        out.text(temp)
    });
}

traps = {
    var but = d3.select('#thiefTrapButton');
    var out = d3.select('#thiefTrapOut');

    but.on('click', () => {
        var temp = generalDice(1,100,0);
        out.text(temp)
    });
}

pocket = {
    var but = d3.select('#thiefPocketsButton');
    var out = d3.select('#thiefPocketsOut');

    but.on('click', () => {
        var temp = generalDice(1,100,0);
        out.text(temp)
    });
}

silently = {
    var but = d3.select('#thiefSilentButton');
    var out = d3.select('#thiefSilentOut');

    but.on('click', () => {
        var temp = generalDice(1,100,0);
        out.text(temp)
    });
}

climb = {
    var but = d3.select('#thiefClimbButton');
    var out = d3.select('#thiefClimbOut');

    but.on('click', () => {
        var temp = generalDice(1,100,0);
        out.text(temp)
    });
}

hide = {
    var but = d3.select('#thiefHideButton');
    var out = d3.select('#thiefHideOut');

    but.on('click', () => {
        var temp = generalDice(1,100,0);
        out.text(temp)
    });
}

listen = {
    var but = d3.select('#thiefListenButton');
    var out = d3.select('#thiefListenOut');

    but.on('click', () => {
        var temp = generalDice(1,100,0);
        out.text(temp)
    });
}
```

```javascript hljs
  import {calculateModifier as calculateModifier, generalDice as generalDice} from "./custom.js"

```

d3 = Object {format: ƒ(t), formatPrefix: ƒ(t, n), timeFormat: ƒ(t), timeParse: ƒ(t), utcFormat: ƒ(t), utcParse: ƒ(t), Adder: class, Delaunay: class, FormatSpecifier: ƒ(t), InternMap: class, InternSet: class, Node: ƒ(t), Path: class, Voronoi: class, ZoomTransform: ƒ(t, n, e), active: ƒ(t, n), arc: ƒ(), area: ƒ(t, n, e), areaRadial: ƒ(), ascending: ƒ(t, n), …}

numberInputStr = Vn {\_groups: Array(1), \_parents: Array(1)}

numberInputDex = Vn {\_groups: Array(1), \_parents: Array(1)}

numberInputCon = Vn {\_groups: Array(1), \_parents: Array(1)}

numberInputInt = Vn {\_groups: Array(1), \_parents: Array(1)}

numberInputWis = Vn {\_groups: Array(1), \_parents: Array(1)}

numberInputCha = Vn {\_groups: Array(1), \_parents: Array(1)}

outputStr = Vn {\_groups: Array(1), \_parents: Array(1)}

outputDex = Vn {\_groups: Array(1), \_parents: Array(1)}

outputCon = Vn {\_groups: Array(1), \_parents: Array(1)}

outputInt = Vn {\_groups: Array(1), \_parents: Array(1)}

outputWis = Vn {\_groups: Array(1), \_parents: Array(1)}

outputCha = Vn {\_groups: Array(1), \_parents: Array(1)}

updateOutput = ƒ(inp, out)

b = undefined

a = undefined

addInputField = ƒ()

c = undefined

addSkill = ƒ()

d = undefined

openLocks = undefined

traps = undefined

pocket = undefined

silently = undefined

climb = undefined

hide = undefined

listen = undefined

```sourceCode javascript
function savetoFile(){
    let char = {};

    // Name and basic info
    char.Name = d3.select('#Name').property("value")
    char.Class = d3.select('#charClass').select('dd').text();
    char.Race = d3.select('#charRace').select('dd').text();
    char.Level = d3.select('#charLevel').select('dd').text();
    char.Experience = d3.select('#charExperience').select('dd').text()

    char.HP = d3.select('#hp1').property('value');
    char.MaxHP = d3.select('#hp2').property('value');
    char.AC = d3.select('#ACinput').property('value');
    char.HD = d3.select('#HDinput').property('value');

    char.BAB = d3.select('#BABbox').text();
    char.Movement = d3.select('#MovementBox').text();
    char.Initiative = d3.select('#InitiativeBox').text();

    // Abilities
    char.Abilities = {};
    char.Abilities.Str = d3.select('#strNum').property('value' );
    char.Abilities.Dex = d3.select('#dexNum').property('value' );
    char.Abilities.Con = d3.select('#conNum').property('value');
    char.Abilities.Wis = d3.select('#wisNum').property('value' );
    char.Abilities.Int = d3.select('#intNum').property('value' );
    char.Abilities.Cha = d3.select('#chaNum').property('value' );

    //saves
    char.Saves = {};
    char.Saves.DRP = d3.select('#save-drpBox').property('value' );
    char.Saves.MW = d3.select('#save-wandBox').property('value' );
    char.Saves.Par = d3.select('#save-parBox').property('value');
    char.Saves.DB = d3.select('#save-dbBox').property('value');
    char.Saves.Spl = d3.select('#save-spellBox').property('value');

      // Thieving skills
    char.ThiefSkills = {};
    char.ThiefSkills.OpenLocks = d3.select('#thiefLocksInput ').property('value');
    char.ThiefSkills.RemoveTraps = d3.select('#thiefTrapInput ').property('value');
    char.ThiefSkills.PickPockets = d3.select('#thiefPocketsInput ').property('value');
    char.ThiefSkills.MoveSilent = d3.select('#thiefSilentInput ').property('value');
    char.ThiefSkills.ClimbWalls = d3.select('#thiefClimbInput ').property('value');
    char.ThiefSkills.Hide = d3.select('#thiefHideInput ').property('value');
    char.ThiefSkills.Listen = d3.select('#thiefListenInput ').property('value');

    // Langs and skills
    char.Languages = d3.selectAll(".lang").nodes().map((node) => node.value);
    char.OtherSkills = d3.selectAll(".oskill").nodes().map((node) => node.value);

    //attacks
    char.WeaponEq = []
    for (let i = 0; i < d3.selectAll(".weaponForm").size(); i++) {
        char.WeaponEq.push( {
            "name": d3.selectAll(".weaponForm").nodes().map((node) => node.value)[i],
            "attack": d3.selectAll(".attackForm").nodes().map((node) => node.value)[i],
            "damage": d3.selectAll(".damageForm").nodes().map((node) => node.value)[i],
            "S": d3.selectAll(".rangeSForm").nodes().map((node) => node.value)[i],
            "M": d3.selectAll(".rangeMForm").nodes().map((node) => node.value)[i],
            "L": d3.selectAll(".rangeLForm").nodes().map((node) => node.value)[i],
            "notes": d3.selectAll(".notesForm").nodes().map((node) => node.value)[i]}
    )};

    //ammo
    char.AmmoEq = []
    for (let i = 0; i < d3.selectAll(".ammoForm").size(); i++) {
        char.AmmoEq.push( {
            "name": d3.selectAll(".ammoForm").nodes().map((node) => node.value)[i],
            "count": d3.selectAll(".countForm").nodes().map((node) => node.value)[i],
            "damage": d3.selectAll(".ammoDmgForm").nodes().map((node) => node.value)[i],
            "notes": d3.selectAll(".ammo-notesForm").nodes().map((node) => node.value)[i]}
    )};

    char.Turning =  d3.selectAll(".turningForm").nodes().map((node) => node.value);

    // spells
    char.Spells = [];
    for (let i = 0; i < d3.selectAll(".spell-name").size(); i++) {
        char.Spells.push( {
            "spellName": d3.selectAll(".spell-name").nodes().map((node) => node.value)[i],
            "spellLvl": d3.selectAll(".spell-level").nodes().map((node) => node.value)[i],
            "prep": d3.selectAll(".spell-prep").nodes().map((node) => node.value)[i]}
    )};

    // Currency
    char.Equipment={}
    char.Equipment.Currency  = {}
    char.Equipment.Currency.pp = d3.select('#PPbox').text()
    char.Equipment.Currency.gp = d3.select('#GPbox').text()
    char.Equipment.Currency.ep = d3.select('#EPbox').text()
    char.Equipment.Currency.sp = d3.select('#SPbox').text()
    char.Equipment.Currency.cp = d3.select('#CPbox').text()

    // Equipment
    char.Equipment.Weapons = [];
    for (let i = 0; i < d3.selectAll(".weaponsEqMag").size(); i++) {
        char.Equipment.Weapons.push( {
            "magic": d3.selectAll(".weaponsEqMag").nodes().map((node) => node.checked)[i],
            "equipped": d3.selectAll(".weaponsEqEq").nodes().map((node) => node.checked)[i],
            "name": d3.selectAll(".weaponsEqName").nodes().map((node) => node.value)[i],
            "weight": d3.selectAll(".weaponsEqWeight").nodes().map((node) => node.value)[i]
            }
    )};

    char.Equipment.Armor = [];
    for (let i = 0; i < d3.selectAll(".armorMagical").size(); i++) {
        char.Equipment.Armor.push( {
            "magic": d3.selectAll(".armorMagical").nodes().map((node) => node.checked)[i],
            "equipped": d3.selectAll(".armorEquipped").nodes().map((node) => node.checked)[i],
            "name": d3.selectAll(".armorName").nodes().map((node) => node.value)[i],
            "weight": d3.selectAll(".armorWeight").nodes().map((node) => node.value)[i]
            }
    )};

    char.Equipment.Misc = [];
    for (let i = 0; i < d3.selectAll(".miscMagical").size(); i++) {
        char.Equipment.Misc.push( {
            "magic": d3.selectAll(".miscMagical").nodes().map((node) => node.checked)[i],
            "equipped": d3.selectAll(".miscEquipped").nodes().map((node) => node.checked)[i],
            "name": d3.selectAll(".miscName").nodes().map((node) => node.value)[i],
            "weight": d3.selectAll(".miscWeight").nodes().map((node) => node.value)[i]
            }
    )};

    //Notes
    char.Hirelings = d3.selectAll(".hirelings").nodes().map((node) => node.value);
    char.Background = d3.select('#background').text()
    char.MiscNotes = d3.select('#miscNotes').text()

    return char
}

function downloadJson() {
      // Generate JSON data
  var jsonData = savetoFile();

  // Convert JSON to string
  var jsonString = JSON.stringify(jsonData, null, 2);

  // Create a Blob from the JSON string
  var blob = new Blob([jsonString], { type: "application/json" });

  // Create a temporary URL for the Blob
  var url = URL.createObjectURL(blob);

  // Create a link element
  var link = document.createElement("a");

  // Set the link's properties
  link.href = url;
  link.download = "character.json";

  // Simulate a click event on the link to trigger the download
  link.click();

  // Clean up the temporary URL
  URL.revokeObjectURL(url);
}
```

savetoFile = ƒ()

downloadJson = ƒ()

Download Character

```sourceCode javascript
dchar = {
d3.select("#downloadCharButton").on("click", downloadJson);
}
// savetoFile()
```

dchar = undefined

[23Dungeon Maker](https://www.basicfantasy.org/srd/appendixMapmaker.html)