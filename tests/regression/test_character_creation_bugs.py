"""
Regression tests for character creation bugs.

These tests verify that previously fixed bugs in character creation remain fixed.
"""

from unittest.mock import patch

import pytest

from app.commands.character_commands import creation_state_store
from app.constants import CharacterClass, CharacterRace
from app.models import Character, User


@pytest.mark.regression
class TestCharacterCreationRegression:
    """
    Regression tests for character creation functionality.

    These tests specifically target bugs that have been fixed in the past
    to ensure they don't reappear.
    """

    def test_character_name_uniqueness_bug(
        self, client, test_db, auth_headers, test_user
    ):
        """
        Test that character names must be unique per user.

        Regression test for bug #142: Users could create multiple characters with the same name.
        """
        # Create first character
        first_char_data = {
            "name": "UniqueCharTest",
            "race": CharacterRace.HUMAN.value,
            "character_class": CharacterClass.FIGHTER.value,
            "strength": 14,
            "intelligence": 10,
            "wisdom": 12,
            "dexterity": 13,
            "constitution": 15,
            "charisma": 8,
        }

        # Create first character
        response = client.post(
            "/api/characters/", json=first_char_data, headers=auth_headers
        )
        assert response.status_code == 200

        # Try to create second character with same name
        second_char_data = first_char_data.copy()
        second_char_data["intelligence"] = 12  # Change some stat to make it different

        response = client.post(
            "/api/characters/", json=second_char_data, headers=auth_headers
        )

        # Should be rejected with 400 Bad Request
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

        # Verify only one character with that name exists
        characters = (
            test_db.query(Character)
            .filter(
                Character.user_id == test_user.id, Character.name == "UniqueCharTest"
            )
            .all()
        )
        assert len(characters) == 1

    def test_race_class_compatibility_bug(self, client, auth_headers):
        """
        Test that incompatible race/class combinations are rejected.

        Regression test for bug #156: Character creation allowed invalid race/class combinations.
        """
        # Try to create a halfling magic-user (invalid combination)
        char_data = {
            "name": f"InvalidCombo",
            "race": CharacterRace.HALFLING.value,
            "character_class": CharacterClass.MAGIC_USER.value,
            "strength": 14,
            "intelligence": 16,  # High intelligence for magic-user
            "wisdom": 12,
            "dexterity": 13,
            "constitution": 15,
            "charisma": 8,
        }

        response = client.post("/api/characters/", json=char_data, headers=auth_headers)

        # Should be rejected
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()
        assert "combination" in response.json()["detail"].lower()

    def test_creation_state_cleanup_bug(self, client, test_db, auth_headers, test_user):
        """
        Test that creation state is properly cleaned up after character creation.

        Regression test for bug #173: Character creation state was not properly cleaned up,
        causing subsequent character creations to fail.
        """
        # Mock the creation state store with a fake entry
        user_id = test_user.id
        creation_state_store[user_id] = {
            "creation_state": "race_selection",
            "name": "AbandonedCharacter",
        }

        # Create a new character
        char_data = {
            "name": f"CleanupTest",
            "race": CharacterRace.HUMAN.value,
            "character_class": CharacterClass.FIGHTER.value,
            "strength": 14,
            "intelligence": 10,
            "wisdom": 12,
            "dexterity": 13,
            "constitution": 15,
            "charisma": 8,
        }

        response = client.post("/api/characters/", json=char_data, headers=auth_headers)

        # Should succeed despite existing creation state
        assert response.status_code == 200

        # Verify creation state was cleaned up
        assert user_id not in creation_state_store

    @pytest.mark.parametrize(
        "stat,value",
        [
            ("strength", 3),  # Minimum allowed
            ("intelligence", 18),  # Maximum allowed
            ("wisdom", 0),  # Too low
            ("dexterity", 19),  # Too high
            ("constitution", -1),  # Negative
            ("charisma", "abc"),  # Non-numeric
        ],
    )
    def test_ability_score_validation_bug(self, client, auth_headers, stat, value):
        """
        Test validation of ability scores.

        Regression test for bug #187: Character creation allowed invalid ability scores.
        """
        # Create character data with the test stat
        char_data = {
            "name": f"StatTest{stat}",
            "race": CharacterRace.HUMAN.value,
            "character_class": CharacterClass.FIGHTER.value,
            "strength": 14,
            "intelligence": 10,
            "wisdom": 12,
            "dexterity": 13,
            "constitution": 15,
            "charisma": 8,
        }

        # Override the test stat
        char_data[stat] = value

        response = client.post("/api/characters/", json=char_data, headers=auth_headers)

        # Valid values should be accepted, invalid ones rejected
        if isinstance(value, int) and 3 <= value <= 18:
            assert response.status_code == 200
        else:
            assert response.status_code == 400
            assert stat in response.json()["detail"].lower()

    def test_deleted_user_character_cleanup_bug(self, test_db):
        """
        Test that characters are deleted when a user is deleted.

        Regression test for bug #203: Character records remained in the database
        after a user was deleted, causing orphaned records.
        """
        # Create a test user
        user = User(
            username="delete_test_user",
            email="delete_test@example.com",
            hashed_password="test_hash",
            is_active=True,
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Create a character for this user
        character = Character(
            name="DeleteTestChar",
            description="A test character",
            race=CharacterRace.HUMAN.value,
            character_class=CharacterClass.FIGHTER.value,
            level=1,
            experience=0,
            strength=12,
            intelligence=10,
            wisdom=10,
            dexterity=10,
            constitution=10,
            charisma=10,
            hit_points=8,
            armor_class=10,
            user_id=user.id,
        )
        test_db.add(character)
        test_db.commit()

        # Verify character exists
        char_check = (
            test_db.query(Character).filter(Character.user_id == user.id).first()
        )
        assert char_check is not None

        # Delete the user
        test_db.delete(user)
        test_db.commit()

        # Verify no orphaned characters exist
        orphaned_chars = (
            test_db.query(Character).filter(Character.user_id == user.id).all()
        )
        assert len(orphaned_chars) == 0
