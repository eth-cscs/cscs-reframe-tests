# `list_tests.py` — Usage Guide

This script generates a GitHub/GitLab-friendly Markdown report of **eligible ReFrame checks** for a given `--system`, using ReFrame’s **Python API** (frontend internals) rather than parsing `reframe -L` output.

The report is written under `eligible_tests/` and contains **clickable links** to the test sources under `checks/`. Since `eligible_tests/` is a sibling of `checks/`, links use `../checks/...`.

---

## What it produces

- A Markdown file in: `eligible_tests/<generated_name>.md`
- A table with columns:
  - **Test name** — clickable link to the defining `checks/.../*.py` file
  - **Description** — table-safe (multi-line descriptions are rendered with `<br>`)
  - **Category** — clickable link to the `checks/<category>/` folder

---

## Requirements

- ReFrame **4.9.1** available in your environment (e.g., `rfm-env`, module, or venv).
- Run the script from a working directory where `checks/` and `eligible_tests/` are siblings (so `../checks/...` links resolve correctly).

---

## Common usage

### 1) Filter by a single tag

Run with a single tag (example: `maintenance`):

    python utility/list_tests.py       -C /path/to/config.py       -c /path/to/checks       -R       --system daint       --tag maintenance

> **Important:** Use `-R` when `-c` points to the root `checks/` directory; most test suites store checks in nested subfolders.

---

### 2) Select an execution mode

    python utility/list_tests.py       -C /path/to/config.py       -c /path/to/checks       -R       --system daint       --mode production

If the installed ReFrame does not support `--mode`, the script will warn and continue.

---

### 3) Exclude dependency/related rows (`↳`)

By default the report includes “related/dependency” rows (shown with `↳`) because dependencies are part of the eligibility picture.

To remove them from the table:

    python utility/list_tests.py       -C /path/to/config.py       -c /path/to/checks       -R       --system daint       --tag maintenance       --exclude-related

---

### 4) Multiple configuration files (repeatable `-C`)

    python utility/list_tests.py       -C /path/to/base_config.py       -C /path/to/site_overrides.py       -c /path/to/checks       -R       --system daint

---

## Output naming

The output file name is derived from the base name (default: `eligible_tests.md`) and is automatically suffixed with:

- the system name (always)
- `mode-<mode>` if `--mode` is set
- `tags-<tag>` if `--tag/--tags/-t` is set

Example:

- `eligible_tests/eligible_tests_daint_tags-maintenance.md`

---

## Tips & troubleshooting

### “0 checks” in the report

Most common reasons:

1) You forgot `-R` while pointing `-c` at the root `checks/` folder.
2) The tag you supplied doesn’t exist on eligible checks for that `--system` selection.

### Links don’t resolve

Verify:

- The report file is under `eligible_tests/`
- `checks/` is a sibling directory of `eligible_tests/`
- You’re viewing the Markdown in the same repo (so relative links work)

---

## Help

Show script options:

    python utility/list_tests.py -h
