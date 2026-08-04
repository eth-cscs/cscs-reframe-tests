import datetime
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Tuple
from collections import defaultdict
from urllib.parse import quote

from .utils import StringUtils

class ReportGenerator(ABC):
    """Base class for generating report files from test data.

    Provides common utilities for string normalization and path handling used by
    specific renderer implementations.
    """

    @abstractmethod
    def generate(self, data: List[Dict[str, Any]], path: Path, context: Dict[str, Any]) -> None:
        """Generates a report file at the specified path.

        Args:
            data (List[Dict[str, Any]]): The list of test data entries to include in the report.
            path (Path): The output destination file path.
            context (Dict[str, Any]): Metadata and configuration for the current run.
        """
        pass

    def normalize_table_string(self, text: str) -> str:
        """Normalizes a string to be safe for use in Markdown tables.

        Args:
            text (str): The raw input string.

        Returns:
            str: The normalized string with table-breaking characters removed or replaced.
        """
        return StringUtils.normalize_table_string(text)

    def split_name_and_params(self, test_name: str) -> Tuple[str, List[str]]:
        """Splits a test name from its associated parameters.

        Args:
            test_name (str): The full test name string including parameters (e.g., 'TestName %param1 %param2').

        Returns:
            Tuple[str, List[str]]: A tuple containing the base test name and a list of parameters.
        """
        return StringUtils.split_name_and_params(test_name)

    def _base_test_id(self, name: str) -> str:
        """Strip parameter part from a test name."""
        import re
        return re.sub(r'<br>.*', '', name).strip()


    def _normalize_test_name(self, name: str) -> str:
        """Normalize prefixes so names match eligible-tests style."""
        return name.replace('CPE_', '').replace('Uenv_', '')


    def _extract_variant_details(self, name: str):
        """Extract parameter lines from test name."""
        parts = name.split('<br>')
        return [p.strip('• ').strip() for p in parts[1:]]


    def _render_collapsible_variants(self, variants):
        """Render collapsible block listing parameter variants."""
        if len(variants) <= 1:
            return ""

        lines = []
        for v in variants:
            details = self._extract_variant_details(v)
            if details:
                lines.append(f"- {' '.join(details)}")
            else:
                lines.append(f"- {v}")

        inner = "\n".join(lines)

        return (
            "<details>\n"
            f"<summary>Variants ({len(variants)})</summary>\n\n"
            f"{inner}\n\n"
            "</details>"
        )
    
    def _group_tests_by_base(self, test_names):
        from collections import defaultdict
        import re

        grouped = defaultdict(list)

        for full_name in test_names:
            # remove markdown link wrapper [text](link)
            name = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", full_name)

            # remove parameter part
            name = re.split(r"<br>|•", name)[0]

            # normalize spaces
            name = name.strip()

            grouped[name].append(full_name)

        return grouped

    


class MatrixModeRenderer(ReportGenerator):
    """Renderer for creating a coverage matrix across multiple systems."""

    def generate(self, data: List[Dict[str, Any]], path: Path, context: Dict[str, Any]) -> None:
        """Generates a Markdown coverage matrix.

        Args:
            data (List[Dict[str, Any]]): The test data to render.
            path (Path): Output file path.
            context (Dict[str, Any]): Context containing 'targets'.
        """
        timestamp = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
        content = ["## Test Coverage Matrix", "", f"- Generated: `{timestamp}`", ""]

        targets = context.get("targets", [])
        if not targets:
            return
            
        labels = []
        for t in targets:
            label = t.split(':')[0] if ':' in t else t
            labels.append(label)

        target_keys = labels

        grouped_tests = defaultdict(list)

        target_counts = {target_key: 0 for target_key in target_keys}
        raw_target_counts = {target_key: 0 for target_key in target_keys}

        raw_seen = set()

        existence_lookup = {}
        unique_tests = {}

        for test in data:
            display_name = test.get("display_name", "Unknown")
            file_path = test.get("file", "")
            target = test.get("target", "")
            
            target_key = target.split(':')[0] if ':' in target else target
        
            key = (display_name, file_path, target_key)
            existence_lookup[key] = True
            
            raw_key = (display_name, file_path, target_key)
            if raw_key not in raw_seen:
                raw_seen.add(raw_key)
                if target_key in raw_target_counts:
                    raw_target_counts[target_key] += 1

            if (display_name, file_path) not in unique_tests:
                unique_tests[(display_name, file_path)] = test

        for test in unique_tests.values():
            file_path_str = test.get("file", "")
            group_key = "other"
            
            # Extract the actual system name for path logic (the part after ':')
            target_entry = test.get("target", "")
            exec_system = target_entry.split(':')[1] if ':' in target_entry else target_entry

            rel_path = None
            if "/checks/" in file_path_str:
                rel_path = "checks/" + file_path_str.split("/checks/")[-1]
            elif "checks/" in file_path_str:
                rel_path = "checks/" + file_path_str.split("checks/")[-1]

            if rel_path:
                parts = rel_path.split("/")
                if len(parts) >= 2 and parts[0] == "checks":
                    folders = parts[1:-1]
                    if folders:
                        group_key = "/".join(folders)

            grouped_tests[group_key].append(test) 

        # Build grouped structure using SAME logic as single-system
        sorted_groups = {}

        for category, tests_list in grouped_tests.items():
            groups = defaultdict(list)

            for test in tests_list:
                display_name = test.get("display_name", "")

                # SAME base extraction
                base = re.sub(r"\s*%.*?(?=\s%|$)", "", display_name).strip()
                base = base.replace("CPE_", "").replace("Uenv_", "")

                if not base:
                    base = display_name

                # category is already handled by the outer loop
                groups[base].append(test)

            sorted_groups[category] = groups

        for group in sorted(sorted_groups.keys()):
            if group == "other" and not grouped_tests[group]:
                continue

            base_groups = sorted_groups[group]

            content.append(f"### {group}")
            content.append("") 
            
            header = ["Test name"] + labels
            sep_str = "|" + ("-----------|" * len(header))
            content.append("| " + " | ".join(header) + " |")
            content.append(sep_str)

            for base_name in sorted(base_groups.keys()):
                variants = base_groups[base_name]

                # representative test
                test = variants[0]

                file_path = test.get("file", "")

                rel_link = file_path
                if "/checks/" in file_path:
                    rel_link = "../checks/" + file_path.split("/checks/")[-1]
                elif "checks/" in file_path:
                    rel_link = "../" + file_path.replace("checks/", "", 1)

                # proper markdown link again
                test_link_text = self.normalize_table_string(base_name)

                if rel_link:
                    href = quote(rel_link, safe="/._-")
                    formatted_name = f"[{test_link_text}]({href})"
                else:
                    formatted_name = test_link_text

                # cleaner collapsible block
                if len(variants) > 1:
                    all_params = []
                    for v in variants:
                        dn = v.get("display_name", "")
                        all_params.extend(re.findall(r"%.*?(?=\s%|$)", dn))

                    unique_params = sorted(set(all_params))

                    if unique_params:
                        details = "".join(
                            f"<br>- {self.normalize_table_string(p)}"
                            for p in unique_params
                        )

                        formatted_name += (
                            f"<br><details>"
                            f"<summary>🔽 {len(variants)} variants</summary>"
                            f"{details}</details>"
                        )

                row_cells = [formatted_name]

                for target_key in target_keys:
                    exists = any(
                        existence_lookup.get(
                            (v.get("display_name", ""), v.get("file", ""), target_key),
                            False
                        )
                        for v in variants
                    )

                    if exists:
                        target_counts[target_key] += 1

                    row_cells.append("✅" if exists else "❌")

                content.append("| " + " | ".join(row_cells) + " |")

            content.append("")

        if target_counts:
            content.append("### Summary")
            content.append("")

            summary_header = ["Metric"] + labels
            summary_sep = "|" + ("--------|" * len(summary_header))

            content.append("| " + " | ".join(summary_header) + " |")
            content.append(summary_sep)

            grouped_row = ["TOTAL (visible grouped rows)"] + [
                str(target_counts[target_key]) for target_key in target_keys
            ]
            content.append("| " + " | ".join(grouped_row) + " |")

            raw_row = ["TOTAL (raw ReFrame-selected tests)"] + [
                str(raw_target_counts[target_key]) for target_key in target_keys
            ]
            content.append("| " + " | ".join(raw_row) + " |")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(content))
