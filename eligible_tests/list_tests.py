#!/usr/bin/env python3
"""
Generate a Markdown report by running and parsing ReFrame `-L` (list-detailed).

Why parsing?
- `reframe -L` already applies the exact selection logic (system/mode/tags/prgenv/etc.). [1](https://reframe-hpc.readthedocs.io/en/v3.5.0/manpage.html)
- We simply format what ReFrame outputs, rather than re-implementing filtering.
"""

import argparse
import re
import shlex
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import quote


# -----------------------------------------------------------------------------
# Running ReFrame
# -----------------------------------------------------------------------------

def run_reframe(args: list[str]) -> tuple[int, str, str]:
    p = subprocess.run(
        ["reframe", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return p.returncode, p.stdout, p.stderr


# -----------------------------------------------------------------------------
# Filename helpers
# -----------------------------------------------------------------------------

def sanitize_for_filename(s: str) -> str:
    s = (s or "").strip()
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s) or "unknown"


def truncate_filename_part(s: str, max_len: int = 60) -> str:
    s = (s or "").strip()
    return s if len(s) <= max_len else s[:max_len].rstrip("_-.")


def extract_tag_from_extra(extra: list[str]) -> str | None:
    """Extract --tag from passthrough args: supports '--tag=EXPR' and '--tag EXPR'."""
    if not extra:
        return None

    for i, t in enumerate(extra):
        if t.startswith("--tag="):
            return t.split("=", 1)[1]
        if t in ("--tag", "--tags") and i + 1 < len(extra):
            return extra[i + 1]
    return None


def build_output_path(base_output: str, system: str, mode: str | None, tag: str | None) -> Path:
    """
    Create output path under eligible_tests/ with suffix:
      <stem>_<system>[_mode-<mode>][_tags-<tag>].md
    """
    out_dir = Path("eligible_tests")
    out_dir.mkdir(parents=True, exist_ok=True)

    p = Path(base_output)
    stem = p.stem if p.suffix else p.name
    ext = p.suffix if p.suffix else ".md"

    parts = [sanitize_for_filename(system)]
    if mode:
        parts.append(f"mode-{truncate_filename_part(sanitize_for_filename(mode))}")
    if tag:
        parts.append(f"tags-{truncate_filename_part(sanitize_for_filename(tag))}")

    suffix = "_".join(parts)
    filename = f"{stem}_{suffix}{ext}"
    return out_dir / filename


def build_reframe_out_path(md_path: Path) -> Path:
    """Same filename as the Markdown file, but with '.reframe.out' suffix."""
    name = md_path.name
    if name.lower().endswith(".md"):
        base = name[:-3]
    else:
        base = md_path.stem
    return md_path.with_name(f"{base}.reframe.out")


# -----------------------------------------------------------------------------
# Parsing helpers
# -----------------------------------------------------------------------------

ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
FOUND_RE = re.compile(r"(?m)^\s*Found\s+(\d+)\s+check\(s\)\.?\s*$")
HEADER_RE = re.compile(r"^\s*(?P<mark>[-^])\s+(?P<name>.+?)\s*/(?P<hash>[0-9a-fA-F]+)\s*$")
DETAIL_RE = re.compile(r"^\s+(?P<key>[A-Za-z0-9_.-]+):\s*(?P<val>.*)\s*$")


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text or "")


def parse_found_count(text: str) -> int | None:
    m = FOUND_RE.search(strip_ansi(text))
    return int(m.group(1)) if m else None


def strip_quotes(s: str) -> str:
    s = (s or "").strip()
    if len(s) >= 2 and ((s[0] == s[-1] == "'") or (s[0] == s[-1] == '"')):
        return s[1:-1]
    return s


def parse_list_detailed(text: str) -> list[dict]:
    """
    Parse ReFrame -L output into a list of items.
    Each item contains:
      kind: 'check' or 'related'
      display_name: str
      hashcode: str
      file: str|None
      description: str|None
    """
    clean = strip_ansi(text)
    lines = clean.splitlines()

    items: list[dict] = []
    current: dict | None = None
    last_key: str | None = None

    def flush():
        nonlocal current
        if current:
            items.append(current)
            current = None

    for line in lines:
        hm = HEADER_RE.match(line)
        if hm:
            flush()
            mark = hm.group("mark")
            current = {
                "kind": "check" if mark == "-" else "related",
                "display_name": hm.group("name").strip(),
                "hashcode": hm.group("hash").strip(),
                "file": None,
                "description": None,
            }
            last_key = None
            continue

        if not current:
            continue

        dm = DETAIL_RE.match(line)
        if dm:
            key = dm.group("key").strip().lower()
            val = dm.group("val").rstrip()

            if key == "file":
                current["file"] = strip_quotes(val.strip())
                last_key = "file"
            elif key in ("description", "descr"):
                current["description"] = val.strip()
                last_key = "description"
            else:
                last_key = None
            continue

        # continuation for wrapped description lines
        if last_key == "description" and line.startswith(" "):
            cont = line.strip()
            if cont:
                current["description"] = (current["description"] or "").rstrip() + " " + cont

    flush()
    return items


# -----------------------------------------------------------------------------
# Markdown output helpers
# -----------------------------------------------------------------------------

def normalize_table_cell(text: str | None) -> str:
    """Table-safe: no physical newlines; escape pipes."""
    if not text:
        return "—"
    s = str(text).replace("\r\n", "\n").replace("\r", "\n").strip()
    if not s:
        return "—"
    s = s.replace("\n", "<br>")
    return s.replace("|", r"\|")


def split_name_and_params(name: str) -> tuple[str, list[str]]:
    """Extract %param=value tokens from display_name."""
    s = (name or "").strip()
    if not s:
        return "—", []
    params = re.findall(r"%\S+", s)
    base = re.sub(r"\s*%\S+", "", s).strip()
    return base if base else s, params


def params_inline_lines(params: list[str]) -> str:
    """Render params as <br> bullet lines."""
    if not params:
        return ""
    return "".join(f"<br>• {normalize_table_cell(p)}" for p in params)


def checks_relative_path(file_path: str) -> str | None:
    """Return relative path starting at checks/"""
    if not file_path:
        return None
    norm = file_path.replace("\\", "/")
    idx = norm.find("/checks/")
    if idx >= 0:
        return norm[idx + 1:]
    idx = norm.find("checks/")
    if idx >= 0:
        return norm[idx:]
    return None


def category_from_checks_rel(rel: str | None) -> str:
    if not rel:
        return "—"
    parts = rel.split("/")
    if len(parts) < 2 or parts[0] != "checks":
        return "—"
    folders = parts[1:-1]
    return "/".join(folders) if folders else "—"


def md_link(text: str, href: str) -> str:
    """Markdown link helper."""
    return f"[{text}]({href})"


def category_cell(file_path: str | None) -> str:
    """
    Category display: subfolders after ../checks (e.g. system/gssr)
    Hyperlink target: the path currently displayed (../checks/system/gssr/)
    """
    rel = checks_relative_path(file_path) if file_path else None
    category = category_from_checks_rel(rel)
    if not category or category == "—":
        return "—"

    href = quote(f"../checks/{category}/", safe="/._-")
    return md_link(normalize_table_cell(category), href)


def test_name_cell(display_name: str, kind: str, file_path: str | None) -> str:
    """
    Show actual test name (base) + parameter bullets.
    Also add a hyperlink to the filename using the displayed relative path.
    """
    base, params = split_name_and_params(display_name)
    prefix = "↳ " if kind == "related" else ""

    # Test name should be the actual test name (not the filename)
    test_text = normalize_table_cell(prefix + base)
    cell = test_text + params_inline_lines(params)

    # Add file hyperlink using current displayed relative path
    rel = checks_relative_path(file_path) if file_path else None
    if rel and rel.startswith("checks/"):
        href = quote(f"../{rel}", safe="/._-")
        # Display text is the same relative path currently shown
        file_text = normalize_table_cell(f"../{rel}")
        cell += f"<br>file: {md_link(file_text, href)}"

    return cell


def build_preamble(system: str, mode: str | None, tag: str | None, found: int | None) -> str:
    lines = ["- Filters:"]
    lines.append(f"  - system: `{system}`")
    if mode:
        lines.append(f"  - mode: `{mode}`")
    if tag:
        lines.append(f"  - tags: `{tag}`")
    lines.append(f"  - checks: `{found if found is not None else '—'}`")
    ts = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    lines.append(f"- Generated: `{ts}`")
    return "\n".join(lines)


def write_markdown(items: list[dict],
                   output_path: Path,
                   system: str,
                   mode: str | None,
                   tag: str | None,
                   found_count: int | None,
                   exclude_related: bool):
    lines = [
        f"## Eligible ReFrame Tests on {system}",
        "",
        build_preamble(system, mode, tag, found_count),
        "",
        "| Test name | Description | Category |",
        "|----------|-------------|----------|",
    ]

    for it in items:
        if exclude_related and it["kind"] == "related":
            continue

        file_path = it.get("file")
        name_cell = test_name_cell(it.get("display_name") or "—", it["kind"], file_path)
        desc_cell = normalize_table_cell(it.get("description") or "—")
        cat_cell = category_cell(file_path)

        lines.append(f"| {name_cell} | {desc_cell} | {cat_cell} |")

    output_path.write_text("\n".join(lines), encoding="utf-8")


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Generate Markdown report by parsing `reframe -L` output.")
    ap.add_argument("--system", required=True, help="ReFrame system name (e.g. daint)")
    ap.add_argument("--mode", help="ReFrame execution mode (passed through)")
    ap.add_argument("--tag", "--tags", dest="tag", help="Tag expression passed to ReFrame (optional)")
    ap.add_argument("-C", dest="config_files", action="append", default=[],
                    help="ReFrame config file (repeatable: -C a.py -C b.py)")
    ap.add_argument("-c", dest="check_paths", action="append", default=[],
                    help="Check path(s) (repeatable, passed through)")
    ap.add_argument("-R", dest="recursive", action="store_true",
                    help="Pass -R to ReFrame")
    ap.add_argument("--list-type", choices=["T", "C"], default="T",
                    help="ReFrame -L listing type: T (regular) or C (concretized).")
    ap.add_argument("--exclude-related", action="store_true",
                    help="Exclude dependency/related rows (^ in ReFrame output).")
    ap.add_argument("-o", "--output", default="eligible_tests.md",
                    help="Base output filename (suffixes added automatically).")
    ap.add_argument("extra", nargs=argparse.REMAINDER,
                    help="Extra args passed to ReFrame after '--'")

    args = ap.parse_args()

    extra = list(args.extra)
    if extra and extra[0] == "--":
        extra = extra[1:]

    tag_used = args.tag if args.tag else extract_tag_from_extra(extra)

    # Build ReFrame args
    reframe_args: list[str] = ["-L", args.list_type]
    for cf in args.config_files:
        reframe_args.extend(["-C", cf])
    for cp in args.check_paths:
        reframe_args.extend(["-c", cp])
    if args.recursive:
        reframe_args.append("-R")
    reframe_args.extend(["--system", args.system])
    if args.mode:
        reframe_args.extend(["--mode", args.mode])
    if tag_used:
        reframe_args.append(f"--tag={tag_used}")  # preserve regex-like expressions
    reframe_args.extend(extra)

    rc, out, err = run_reframe(reframe_args)
    combined = (out or "") + "\n" + (err or "")

    if rc != 0:
        raise SystemExit(
            "ReFrame failed.\n\n"
            f"Command: reframe {' '.join(shlex.quote(x) for x in reframe_args)}\n\n"
            f"STDERR:\n{err}"
        )

    # Output paths
    md_path = build_output_path(args.output, args.system, args.mode, tag_used)
    out_path = build_reframe_out_path(md_path)

    # Save raw ReFrame output alongside the Markdown report
    out_path.write_text(combined, encoding="utf-8")

    found = parse_found_count(combined)
    items = parse_list_detailed(combined)

    write_markdown(
        items=items,
        output_path=md_path,
        system=args.system,
        mode=args.mode,
        tag=tag_used,
        found_count=found,
        exclude_related=args.exclude_related
    )

    print(f"Markdown written to {md_path}")
    print(f"ReFrame output saved to {out_path}")
    if found is not None:
        print(f"Checks (ReFrame footer): {found}")


if __name__ == "__main__":
    main()