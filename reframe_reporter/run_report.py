import sys
import os

# Ensure the parent directory is in sys.path so we can import reframe_reporter as a package.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

try:
    from cscs_reframe_tests.reframe_reporter.cli import main
except ImportError:
    # Fallback for running the script directly from within the package directory
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from reframe_reporter.cli import main

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Execution Error: {e}")
        sys.exit(1)
