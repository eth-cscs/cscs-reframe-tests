import pytest
from unittest.mock import patch
import sys
from reframe_reporter.cli import main

def run_main(args):
    """Helper to run the main function with provided arguments."""
    with patch.object(sys, 'argv', ['reframe_reporter', *args]):
        main()

def test_cli_mutual_exclusivity():
    """Verify that --matrix-mode and --matrix-tag cannot be used together."""
    with pytest.raises(Exception) as excinfo:
        run_main(["--matrix-mode", "a:b:c", "--matrix-tag", "d:e:f"])
    assert "mutually exclusive" in str(excinfo.value).lower()

def test_cli_missing_flags():
    """Verify that running without any matrix flags fails."""
    with pytest.raises(Exception) as excinfo:
        run_main(["-c", "checks"])
    assert "must be specified" in str(excinfo.value).lower()

def test_cli_invalid_target_syntax():
    """Verify that targets missing components (3-part syntax) fail validation."""
    with pytest.raises(Exception) as excinfo:
        run_main(["--matrix-mode", "label:system"])
    assert "3-part format" in str(excinfo.value).lower()

def test_cli_removed_flags():
    """Verify that old flags (--system, --mode, --tag) are no longer accepted."""
    # Argparse will exit with error or raise SystemExit for unknown args
    with pytest.raises(SystemExit):
        run_main(["--system", "daint"])
