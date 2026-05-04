# `list_tests.py` — Usage Guide

This script generates a GitHub/GitLab-friendly Markdown report of **eligible ReFrame checks** for a given `--system`, using ReFrame’s **Python API** (frontend internals) rather than parsing `reframe -L` output. [1](https://github.com/RichLewis007/HTML-Tags-Supported-in-GitHub-Flavored-Markdown-Documents)  
It writes the report under `eligible_tests/` and creates **clickable links** to the corresponding sources under `checks/` via `../checks/...` (because `eligible_tests/` is a sibling of `checks/`). [1](https://github.com/RichLewis007/HTML-Tags-Supported-in-GitHub-Flavored-Markdown-Documents)

---

## What it produces

- A Markdown file in: `eligible_tests/<generated_name>.md`
- A table with columns:
  - **Test name** — clickable link to the defining `checks/.../*.py`
  - **Description** — table-safe (multi-line descriptions are rendered with `<br>`)
  - **Category** — clickable link to the `checks/<category>/` directory

---

## Requirements

- ReFrame **4.9.1** available in your environment (e.g., your `rfm-env` / module / venv). [1](https://github.com/RichLewis007/HTML-Tags-Supported-in-GitHub-Flavored-Markdown-Documents)
- Run the script from a working directory where **`checks/` and `eligible_tests/` are siblings** (so `../checks/...` links resolve correctly).

---

## Common usage

### 1) Filter by a single tag

```bash
python utility/list_tests.py \
  -C /path/to/config.py \
  -c /path/to/checks \
  -R \
  --system daint \
  --tag maintenance