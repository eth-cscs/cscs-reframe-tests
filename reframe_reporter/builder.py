from typing import List, Optional
from .models import ReFrameReporterConfig

class CommandBuilder:
    """Constructs the CLI commands required by ReFrame for reporting and metadata extraction."""

    def __init__(self, config: ReFrameReporterConfig):
        """
        Initializes the CommandBuilder with a configuration object.

        Args:
            config (ReFrameReporterConfig): The reporter configuration settings.
        """
        self.config = config

    def build_reframe_cmd(self, system: str, mode: str, tag: str, extra_args: List[str]) -> List[str]:
        """
        Constructs the ReFrame command with all necessary flags and arguments.

        Args:
            system (str): The target system name.
            mode (str): The execution mode.
            tag (str): The filtering tag.
            extra_args (List[str]): Additional CLI arguments provided by the user.

        Returns:
            List[str]: The complete command as a list of strings.
        """
        # 1. Start with base command
        cmd = ["reframe"]
        
        # 2. Apply core requirements for reporting/describing
        cmd.append("--describe")

        # 3. Add recursive flag if configured in ReFrameReporterConfig
        if self.config.recursive:
            cmd.append("-R")

        # 4. Add system-specific configuration if provided
        if system:
            cmd.extend(["--system", system])

        # 4.5 Add execution mode if provided (not the internal orchestrator modes)
        if mode and mode not in ["single", "matrix", "tag"]:
            cmd.extend(["--mode", mode])

        # 5. Handle the tag specifically if it wasn't part of a pattern
        if tag and mode not in ["matrix"]:
             cmd.extend(["--tag", tag])

        # 6. Process and Clean Extra Arguments (Ported from list_tests.py)
        cleaned_extra = self._normalize_extra(extra_args)
        cmd.extend(cleaned_extra)

        return cmd

    def build_tag_reframe_cmd(self, tag: str, extra_args: List[str], target_system: str) -> List[str]:
        """
        Constructs a ReFrame command for matrix-tag mode entries.

        Unlike build_rel_reframe_cmd, this method does NOT forward --mode
        (the user opted to filter by tag directly rather than via a mode).

        Args:
            tag (str): The tag expression to filter by (e.g., 'production').
            extra_args (List[str]): Additional CLI arguments provided by the user.
            target_system (str): The specific system to target (overrides any global --system).

        Returns:
            List[str]: The complete command as a list of strings.
        """
        cmd = ["reframe", "--describe"]

        if self.config.recursive:
            cmd.append("-R")

        if target_system:
            cmd.extend(["--system", target_system])

        if tag:
            cmd.extend(["--tag", tag])

        cleaned_extra = self._normalize_extra(extra_args)
        cmd.extend(cleaned_extra)

        return cmd

    def build_output_filename(self, report_type: str, explicit_filename: bool = False) -> str:
        """
        Constructs a sanitized and truncated filename for the report.
        If the filename was explicitly provided by the user (via -f/--filename argument),
        it is used as-is without any modification.

        Args:
            report_type (str): The type of report ("matrix", "tag_matrix").
            explicit_filename (bool): If True, use config.filename as-is without modification.

        Returns:
            str: The formatted filename string.
        """
        from pathlib import Path

        if explicit_filename:
            # If -f was provided by user, use the filename EXACTLY as specified
            # without any automatic modification based on report_type
            return self.config.filename

        if report_type == "matrix":
            return f"{Path(self.config.filename).stem}_matrix.md"
        if report_type == "tag_matrix":
            return f"{Path(self.config.filename).stem}_tag-matrix.md"

        raise ValueError(f"Unknown report type: {report_type}")


    def extract_tag_from_extra(self, extra_args: List[str]) -> Optional[str]:
        """
        Extracts the value of the --tag flag from a list of arguments.

        Args:
            extra_args (List[str]): The list of command line arguments.

        Returns:
            Optional[str]: The tag value if found, otherwise None.
        """
        for i, arg in enumerate(extra_args):
            if arg.startswith("--tag="):
                return arg.split("=", 1)[1]
            elif arg in ("--tag", "--tags") and i + 1 < len(extra_args):
                return extra_args[i+1]
        return None

    def extract_param_from_extra(self, extra_args: List[str], flag: str) -> Optional[str]:
        """
        Extracts the value of a specific flag from a list of arguments.

        Args:
            extra_args (List[str]): The list of command line arguments.
            flag (str): The flag to search for (e.g., '--system').

        Returns:
            Optional[str]: The value following the flag if found, otherwise None.
        """
        for i, arg in enumerate(extra_args):
            if arg == flag and i + 1 < len(extra_args):
                return extra_args[i + 1]
            elif arg.startswith(f"{flag}="):
                return arg.split("=")[1]
        return None

    def _normalize_extra(self, extra_args: List[str]) -> List[str]:
        """
        Removes redundant tags and the '--' separator from user-provided arguments 
        to avoid conflicts with the automated builder logic.

        Args:
            extra_args (List[str]): The raw list of additional arguments.

        Returns:
            List[str]: A cleaned list of arguments.
        """
        if not extra_args:
            return []
        cleaned = list(extra_args)
        if cleaned and cleaned[0] == "--":
            cleaned = cleaned[1:]
        final_args = []
        skip_next = False
        for i, arg in enumerate(cleaned):
            if skip_next:
                skip_next = False
                continue
            if arg.startswith("--tag=") or arg in ("--tag", "--tags"):
                skip_next = True
                continue
            final_args.append(arg)
        return final_args
