import json
import subprocess
import os
from typing import Optional
from .models import CommandResult

class ReFrameReporterExecutor:
    """Handles the execution of ReFrame CLI commands and parsing of their output."""

    def run(self, cmd: list[str], env: Optional[dict[str, str]] = None) -> CommandResult:
        """
        Execute the ReFrame CLI command as a subprocess.

        Args:
            cmd (list[str]): The command and arguments to execute.
            env (Optional[dict[str, str]]): Environment variables to use. 
                Defaults to current os.environ if not provided.

        Returns:
            CommandResult: An object containing the return code, stdout, stderr, and the command executed.

        Raises:
            SystemExit: If the 'reframe' binary is not found in the system PATH.
        """
        try:
            p = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env or os.environ.copy(),
            )
            return CommandResult(
                returncode=p.returncode,
                stdout=p.stdout,
                stderr=p.stderr,
                cmd=cmd
            )
        except FileNotFoundError as e:
            raise SystemExit(
                f"ERROR: Could not find 'reframe' command in PATH.\n"
                f"Error: {e}"
            )

    def parse_json(self, text: str) -> list[dict]:
        """
        Parse ReFrame --describe JSON output into a standardized list of test dictionaries.

        This method attempts to isolate the JSON array from any noise in the stdout 
        by iteratively searching for matching brackets.

        Args:
            text (str): The raw stdout string containing the JSON output.

        Returns:
            list[dict]: A list of parsed tests, each converted to a standardized internal schema.

        Raises:
            ValueError: If the output cannot be parsed as valid JSON.
        """
        if not text or not text.strip():
            return []

        try:
            # Isolate the JSON array by finding the outermost brackets to handle noise.
            # Noise may contain '[' so we iteratively try parsing to find the actual JSON.
            raw_items = None
            start_idx = text.find('[')
            end_idx = text.rfind(']') + 1
            
            while start_idx != -1 and end_idx > start_idx:
                json_str = text[start_idx:end_idx]
                try:
                    raw_items = json.loads(json_str)
                    break
                except json.JSONDecodeError:
                    start_idx = text.find('[', start_idx + 1)
            
            if raw_items is None:
                # Fallback to parsing the whole text if no bracket substring worked
                raw_items = json.loads(text)
            
            items = []
            for item in raw_items:
                # Standardize the keys to a strict, internal schema. 
                # This prevents "key leak" and ensures Renderers only rely on known fields.
                parsed_item = {
                    "kind": "check",
                    "display_name": item.get("display_name", ""),
                    "hashcode": item.get("hashcode", ""),
                    "file": item.get("@file", item.get("file", "")),
                    "description": item.get("descr", item.get("inheritDoc", item.get("description", "")))
                }
                items.append(parsed_item)
            return items
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse ReFrame JSON output: {str(e)}\nOutput was truncated: {text[:500]}...")

