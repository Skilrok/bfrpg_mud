"""
Unit tests for the command registry functionality.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.commands.base import CommandContext, CommandHandler, CommandResponse
from app.commands.registry import CommandRegistry


class TestCommandHandler(CommandHandler):
    """Test command handler for unit tests"""

    name = "test"
    aliases = ["t", "tst"]
    help_text = "Test command for unit testing. Usage: test [arg]"

    async def execute(self, ctx: CommandContext) -> CommandResponse:
        """Test command execution"""
        return CommandResponse(
            success=True,
            message=f"Test command executed with args: {ctx.args}",
            data={"args": ctx.args},
        )


class AliasCommandHandler(CommandHandler):
    """Test command handler with aliases"""

    name = "alias"
    aliases = ["a", "als"]
    help_text = "Test alias command. Usage: alias [arg]"

    async def execute(self, ctx: CommandContext) -> CommandResponse:
        """Test command execution"""
        return CommandResponse(
            success=True,
            message=f"Alias command executed with args: {ctx.args}",
            data={"args": ctx.args},
        )


class ErrorCommandHandler(CommandHandler):
    """Test command that raises an exception"""

    name = "error"
    aliases = ["err"]
    help_text = "Test error handling. Usage: error"

    async def execute(self, ctx: CommandContext) -> CommandResponse:
        """Test command that raises an exception"""
        raise ValueError("Test exception")


class TestCommandRegistry:
    """Test suite for the command registry."""

    @pytest.fixture
    def registry(self):
        """Create a fresh command registry for each test."""
        return CommandRegistry()

    @pytest.fixture
    def populated_registry(self, registry):
        """Create a registry populated with test commands."""
        registry.register(TestCommandHandler)
        registry.register(AliasCommandHandler)
        registry.register(ErrorCommandHandler)
        return registry

    def test_register_command(self, registry):
        """Test registering a command handler."""
        # Register a test command
        registry.register(TestCommandHandler)

        # Verify it was registered
        assert "test" in registry._commands
        assert isinstance(registry._commands["test"], TestCommandHandler)

        # Verify aliases were registered
        assert "t" in registry._command_aliases
        assert "tst" in registry._command_aliases
        assert registry._command_aliases["t"] == "test"
        assert registry._command_aliases["tst"] == "test"

    def test_get_handler(self, populated_registry):
        """Test getting a command handler by name or alias."""
        # Test getting by primary name
        handler = populated_registry.get_handler("test")
        assert handler is not None
        assert handler.name == "test"

        # Test getting by alias
        handler = populated_registry.get_handler("t")
        assert handler is not None
        assert handler.name == "test"

        # Test getting a non-existent command
        handler = populated_registry.get_handler("nonexistent")
        assert handler is None

    def test_get_available_commands(self, populated_registry):
        """Test getting the set of available command names."""
        commands = populated_registry.get_available_commands()
        assert isinstance(commands, set)
        assert "test" in commands
        assert "alias" in commands
        assert "error" in commands
        assert len(commands) == 3

    def test_get_command_list(self, populated_registry):
        """Test getting the list of command handlers."""
        command_list = populated_registry.get_command_list()
        assert isinstance(command_list, list)
        assert len(command_list) == 3

        # Check command names
        command_names = {cmd.name for cmd in command_list}
        assert "test" in command_names
        assert "alias" in command_names
        assert "error" in command_names

    @pytest.mark.asyncio
    async def test_execute_command_success(self, populated_registry):
        """Test successful command execution."""
        # Create a context for the test command
        ctx = CommandContext(
            command="test", args=["arg1", "arg2"], raw_input="test arg1 arg2"
        )

        # Execute the command
        response = await populated_registry.execute_command(ctx)

        # Verify the response
        assert response.success is True
        assert "Test command executed with args" in response.message
        assert response.data["args"] == ["arg1", "arg2"]

    @pytest.mark.asyncio
    async def test_execute_command_by_alias(self, populated_registry):
        """Test command execution using an alias."""
        # Create a context for the alias command
        ctx = CommandContext(
            command="a", args=["arg1", "arg2"], raw_input="a arg1 arg2"
        )

        # Execute the command
        response = await populated_registry.execute_command(ctx)

        # Verify the response
        assert response.success is True
        assert "Alias command executed with args" in response.message
        assert response.data["args"] == ["arg1", "arg2"]

    @pytest.mark.asyncio
    async def test_execute_command_empty(self, populated_registry):
        """Test executing an empty command."""
        # Create a context with empty command
        ctx = CommandContext(command="", args=[], raw_input="")

        # Execute the command
        response = await populated_registry.execute_command(ctx)

        # Verify the response
        assert response.success is False
        assert "No command specified" in response.message
        assert len(response.errors) > 0

    @pytest.mark.asyncio
    async def test_execute_command_not_found(self, populated_registry):
        """Test executing a non-existent command."""
        # Create a context with non-existent command
        ctx = CommandContext(command="nonexistent", args=[], raw_input="nonexistent")

        # Execute the command
        response = await populated_registry.execute_command(ctx)

        # Verify the response
        assert response.success is False
        assert "Unknown command" in response.message
        assert len(response.errors) > 0
        assert "not found" in response.errors[0]

    @pytest.mark.asyncio
    async def test_execute_command_error(self, populated_registry):
        """Test executing a command that raises an exception."""
        # Create a context for the error command
        ctx = CommandContext(command="error", args=[], raw_input="error")

        # Execute the command
        response = await populated_registry.execute_command(ctx)

        # Verify the response
        assert response.success is False
        assert "An error occurred" in response.message
        assert len(response.errors) > 0
        assert "Test exception" in response.errors[0]
