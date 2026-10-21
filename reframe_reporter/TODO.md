# Implementation Plan: ReFrame Test Reporter Refactoring

This document outlines the detailed implementation plan for refactoring the ReFrame Test Reporter, addressing technical debt, simplifying the CLI/API, fixing CLI bugs, and implementing an automated testing suite.

---

## Status
[x] 1. Filename Generation Logic Refactoring
[x] 2. API Simplification (Deprecate Single Runs)
[x] 3. CLI Bug Fixes & Refactoring
[x] 4. Automated Testing Suite
[x] 5. Documentation Update

---

## Completed Details

### 1. Filename Generation Logic Refactoring
* **Modified** `builder.py`: Updated `build_output_filename` to accept explicit `report_type`.
* **Modified** `orchestrator.py`: Updated calls to pass `report_type` (e.g., `"matrix"` or `"tag_matrix"`).

### 2. API Simplification (Deprecate Single Runs)
* **Modified** `cli.py`: Removed single-system flags; enforced `--matrix-mode` and `--matrix-tag` exclusivity.
* **Modified** `orchestrator.py`: Removed `run_single_mode` and unified renderer usage.
* **Modified** `renderers.py`: Deleted `SingleModeRenderer` class.

### 3. CLI Bug Fixes & Refactoring
* **Modified** `builder.py`: Removed redundant method to prevent duplicate flags.
* **Modified** `orchestrator.py`: Fixed typo in `_prepare_env` (`CSCS_RFM_UENV_TARGET_SYSTEMS`).

### 4. Automated Testing Suite
* **Created** `tests/conftest.py`, `tests/test_cli.py`, and `tests/test_snapshot.py`.
* Verified with `pytest` (Unit + Snapshot tests).

### 5. Documentation Update
* **Modified** `README.md`: Updated CLI syntax and removed single-mode references.