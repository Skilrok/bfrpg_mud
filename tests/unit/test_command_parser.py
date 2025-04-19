"""
Unit tests for the command parser functionality.
"""

import pytest

from app.commands.parser import extract_target, parse_command, parse_direction


class TestCommandParser:
    """Test suite for command parser functions."""

    def test_parse_command_basic(self):
        """Test basic command parsing."""
        # Test basic command parsing
        cmd, args = parse_command("look")
        assert cmd == "look"
        assert args == []

    def test_parse_command_with_args(self):
        """Test command parsing with arguments."""
        # Test command with arguments
        cmd, args = parse_command("look sword")
        assert cmd == "look"
        assert args == ["sword"]

        # Test command with multiple arguments
        cmd, args = parse_command("look rusty sword")
        assert cmd == "look"
        assert args == ["rusty", "sword"]

    def test_parse_command_with_quoted_args(self):
        """Test command parsing with quoted arguments."""
        # Test with quoted arguments
        cmd, args = parse_command('say "Hello, world!"')
        assert cmd == "say"
        assert args == ["Hello, world!"]

        # Test with multiple quoted arguments
        cmd, args = parse_command('give "gold coin" to "old man"')
        assert cmd == "give"
        assert args == ["gold coin", "to", "old man"]

    def test_parse_command_edge_cases(self):
        """Test command parsing edge cases."""
        # Test empty command
        cmd, args = parse_command("")
        assert cmd == ""
        assert args == []

        # Test with extra whitespace
        cmd, args = parse_command("  look   around  ")
        assert cmd == "look"
        assert args == ["around"]

        # Test with only whitespace
        cmd, args = parse_command("    ")
        assert cmd == ""
        assert args == []

    @pytest.mark.parametrize(
        "input_str, expected_dir",
        [
            ("north", "north"),
            ("n", "north"),
            ("south", "south"),
            ("s", "south"),
            ("east", "east"),
            ("e", "east"),
            ("west", "west"),
            ("w", "west"),
            ("up", "up"),
            ("u", "up"),
            ("down", "down"),
            ("d", "down"),
            ("northeast", "northeast"),
            ("ne", "northeast"),
            ("southwest", "southwest"),
            ("sw", "southwest"),
            ("invalid", None),
        ],
    )
    def test_parse_direction(self, input_str, expected_dir):
        """Test direction parsing with various inputs."""
        assert parse_direction(input_str) == expected_dir

    @pytest.mark.parametrize(
        "command, args, expected",
        [
            ("look", [], None),
            ("look", ["sword"], "sword"),
            ("look", ["rusty", "sword"], "rusty sword"),
            ("examine", ["old", "rusty", "sword"], "old rusty sword"),
            ("get", ["all"], "all"),
            ("talk", ["to", "guard"], "guard"),
        ],
    )
    def test_extract_target(self, command, args, expected):
        """Test target extraction from command arguments."""
        assert extract_target(command, args) == expected
