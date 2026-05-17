# list_tests.py — README

## Purpose

`list_tests.py` generates a GitHub/GitLab-friendly Markdown report of the checks **selected by ReFrame itself**, by running `reframe -L` (list-detailed) and parsing its output. 
This means you **do not re-implement** ReFrame’s selection logic in Python (modes, filtering, dependency inclusion, etc.); you simply format the already-selected tests that ReFrame prints. 

## Why this matches ReFrame

ReFrame’s frontend works in phases: it **discovers** tests, then **filters** them (by system and any other criteria), then performs an action such as listing.   
When listing, `-L/--list-detailed` prints details (including unique id and the file where each test is defined) for the **selected** tests. 
ReFrame also guarantees that if a test is selected, **its dependencies are selected too**, even if they do not match filtering criteria. 

## Output

Running the script produces **two files** under the `eligible_tests/` directory:

1. `*.md` — the human-friendly report
2. `*.reframe.out` — the raw output captured from the `reframe -L` run (stdout + stderr)

Both files share the same base filename.

### Markdown table

The report contains a table with columns:

- **Test name** — clickable link to the defining `checks/.../*.py` file
- **Description** — table-safe (wrapped output converted to `<br>`)
- **Category** — clickable link to the `checks/<category>/` folder

Because the report lives in `eligible_tests/` (a sibling of `checks/`), links are written as `../checks/...`.

## Requirements

- ReFrame installed and available as `reframe` on `PATH`
- Run the script from a working directory where `eligible_tests/` can be created and `checks/` is a sibling folder (so relative links resolve)

## Usage

### Mode-based selection (recommended)

This mirrors a typical ReFrame selection driven by an execution mode:

```bash
python utility/list_tests.py \
  -C /path/to/config.py \
  -c /path/to/checks \
  -R \
  --system daint \
  --mode maintenance \
  --list-type T
```

Notes:
- `-c/--checkpath` sets the filesystem path where ReFrame searches for tests.  
- `-R/--recursive` makes ReFrame search for test files recursively under directories in the check search path.
- `--system` selects the system configuration used for filtering.
- `--mode` activates an execution mode (which may inject additional CLI options). 
- `--list-type T|C` chooses between regular (`T`) and concretized (`C`) listing types.

### Tag-based selection

If you want to pass an explicit tag expression to ReFrame:

```bash
python utility/list_tests.py \
  -C /path/to/config.py \
  -c /path/to/checks \
  -R \
  --system daint \
  --tag 'maintenance|production'
```

> The script passes tags to ReFrame using the `--tag=<expr>` form to preserve regex-like expressions.

### Concretized listing (exact testcase DAG)

ReFrame supports two listing types for `-L`:

- `T` (default): regular test listing
- `C`: concretized test case listing (exact test cases as expanded for the selected system and environments) citeturn84view145

Example:

```bash
python utility/list_tests.py \
  -C /path/to/config.py \
  -c /path/to/checks \
  -R \
  --system daint \
  --mode maintenance \
  --list-type C
```

### Exclude dependency/related rows

By default, ReFrame lists dependencies/fixtures; the script can hide those rows in the Markdown table:

```bash
python utility/list_tests.py \
  -C /path/to/config.py \
  -c /path/to/checks \
  -R \
  --system daint \
  --mode maintenance \
  --exclude-related
```

### Pass-through extra ReFrame arguments

Anything after `--` is passed directly to ReFrame:

```bash
python utility/list_tests.py \
  -C /path/to/config.py \
  -c /path/to/checks \
  -R \
  --system daint \
  --mode maintenance \
  -- \
  -v
```

## Output filenames

You specify a base output name with `-o/--output` (default: `eligible_tests.md`).
The script automatically appends:

- the system (always)
- the mode (if used)
- the tag expression (if used)

Example:

- Markdown: `eligible_tests/eligible_tests_daint_mode-maintenance.md`
- Raw output: `eligible_tests/eligible_tests_daint_mode-maintenance.reframe.out`

## Troubleshooting

### 0 checks

- First run the same arguments directly with `reframe -L` to confirm ReFrame selects tests. citeturn84view145  
- If your checks tree is nested, ensure `-R` is passed so discovery is recursive. citeturn84view145

### Links don’t resolve

- Confirm the report lives in `eligible_tests/` and `checks/` is a sibling directory.
- Confirm your Markdown renderer resolves repository-relative links.
