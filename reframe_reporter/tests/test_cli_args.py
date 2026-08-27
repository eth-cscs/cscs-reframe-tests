from unittest.mock import patch
import sys
from reframe_reporter.cli import parse_args

def test_parse_args_default_filename():
    """Verify that the default filename is used when -f is not provided."""
    with patch.object(sys, 'argv', ['reframe_reporter', '--matrix-mode', 'a:b:c']):
        processed, args = parse_args()
        assert processed.filename == "eligible_tests.md"
        assert processed.explicit_filename is False

def test_parse_args_custom_filename():
    """Verify that a custom filename is used when -f is provided."""
    with patch.object(sys, 'argv', ['reframe_reporter', '--matrix-mode', 'a:b:c', '-f', 'my_report.md']):
        processed, args = parse_args()
        assert processed.filename == "my_report.md"
        assert processed.explicit_filename is True

def test_parse_args_custom_filename_with_extension():
    """Verify that a custom filename with an extension is used as-is."""
    with patch.object(sys, 'argv', ['reframe_reporter', '--matrix-mode', 'a:b:c', '-f', 'test.txt']):
        processed, args = parse_args()
        assert processed.filename == "test.txt"
        assert processed.explicit_filename is True

