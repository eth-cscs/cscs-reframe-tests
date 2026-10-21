import pytest
import os
import subprocess
from pathlib import Path

@pytest.fixture
def project_root():
    return Path(__file__).resolve().parents[2]

@pytest.fixture
def snapshot_dir(project_root):
    return project_root / "reframe_reporter" / "snapshots"

def run_cli(args, project_root):
    """Helper to run the CLI via subprocess from the project root."""
    cmd = [
        "python3",
        str(project_root / "reframe_reporter" / "run_report.py"),
        *args
    ]
    env = os.environ.copy()
    print(f"\nExecuting: {' '.join(map(str, cmd))}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(project_root))
    if result.returncode != 0:
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        raise RuntimeError(f"CLI failed with return code {result.returncode}")
    return result

def normalize_content(content):
    """Removes the timestamp line to allow stable comparisons."""
    import re
    return re.sub(r".*Generated: `.*?`.*\n?", "", content).strip()

def test_mode_matrix_snapshots(snapshot_dir, project_root):
    """Tests Mode Matrix against baseline MD using real CLI execution."""
    args = [
        "--matrix-mode", "prod:daint:production,maint:daint:maintenance",
        "-C", str(project_root / "config" / "cscs.py"),
        "-c", str(project_root / "checks"),
        "-o", snapshot_dir,
        "-f", "eligible_tests_mode-matrix_snapshot.md"
    ]
    output_md_path = snapshot_dir / "eligible_tests_mode-matrix_snapshot.md"
    baseline_md_path = snapshot_dir / "eligible_tests_mode-matrix_baseline.md"

    baseline_content = normalize_content(baseline_md_path.read_text()) if baseline_md_path.exists() else None

    run_cli(args, project_root)

    if not output_md_path.exists():
        existing = list(snapshot_dir.glob("*.md"))
        raise AssertionError(f"Expected {output_md_path} but found: {existing}")

    actual_content = normalize_content(output_md_path.read_text())

    if os.environ.get("UPDATE_SNAPSHOTS") == "1":
        baseline_md_path.write_text(output_md_path.read_text())
        print(f"\\n[SNAPSHOT UPDATE] Wrote baseline to {baseline_md_path}")
    else:
        assert baseline_content is not None, f"Baseline not found at {baseline_md_path}. Run with UPDATE_SNAPSHOTS=1 first."
        assert actual_content == baseline_content, f"\\nSnapshot mismatch!\\n\\n--- EXPECTED ---\\n{baseline_content}\\n\\n--- ACTUAL ---\\n{actual_content}"
 
def test_tag_matrix_snapshots(snapshot_dir, project_root):
    """Tests Tag Matrix against baseline MD using real CLI execution."""
    args = [
        "--matrix-tag", "prod:daint:production,maint:daint:maintenance",
        "-C", str(project_root / "config" / "cscs.py"),
        "-c", str(project_root / "checks"),
        "-o", str(project_root / "reframe_reporter" / "snapshots"),
        "-f", "eligible_tests_tag-matrix_snapshot.md"
    ]
    output_md_path = snapshot_dir / "eligible_tests_tag-matrix_snapshot.md"
    baseline_md_path = snapshot_dir / "eligible_tests_tag-matrix_baseline.md"

    baseline_content = normalize_content(baseline_md_path.read_text()) if baseline_md_path.exists() else None

    run_cli(args, project_root)

    if not output_md_path.exists():
        existing = list(snapshot_dir.glob("*.md"))
        raise AssertionError(f"Expected {output_md_path} but found: {existing}")

    actual_content = normalize_content(output_md_path.read_text())

    if os.environ.get("UPDATE_SNAPSHOTS") == "1":
        baseline_md_path.write_text(output_md_path.read_text())
        print(f"\\n[SNAPSHOT UPDATE] Wrote baseline to {baseline_md_path}")
    else:
        assert baseline_content is not None, f"Baseline not found at {baseline_md_path}. Run with UPDATE_SNAPSHOTS=1 first."
        assert actual_content == baseline_content, f"\\nSnapshot mismatch!\\n\\n--- EXPECTED ---\\n{baseline_content}\\n\\n--- ACTUAL ---\\n{actual_content}"