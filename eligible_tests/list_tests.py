#!/usr/bin/env python3
"""list_tests.py

Goal
----
Generate a GitHub/GitLab-friendly Markdown report of the ReFrame checks that are
eligible for a given system (and optionally a single tag or a mode), without
parsing `reframe -L` text output.

How it works (high level)
-------------------------
1) Loads ReFrame site configuration (-C ...) and selects a system (--system).
2) Discovers tests under the provided check paths (-c ...), optionally recursive (-R).
3) Generates test cases, builds a dependency graph and keeps dependencies of selected tests.
4) Writes a Markdown file under `eligible_tests/`.

Output format
-------------
- The Markdown file is placed in `eligible_tests/` (created if missing).
- The table columns are: Test name (clickable), Description, Category (clickable).
- Links are relative to `eligible_tests/*.md`, so they use `../checks/...`.

Notes
-----
- This script targets ReFrame 4.9.1 and uses frontend internals (reframe.frontend.*).
  Those are not a formal public API, but are stable enough for this use case.
"""

import argparse
import inspect
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import reframe.core.config as rfm_config
import reframe.core.runtime as rfm_runtime

from reframe.frontend.loader import RegressionCheckLoader
from reframe.frontend.executors import generate_testcases
import reframe.frontend.dependencies as rfm_deps


# -----------------------------------------------------------------------------
# CLI / environment helpers
# -----------------------------------------------------------------------------

def run_cmd(cmd: list[str]):
    """Run a command and return (returncode, stdout, stderr)."""
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return p.returncode, p.stdout, p.stderr


def reframe_supports_mode() -> bool:
    """Detect if the installed `reframe` supports --mode."""
    rc, out, err = run_cmd(["reframe", "-h"])
    _ = rc
    return "--mode" in ((out or "") + "\n" + (err or ""))


# -----------------------------------------------------------------------------
# Output naming helpers
# -----------------------------------------------------------------------------

def sanitize_for_filename(s: str) -> str:
    """Make a string safe to embed in filenames."""
    s = (s or "").strip()
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s) or "unknown"


def truncate_filename_part(s: str, max_len: int = 60) -> str:
    """Prevent extremely long filename parts."""
    s = (s or "").strip()
    return s if len(s) <= max_len else s[:max_len].rstrip("_-.")


def make_output_filename(base_output: str, system: str, mode: str | None, tag: str | None) -> str:
    """Build output filename enriched with system/mode/tag."""
    p = Path(base_output)
    parts = [sanitize_for_filename(system)]
    if mode:
        parts.append(f"mode-{truncate_filename_part(sanitize_for_filename(mode))}")
    if tag:
        parts.append(f"tags-{truncate_filename_part(sanitize_for_filename(tag))}")

    suffix = "_".join(parts)
    if p.suffix:
        return f"{p.stem}_{suffix}{p.suffix}"
    return f"{p.name}_{suffix}"


# -----------------------------------------------------------------------------
# Markdown helpers (table-safe)
# -----------------------------------------------------------------------------

def md_escape_pipes(s: str) -> str:
    """Escape pipe characters so Markdown tables remain valid."""
    return str(s).replace("|", r"\|")


def normalize_table_cell(text: str) -> str:
    """Make a string safe inside a Markdown table cell."""
    if text is None:
        return "—"

    s = str(text).replace("\r\n", "\n").replace("\r", "\n").strip()
    if not s:
        return "—"

    # Keep the row on a single physical line
    s = s.replace("\n", "<br>")
    return md_escape_pipes(s)


def split_name_and_params(display_name: str) -> tuple[str, list[str]]:
    """Split a display name into base name + list of %param tokens."""
    s = (display_name or "").strip()
    if not s:
        return "—", []

    params = re.findall(r"%\S+", s)
    base = re.sub(r"\s*%\S+", "", s).strip()
    return base if base else s, params


def params_inline_lines(params: list[str]) -> str:
    """Render params as <br> bullet lines (works well in tables)."""
    if not params:
        return ""

    return "".join(f"<br>• {normalize_table_cell(p)}" for p in params)


# -----------------------------------------------------------------------------
# Repo-relative linking helpers
# -----------------------------------------------------------------------------

def checks_relative_path(file_path: str) -> str | None:
    """Return relative path starting at 'checks/' (included), or None if not found."""
    if not file_path:
        return None

    norm = str(file_path).replace("\\", "/")

    idx = norm.find("/checks/")
    if idx >= 0:
        return norm[idx + 1:]  # drop leading '/'

    idx = norm.find("checks/")
    if idx >= 0:
        return norm[idx:]

    return None


def category_from_checks_rel(rel: str | None) -> str:
    """Compute category as folders after checks/ up to the file name."""
    if not rel:
        return "—"

    parts = rel.split("/")
    if len(parts) < 2 or parts[0] != "checks":
        return "—"

    folders = parts[1:-1]
    return "/".join(folders) if folders else "—"


def category_link_cell(category: str) -> str:
    """Return a Markdown link for the category pointing to ../checks/<category>/"""
    if not category or category == "—":
        return "—"

    href = quote(f"../checks/{category}/", safe="/._-")
    text = normalize_table_cell(category)
    return f"[{text}]({href})"


def test_name_link_cell(test_text: str, location: str) -> str:
    """Return a Markdown link for the test name pointing to ../checks/.../file.py"""
    rel = checks_relative_path(location) if location else None
    if rel and rel.startswith("checks/"):
        href = quote(f"../{rel}", safe="/._-")
        text = normalize_table_cell(test_text)
        return f"[{text}]({href})"

    # Fallback: plain text
    return normalize_table_cell(test_text)


# -----------------------------------------------------------------------------
# Markdown preamble
# -----------------------------------------------------------------------------

def build_preamble(system: str, mode: str | None, tag: str | None, checks_count: int) -> str:
    """Build the bullet preamble shown above the table."""
    lines = ["- Filters:"]
    lines.append(f"  - system: `{system}`")
    if mode:
        lines.append(f"  - mode: `{mode}`")
    if tag:
        lines.append(f"  - tags: `{tag}`")
    lines.append(f"  - checks: `{checks_count}`")

    ts = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    lines.append(f"- Generated: `{ts}`")
    return "\n".join(lines)


# -----------------------------------------------------------------------------
# Config loading (ReFrame 4.9.1: filename/varargs)
# -----------------------------------------------------------------------------

def _flatten(obj, out: list[str]):
    """Flatten nested lists/tuples of config files into a flat list of strings."""
    if obj is None:
        return

    if isinstance(obj, (str, os.PathLike)):
        out.append(str(obj))
        return

    if isinstance(obj, (list, tuple)):
        for x in obj:
            _flatten(x, out)


def normalize_config_files(config_files) -> list[str]:
    """Normalize config files argument into a flat list of file paths."""
    flat: list[str] = []
    _flatten(config_files, flat)
    return [x for x in flat if x]


def load_site_config(config_files):
    """Load and validate the ReFrame site configuration."""
    cfgs = normalize_config_files(config_files)

    # ReFrame 4.9.1 expects filename or varargs; not a list-as-single-arg.
    if not cfgs:
        site_config = rfm_config.load_config()
    elif len(cfgs) == 1:
        site_config = rfm_config.load_config(cfgs[0])
    else:
        site_config = rfm_config.load_config(*cfgs)

    site_config.validate()
    return site_config


def apply_mode_best_effort(site_config, mode: str | None):
    """Apply an execution mode if supported by this ReFrame/site configuration."""
    if not mode:
        return

    if hasattr(site_config, "select_mode"):
        try:
            site_config.select_mode(mode)
            return
        except Exception:
            pass

    if hasattr(site_config, "add_sticky_option"):
        try:
            site_config.add_sticky_option("general/0/mode", mode)
        except Exception:
            pass


# -----------------------------------------------------------------------------
# Dependency graph normalization (ReFrame 4.9.x)
# -----------------------------------------------------------------------------

class TCNode:
    """Wrap a testcase object and attach deps/in_degree for easy traversal."""

    __slots__ = ("tc", "deps", "in_degree")

    def __init__(self, tc):
        self.tc = tc
        self.deps: list[TCNode] = []
        self.in_degree: int = 0

    def __getattr__(self, item):
        return getattr(self.tc, item)

    @property
    def check(self):
        return self.tc.check


def _extract_adjacency(res):
    """Extract adjacency mapping from dependency builder output."""
    if isinstance(res, dict):
        return res

    if isinstance(res, (list, tuple)):
        for x in res:
            if isinstance(x, dict):
                return x

    return None


def build_dependency_nodes(testcases):
    """Build TCNode objects and connect them using the ReFrame dependency graph."""
    res = None

    for fn_name in ("build_deps", "build_deps_graph", "build_graph"):
        fn = getattr(rfm_deps, fn_name, None)
        if callable(fn):
            try:
                res = fn(testcases)
                break
            except Exception:
                continue

    adj = _extract_adjacency(res)
    if adj is None:
        return [TCNode(tc) for tc in testcases]

    node_map = {}

    def get_node(tc):
        if tc not in node_map:
            node_map[tc] = TCNode(tc)
        return node_map[tc]

    for src_tc, deps in adj.items():
        src = get_node(src_tc)
        for dep_tc in deps:
            dep = get_node(dep_tc)
            src.deps.append(dep)
            dep.in_degree += 1

    return list(node_map.values())


# -----------------------------------------------------------------------------
# Filtering (single tag + dependency closure)
# -----------------------------------------------------------------------------

def filter_nodes_by_single_tag(nodes: list[TCNode], tag: str | None) -> list[TCNode]:
    """Keep nodes with `tag` in check.tags and include their dependency closure."""
    if not tag:
        return nodes

    selected = set()

    def add_closure(n: TCNode):
        if id(n) in selected:
            return
        selected.add(id(n))
        for d in n.deps:
            add_closure(d)

    for n in nodes:
        tags = getattr(n.check, "tags", set())
        if tag in tags:
            add_closure(n)

    return [n for n in nodes if id(n) in selected]


# -----------------------------------------------------------------------------
# Counting and ordering
# -----------------------------------------------------------------------------

def count_checks_reframe_like(nodes: list[TCNode]) -> int:
    """Set-based counting: leaf nodes (in_degree==0), fixture-aware, traverse deps."""
    unique_checks = set()
    leaf_nodes = [n for n in nodes if n.in_degree == 0]

    def walk_deps(node: TCNode):
        for dep in node.deps:
            unique_checks.add(dep.check.unique_name)
            walk_deps(dep)

    for n in leaf_nodes:
        if not n.check.is_fixture():
            unique_checks.add(n.check.unique_name)
        walk_deps(n)

    return len(unique_checks)


def build_rows_like_listing(nodes: list[TCNode]):
    """Produce rows: leaf nodes first, then their dependencies as related entries."""
    rows = []
    leaf_nodes = [n for n in nodes if n.in_degree == 0]

    def add_deps(node: TCNode, depth=0):
        for dep in node.deps:
            rows.append({"kind": "related", "node": dep, "depth": depth + 1})
            add_deps(dep, depth + 1)

    for n in leaf_nodes:
        rows.append({"kind": "check", "node": n, "depth": 0})
        add_deps(n, 0)

    return rows


# -----------------------------------------------------------------------------
# Markdown generation
# -----------------------------------------------------------------------------

def generate_markdown(rows,
                      checks_count: int,
                      system: str,
                      mode: str | None,
                      tag: str | None,
                      exclude_related: bool,
                      output_path: Path):
    """Write the Markdown report to disk."""
    lines = [
        f"## Eligible ReFrame Tests on {system}",
        "",
        build_preamble(system, mode, tag, checks_count),
        "",
        "| Test name | Description | Category |",
        "|----------|-------------|----------|",
    ]

    for r in rows:
        if exclude_related and r["kind"] == "related":
            continue

        node: TCNode = r["node"]
        chk = node.check

        # Locate source file path (ReFrame listing uses inspect.getfile(type(check)))
        try:
            location = inspect.getfile(type(chk))
        except Exception:
            location = ""

        rel = checks_relative_path(location) if location else None
        category = category_from_checks_rel(rel)

        descr_value = getattr(chk, "descr", None)
        descr = "—" if (descr_value is None or descr_value == "") else str(descr_value)

        display_name = getattr(chk, "display_name", getattr(chk, "name", "—"))
        base_name, params = split_name_and_params(display_name)

        prefix = "↳ " if r["kind"] == "related" else ""
        test_cell = test_name_link_cell(prefix + base_name, location) + params_inline_lines(params)

        lines.append(
            "| {name} | {desc} | {cat} |".format(
                name=test_cell,
                desc=normalize_table_cell(descr),
                cat=category_link_cell(category),
            )
        )

    output_path.write_text("\n".join(lines), encoding="utf-8")


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Generate a Markdown report of eligible ReFrame tests (ReFrame 4.9.1)."
    )

    ap.add_argument("--system", required=True, help="System name (e.g. daint)")
    ap.add_argument("--mode", help="Execution mode name")
    ap.add_argument("-t", "--tag", "--tags", dest="tag", help="Single tag to filter on")

    ap.add_argument(
        "-C", dest="config_files", action="append", default=[],
        help="ReFrame config file (repeatable: -C a.py -C b.py)"
    )
    ap.add_argument(
        "-c", dest="check_paths", action="append", required=True,
        help="Check path (file or directory). Repeatable."
    )
    ap.add_argument(
        "-R", dest="recursive", action="store_true",
        help="Search recursively inside directories passed with -c"
    )

    ap.add_argument(
        "--exclude-related", action="store_true",
        help="Do not include dependency/related entries in the table"
    )
    ap.add_argument(
        "-o", "--output", default="eligible_tests.md",
        help="Base output Markdown filename"
    )

    args = ap.parse_args()
    tag = args.tag.strip() if args.tag else None

    if args.mode and not reframe_supports_mode():
        print("WARNING: This ReFrame does not support --mode; ignoring it.")
        args.mode = None

    site_config = load_site_config(args.config_files)
    site_config.select_subconfig(args.system, ignore_resolve_errors=True)
    apply_mode_best_effort(site_config, args.mode)

    # Initialize global runtime context (required by frontend APIs)
    rfm_runtime.init_runtime(site_config)

    recursive = bool(args.recursive)

    # Discover checks
    loader = RegressionCheckLoader(args.check_paths)
    checks = []
    for p in args.check_paths:
        if os.path.isdir(p):
            try:
                checks.extend(loader.load_from_dir(p, recurse=recursive))
            except TypeError:
                # Signature compatibility fallback
                checks.extend(loader.load_from_dir(p, recursive))
        else:
            checks.extend(loader.load_from_file(p))

    # Generate testcases and dependency graph
    testcases = generate_testcases(checks)
    nodes = build_dependency_nodes(testcases)
    nodes = filter_nodes_by_single_tag(nodes, tag)

    checks_count = count_checks_reframe_like(nodes)
    rows = build_rows_like_listing(nodes)

    # Output goes to eligible_tests/ (sibling of checks/)
    out_dir = Path("eligible_tests")
    out_dir.mkdir(parents=True, exist_ok=True)

    out_name = make_output_filename(args.output, args.system, args.mode, tag)
    out_path = out_dir / out_name

    generate_markdown(
        rows,
        checks_count,
        args.system,
        args.mode,
        tag,
        exclude_related=args.exclude_related,
        output_path=out_path,
    )

    print(f"Markdown written to {out_path}")
    print(f"Checks count (ReFrame-like unique set): {checks_count}")


if __name__ == "__main__":
    main()