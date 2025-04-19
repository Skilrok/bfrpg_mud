import pytest
from app.commands.character_commands import get_valid_classes_for_race
from app.models.character import CharacterRace, CharacterClass

def test_get_valid_classes_for_race():
    """Test that get_valid_classes_for_race returns the correct classes for each race"""
    
    # Test human valid classes
    human_classes = get_valid_classes_for_race(CharacterRace.HUMAN)
    assert CharacterClass.FIGHTER in human_classes
    assert CharacterClass.CLERIC in human_classes
    assert CharacterClass.MAGIC_USER in human_classes
    assert CharacterClass.THIEF in human_classes
    assert len(human_classes) == 4
    
    # Test dwarf valid classes
    dwarf_classes = get_valid_classes_for_race(CharacterRace.DWARF)
    assert CharacterClass.FIGHTER in dwarf_classes
    assert CharacterClass.CLERIC in dwarf_classes
    assert CharacterClass.THIEF in dwarf_classes
    assert CharacterClass.MAGIC_USER not in dwarf_classes
    assert len(dwarf_classes) == 3
    
    # Test elf valid classes
    elf_classes = get_valid_classes_for_race(CharacterRace.ELF)
    assert CharacterClass.FIGHTER_MAGIC_USER in elf_classes
    assert len(elf_classes) == 1
    
    # Test halfling valid classes
    halfling_classes = get_valid_classes_for_race(CharacterRace.HALFLING)
    assert CharacterClass.FIGHTER in halfling_classes
    assert CharacterClass.THIEF in halfling_classes
    assert len(halfling_classes) == 2
    
    # Test invalid race
    invalid_classes = get_valid_classes_for_race("INVALID_RACE")
    assert len(invalid_classes) == 0 