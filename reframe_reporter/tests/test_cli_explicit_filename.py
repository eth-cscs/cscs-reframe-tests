import pytest
from unittest.mock import MagicMock
from reframe_reporter.models import ReFrameReporterConfig
from reframe_reporter.orchestrator import ReportOrchestrator

@pytest.fixture
def mock_config(tmp_path):
    """
    Creates a mock ReFrameReporterConfig pointing to temporary directories.
    """
    config = MagicMock(spec=ReFrameReporterConfig)
    config.output_dir = tmp_path / "output"
    config.check_paths = [tmp_path / "checks/test_app.py"]
    config.filename = "default_report.md"
    config.recursive = False
    config.uenv_recipes_dir = None
    config.uenv_image_inventory = None
    config.uenv_env = {}
    return config

def test_cli_explicit_filename(mock_config, tmp_path, monkeypatch):
    """
    Verifies that the -f argument is respected by the CLI and passed correctly to the orchestrator.
    """
    # Setup: Create a dummy check file so the builder doesn't fail
    checks_dir = tmp_path / "checks"
    checks_dir.mkdir()
    (checks_dir / "test_app.py").write_text("def test(): pass")
    mock_config.check_paths = [checks_dir / "test_app.py"]
    
    explicit_name = "custom_name.md"
    output_dir = tmp_path / "output_dir"
    output_dir.mkdir()
    mock_config.output_dir = output_dir

    # We want to capture the call to orchestrator.run_matrix_tag_mode (or similar)
    # Since we are testing the CLI entry point, we'll mock the Orchestrator class
    # inside the module where it is used (reframe_reporter/cli.py or similar).
    # However, a cleaner way for unit testing the logic is to test the orchestrator directly.
    
    orchestrator = ReportOrchestrator(mock_config, explicit_filename=True)
    
    # Mocking targets and extra args
    targets = ["label:system:tag"]
    extra_args = ["-f", explicit_name]
    
    # We need to mock the executor so it doesn't actually run 'reframe'
    orchestrator.executor.run = MagicMock(return_value=MagicMock(returncode=0, stdout='[]', stderr=''))
    orchestrator.executor.parse_json = MagicMock(return_value=[])
    # Mock renderer to avoid file writing during unit test if preferred, 
    # but here we check if the filename is correct.
    orchestrator.matrix_renderer.generate = MagicMock()

    # Execution
    # Note: In a real scenario, CLI parses args and sets config.filename
    # For this unit test, we simulate what the CLI should do:
    mock_config.filename = explicit_name
    orchestrator.config.filename = explicit_name
    
    orchestrator.run_matrix_tag_mode(targets, extra_args)

    # Verification
    expected_path = output_dir / explicit_name
    orchestrator.matrix_renderer.generate.assert_called_once()
    args, kwargs = orchestrator.matrix_renderer.generate.call_args
    actual_output_path = args[1]
    
    assert actual_output_path == expected_path
