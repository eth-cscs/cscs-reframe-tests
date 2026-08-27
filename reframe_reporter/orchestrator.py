import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from .models import ReFrameReporterConfig
from .builder import CommandBuilder
from .executor import ReFrameReporterExecutor
from .renderers import MatrixModeRenderer

class ReportOrchestrator:
    def __init__(self, config: ReFrameReporterConfig, explicit_filename: bool = False):
        """
        Initializes the ReportOrchestrator with the provided configuration.

        Args:
            config (ReFrameReporterConfig): The configuration object containing settings for 
                output directories, check paths, environment variables, and other parameters.
            explicit_filename (bool): If True, the filename from config is used as-is without 
                modification (for '-f' flag). If False, the filename is modified based on 
                report type (matrix mode appends suffix).
        """
        self.config = config
        self.builder = CommandBuilder(config)
        self.executor = ReFrameReporterExecutor()
        self.matrix_renderer = MatrixModeRenderer()
        self.explicit_filename = explicit_filename

    def _get_target_dir(self) -> Path:
        """
        Determines the target directory for output based on the configuration.

        Returns:
            Path: The resolved path to use as the output directory. Defaults to the current 
                directory if no specific paths are provided in the config.
        
        Determines the target directory for output based on the configuration.

        Returns:
            Path: The resolved path to use as the output directory. Defaults to the current 
                directory if no specific paths are provided in the config.
        """
        if self.config.output_dir:
            return self.post_process_path(self.config.output_dir)
        elif self.config.check_paths:
            return self.config.check_paths[0].parent
        else:
            return Path(".")

    def post_process_path(self, path: Path) -> Path:
        """
        Ensures the output directory exists by creating it if necessary.

        Args:
            path (Path): The path to the directory that should be ensured to exist.

        Returns:
            Path: The validated and created directory path.
        """
        os.makedirs(path, exist_ok=True)
        return path



    def run_matrix_mode(self, targets: List[str], extra_args: List[str]) -> Path:
        """
        Executes ReFrame for multiple targets and aggregates the results into a matrix report.

        Args:
            targets (List[str]): A list of targets in 'label:system:mode' format.
            extra_args (List[str]): Additional arguments to pass to ReFrame.

        Returns:
            Path: The path to the generated matrix report file.
        """
        all_results = []
        processed_targets_ordered = []
        any_failures = False

        for target in targets:
            clean_target = target.strip()
            parts = clean_target.split(':')
            label = parts[0] if len(parts) > 0 and parts[0] else clean_target
            exec_system = parts[1] if len(parts) > 1 and parts[1] else ""
            exec_mode = parts[2] if len(parts) > 2 and parts[2] else ""

            cmd = self.builder.build_reframe_cmd(exec_system, exec_mode, "", extra_args)
            env = self._prepare_env(exec_system)

            print(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] "
                f"Executing Matrix Target: {exec_system} (Label entry: {label}, Mode: {exec_mode})"
            )
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Executing Matrix Mode Command: {' '.join(cmd)}")

            result = self._run_and_save_raw(cmd, env)

            if result.returncode == 0:
                try:
                    data = self.executor.parse_json(result.stdout)
                    for item in data:
                        item["target"] = clean_target 
                        all_results.append(item)
                    if clean_target not in processed_targets_ordered:
                        processed_targets_ordered.append(clean_target)
                except ValueError as e:
                    print(f"ERROR: {e}")
                    any_failures = True
            else:
                self._report_failure(f"Matrix Target ({clean_target})", cmd, result)
                any_failures = True

        filename = self.builder.build_output_filename("matrix", explicit_filename=self.explicit_filename)
        target_dir = self._get_target_dir()
        output_path = target_dir / filename
        context = {
            "system": "",
            "mode": "",
            "tag": "",
            "targets": processed_targets_ordered if processed_targets_ordered else targets,
            "any_failures": any_failures
        }
        self.matrix_renderer.generate(all_results, output_path, context)
        return output_path

    def run_matrix_tag_mode(self, targets: List[str], extra_args: List[str]) -> Path:
        """
        Executes ReFrame for multiple tag targets and aggregates the results into a matrix report.

        Args:
            targets (List[str]): A list of targets in 'label:system:tag' format.
            extra_args (List[str]): Additional arguments to pass to ReFrame.

        Returns:
            Path: The path to the generated matrix report file.
        """
        all_results = []
        processed_targets_ordered = []
        any_failures = False

        for target in targets:
            clean_target = target.strip()
            parts = clean_target.split(':')
            label = parts[0] if len(parts) > 0 and parts[0] else clean_target
            exec_system = parts[1] if len(parts) > 1 and parts[1] else ""
            exec_tag = parts[2] if len(parts) > 2 and parts[2] else ""

            cmd = self.builder.build_tag_reframe_cmd(exec_tag, extra_args, exec_system)
            env = self._prepare_env(exec_system)

            print(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] "
                f"Executing Matrix Tag Target: {exec_system} (Label: {label}, Tag: {exec_tag})"
            )
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Command: {' '.join(cmd)}")

            result = self._run_and_save_raw(cmd, env)

            if result.returncode == 0:
                try:
                    data = self.executor.parse_json(result.stdout)
                    for item in data:
                        item["target"] = clean_target
                        all_results.append(item)
                    if clean_target not in processed_targets_ordered:
                        processed_targets_ordered.append(clean_target)
                except ValueError as e:
                    print(f"ERROR: {e}")
                    any_failures = True
            else:
                self._report_failure(f"Matrix Tag Target ({clean_target})", cmd, result)
                any_failures = True

        filename = self.builder.build_output_filename("tag_matrix", explicit_filename=self.explicit_filename)
        target_dir = self._get_target_dir()
        output_path = target_dir / filename
        context = {
            "system": "",
            "mode": "",
            "tag": "",
            "targets": processed_targets_ordered if processed_targets_ordered else targets,
            "any_failures": any_failures
        }
        self.matrix_renderer.generate(all_results, output_path, context)
        return output_path

    def _report_failure(self, context_label: str, cmd: List[str], result: Any) -> None:
        """Detailed error reporting for failed ReFrame executions."""
        print(f"\n{'!'*20} ERROR {'!'*20}")
        print(f"Context: {context_label}")
        print(f"Command: {' '.join(cmd)}")
        print(f"Return Code: {result.returncode}")
        if result.stdout:
            print(f"\n--- STDOUT --- \n{result.stdout}")
        if result.stderr:
            print(f"\n--- STDERR --- \n{result.stderr}")
        print(f"{'!'*49}\n")

    def _run_and_save_raw(self, cmd: List[str], env: Dict[str, str]) -> Any:
        """Executes the command and preserves raw stdout/stderr to a file."""
        result = self.executor.run(cmd, env=env)
        try:
            directory = self._get_target_dir()
            from .utils import StringUtils
            raw_name = "reframe_raw"
            raw_filename = StringUtils.sanitize_for_filename(raw_name) + ".reframe.out"
            raw_path = directory / raw_filename
            os.makedirs(directory, exist_ok=True)
            with open(raw_path, "w") as f:
                f.write("=== COMMAND ===\n")
                f.write(" ".join(cmd) + "\n")
        except (OSError, IOError) as e:
            print(f"WARNING: Failed to save raw output file due to I/O error: {e}")
        except Exception as e:
            print(f"WARNING: An unexpected error occurred while saving raw output: {e}")
        return result

    def _prepare_env(self, system: str) -> Dict[str, str]:
        """Prepares the environment variables."""
        env = os.environ.copy()
        if self.config.uenv_recipes_dir:
            env["CSCS_RFM_UENV_RECIPES_DIR"] = str(self.config.uenv_recipes_dir.resolve())
        if self.config.uenv_image_inventory:
            env["CSCS_RFM_UENV_IMAGE_INVENTORY"] = str(self.config.uenv_image_inventory.resolve())
        if self.config.uenv_recipes_dir or self.config.uenv_image_inventory:
            env["CSCS_RFM_UENV_TARGET_SYSTEMS"] = system 
        env.update(self.config.uenv_env)
        return env
