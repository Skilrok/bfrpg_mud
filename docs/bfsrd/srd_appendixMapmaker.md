1. [Appendix](https://www.basicfantasy.org/srd/appendix_interactive.html)
2. [23Dungeon Maker](https://www.basicfantasy.org/srd/appendixMapmaker.html)

[Basic Fantasy RPG, 4th edition](https://www.basicfantasy.org/srd/)

[Toggle dark mode](https://www.basicfantasy.org/srd/appendixMapmaker.html "Toggle dark mode")

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

# 23Dungeon Maker

**How to use**

- Input the size of the square grid to create the drawing canvas (note this erases anything you may have already drawn)
- Click or drag to create rooms and hallways. The click toggles between white and blue squares.
- Click on a square and then type a character on your keyboard to annotate a square with a letter or number (multiple characters are possible).
- Right click on a square to erase existing text.

```sourceCode javascript
viewof gridsize = Inputs.text({placeholder:"Grid Size"})

viewof grid1 = Inputs.button("Create Grid", {reduce: () =>  draw(Number(gridsize))})
```

gridsize = ""

Create Grid

grid1 = 0

```sourceCode javascript
size = 30

viewof form = Inputs.form(
  {
    button1: "  ",
    button2: Inputs.button("Delete Grid", {reduce: () => resetGrid()})
  },
  {
    template: (formParts) => htl.html`
     <div>
       <h3></h3>
       <div style="
         width: 400px;
         display: flex;
       ">
         ${Object.values(formParts)}
       </div>
     </div>`
  }
)
```

size = 30

Delete Grid

form = Object {button1: undefined, button2: 0}

```sourceCode javascript
Inputs.button("Export to PNG", {reduce: () => exportToImage(size, "png", Number(gridsize), grid1.col, grid1.chars)})
```

Export to PNG

[22Interactive tools](https://www.basicfantasy.org/srd/appendix_interactive.html)

[24Character Sheet](https://www.basicfantasy.org/srd/char_sheet.html)