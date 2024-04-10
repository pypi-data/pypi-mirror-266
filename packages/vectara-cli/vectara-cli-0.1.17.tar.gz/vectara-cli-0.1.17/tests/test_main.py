# test_main.py

from unittest.mock import patch
import sys
import pytest
from vectara_cli.main import main

def test_valid_command():
    # Simulate running the script with a valid command
    with patch.object(sys, "argv", ["main.py", "help"]):
        main()

    # Add assertions to verify expected behavior (e.g., check if index_document.main was called)

def test_unknown_command():
    # Simulate running the script with an unknown command
    with patch.object(sys, "argv", ["main.py", "unknown-command"]):
        with pytest.raises(SystemExit) as exc_info:
            main()

    # Verify that the script exits with a non-zero status
    assert exc_info.value.code != 0

    # Add additional assertions if needed

# Add more test cases as necessary
