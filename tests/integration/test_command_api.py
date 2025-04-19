"""
Integration tests for the command API endpoints.
"""

from unittest.mock import patch

import pytest

from app.commands.base import CommandContext, CommandHandler, CommandResponse
from app.commands.registry import command_registry
from app.models import CommandHistory


class TestCommandAPI:
    """Integration tests for the command API endpoints."""

    @pytest.fixture
    def command_endpoint(self):
        """Get the command endpoint."""
        return "/api/commands/"

    def test_command_api_unauthorized(self, client, command_endpoint):
        """Test that unauthorized requests are rejected."""
        response = client.post(command_endpoint, json={"command": "help"})
        assert response.status_code == 401

    def test_command_api_empty_command(self, client, command_endpoint, auth_headers, mock_current_user):
        """Test that empty commands are rejected."""
        response = client.post(
            command_endpoint, json={"command": ""}, headers=auth_headers
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "No command provided" in data["detail"]

    def test_command_api_help(
        self, client, command_endpoint, auth_headers, test_db, test_user, mock_current_user
    ):
        """Test the help command through the API."""
        # Use a mock to avoid dependency on actual command implementation
        with patch.object(command_registry, "execute_command") as mock_execute:
            # Set up the mock response
            mock_execute.return_value = CommandResponse(
                success=True,
                message="Help information",
                data={"commands": [{"name": "help", "help": "Show help"}]},
            )

            # Make the request
            response = client.post(
                command_endpoint, json={"command": "help"}, headers=auth_headers
            )

            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Help information"
            assert "data" in data
            assert "commands" in data["data"]

            # Verify command was logged to history
            history = (
                test_db.query(CommandHistory)
                .filter(CommandHistory.user_id == test_user.id)
                .first()
            )
            assert history is not None
            assert history.command == "help"

    def test_command_api_with_character(
        self, client, command_endpoint, auth_headers, test_db, test_user, test_character, mock_current_user
    ):
        """Test command execution with a specific character."""
        # Use a mock to avoid dependency on actual command implementation
        with patch.object(command_registry, "execute_command") as mock_execute:
            # Set up the mock response
            mock_execute.return_value = CommandResponse(
                success=True,
                message="Look command executed",
                data={"room_id": 1, "room_name": "Test Room"},
            )

            # Make the request
            response = client.post(
                command_endpoint,
                json={"command": "look", "character_id": test_character.id},
                headers=auth_headers,
            )

            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Look command executed"

            # Verify command was logged to history with character ID
            history = (
                test_db.query(CommandHistory)
                .filter(
                    CommandHistory.user_id == test_user.id,
                    CommandHistory.character_id == test_character.id,
                )
                .first()
            )
            assert history is not None
            assert history.command == "look"

    def test_command_api_error_handling(self, client, command_endpoint, auth_headers, mock_current_user):
        """Test error handling in the command API."""
        # Use a mock to simulate an error
        with patch.object(command_registry, "execute_command") as mock_execute:
            # Set up the mock to raise an exception
            mock_execute.side_effect = ValueError("Test error")

            # Make the request
            response = client.post(
                command_endpoint, json={"command": "error"}, headers=auth_headers
            )

            # Verify response
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "Error processing command" in data["detail"]

    @pytest.mark.parametrize(
        "command,args",
        [
            ("look", []),
            ("inventory", []),
            ("help", ["look"]),
            ("go", ["north"]),
        ],
    )
    def test_command_api_various_commands(
        self, client, command_endpoint, auth_headers, test_db, test_user, command, args, mock_current_user
    ):
        """Test various commands through the API."""
        # Use a mock to avoid dependency on actual command implementation
        with patch.object(command_registry, "execute_command") as mock_execute:
            # Set up the mock response
            mock_execute.return_value = CommandResponse(
                success=True,
                message=f"{command} command executed",
                data={"command": command, "args": args},
            )

            # Construct command string
            command_str = command
            if args:
                command_str += " " + " ".join(args)

            # Make the request
            response = client.post(
                command_endpoint, json={"command": command_str}, headers=auth_headers
            )

            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert f"{command} command executed" in data["message"]

            # Verify command context construction
            called_context = mock_execute.call_args[0][0]
            assert called_context.command == command
            assert called_context.args == args
            assert called_context.raw_input == command_str

    @pytest.mark.xfail(reason="WebSocket testing not fully implemented")
    def test_command_websocket(self, client):
        """Test the WebSocket command endpoint."""
        # This test is marked as expected to fail until WebSocket testing is implemented
        # It would test the WebSocket endpoint for command processing
        assert False, "WebSocket testing not implemented"
