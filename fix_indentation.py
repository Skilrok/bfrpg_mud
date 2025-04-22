import os


def fix_indentation_error():
    """Fix the unexpected indent error in the WebSocket code"""
    websocket_file = os.path.join("app", "websockets", "__init__.py")

    if not os.path.exists(websocket_file):
        print(f"Error: WebSocket file not found: {websocket_file}")
        return False

    with open(websocket_file, "r") as f:
        lines = f.readlines()

    # Find and fix the indentation issue in line 511
    for i, line in enumerate(lines):
        if "response = await command_registry.execute_command(ctx)" in line:
            # This is the problematic line with incorrect indentation
            correct_indent = line.lstrip()  # Remove leading whitespace
            lines[i] = (
                " " * 32 + correct_indent
            )  # Add exactly 32 spaces (8 tabs) of indentation
            print(f"Fixed indentation at line {i+1}")

    # Write back the fixed content
    with open(websocket_file, "w") as f:
        f.writelines(lines)

    print("File updated successfully")
    return True


if __name__ == "__main__":
    print("Fixing indentation error in WebSocket handler...")
    success = fix_indentation_error()

    if success:
        print("Indentation error fixed. You can now restart the server.")
    else:
        print("Failed to fix the indentation error.")
