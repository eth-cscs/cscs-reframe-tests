from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

@dataclass
class ReFrameReporterConfig:
    """
    Configuration settings for the ReFrame Reporter.

    Attributes:
        config_files (list[Path]): List of paths to ReFrame configuration files.
        check_paths (list[Path]): Paths where checks are located.
        recursive (bool): Whether to search for checks recursively.
        uenv_recipes_dir (Optional[Path]): Directory containing uEnv recipes.
        uenv_image_inventory (Optional[Path]): Path to the uEnv image inventory file.
        uenv_env (dict[str, str]): Additional environment variables for uEnv.
        output_dir (Path): Directory where reports will be saved. Defaults to current working directory.
        filename (str): Base filename for the generated report. Defaults to "eligible_tests.md".
        system (str): Target system name.
        mode (Optional[str]): Execution mode (e.g., production, maintenance).
        tag (Optional[str]): ReFrame tag to filter checks.
    """
    config_files: list[Path] = field(default_factory=list)
    check_paths: list[Path] = field(default_factory=list)
    recursive: bool = False
    uenv_recipes_dir: Optional[Path] = None
    uenv_image_inventory: Optional[Path] = None
    uenv_env: dict[str, str] = field(default_factory=dict)
    output_dir: Path = field(default_factory=lambda: Path.cwd())
    filename: str = "eligible_tests.md"
    explicit_filename: bool = False
    system: str = ""
    mode: Optional[str] = None
    tag: Optional[str] = None

@dataclass
class CommandResult:
    """
    Captures the result of a ReFrame CLI command execution.

    Attributes:
        returncode (int): The exit status of the process.
        stdout (str): Standard output captured from the process.
        stderr (str): Standard error captured from the process.
        cmd (list[str]): The exact command list that was executed.
    """
    returncode: int
    stdout: str
    stderr: str
    cmd: list[str]
