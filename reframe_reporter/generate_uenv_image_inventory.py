#!/usr/bin/env python3
"""Generate per-system and merged UENV image inventory JSON files.

Need to be run on a system with access to the `uenv` CLI tool.
Will generate one JSON file per system, as well as a merged file containing all records from the specified systems.

reframe_reporter can then use these inventory files to determine which UENV images are available for each system when generating test eligibility reports.

Usage:
  python3 generate_uenv_image_inventory.py --output-dir ./inventories --system daint,eiger,santis,clariden,starlex
  python3 generate_uenv_image_inventory.py -o ./inventories -s daint
"""

from __future__ import annotations

import json
import subprocess
from argparse import ArgumentParser
from pathlib import Path
from typing import Any


def run_uenv_find(system: str) -> dict[str, Any]:
    cmd = ["uenv", "image", "find", "--json", f"@{system}"]
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise SystemExit(
            f"`{' '.join(cmd)}` failed with exit code {result.returncode}\n"
            f"STDERR:\n{result.stderr.strip()}"
        )

    try:
        inventory = json.loads(result.stdout)
    except json.JSONDecodeError as err:
        raise SystemExit(
            f"Failed to parse JSON output from {' '.join(cmd)}: {err}\n"
            f"Output:\n{result.stdout[:1024]}"
        )

    if not isinstance(inventory, dict):
        raise SystemExit("Invalid UENV image inventory: expected JSON object at top level")

    return inventory


def write_inventory_file(path: Path, inventory: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    print(f"Wrote {path}")


def main() -> None:
    parser = ArgumentParser(
        description="Generate per-system and merged UENV image inventory JSON files for matrix runs."
    )
    parser.add_argument(
        "-o", "--output-dir",
        required=True,
        help="Directory where the inventory JSON files will be written.",
    )
    parser.add_argument(
        "-s", "--system",
        required=True,
        help="System or comma-separated list of systems to query, e.g. daint or daint,eiger,santis",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir).expanduser().resolve()
    
    # Parse comma-separated system string into a clean list
    systems = [part.strip() for part in args.system.split(",") if part.strip()]
    if not systems:
        raise SystemExit("No valid systems provided. Use a format like --system daint,eiger")

    merged_records: list[dict[str, Any]] = []

    for system in systems:
        # 1. Fetch individual system inventory
        inventory = run_uenv_find(system)
        
        # 2. Save individual per-system inventory file (ideal for matrix downstream steps)
        system_file = output_dir / f"uenv_image_inventory_{system}.json"
        write_inventory_file(system_file, inventory)
        
        # 3. Harvest records for the merged aggregate file
        records = inventory.get("records")
        if not isinstance(records, list):
            raise SystemExit(
                f"Inventory returned by system {system} does not contain a 'records' list"
            )
        merged_records.extend(record for record in records if isinstance(record, dict))

    # 4. Save the combined merged inventory file
    merged_inventory = {"records": merged_records}
    # Append the system names (joined by '_') to the merged filename
    systems_suffix = "_".join(systems)
    merged_file = output_dir / f"uenv_image_inventory_{systems_suffix}.json"
    write_inventory_file(merged_file, merged_inventory)


if __name__ == "__main__":
    main()