# Changelog

All notable changes to `reframe_reporter` are documented here.

---

## [1.5.1] - 2026-07-07

### Fixed
- Aligned reporter-injected uenv environment variables with `config/utilities/uenv.py`:
  - `RFM_UENV_RECIPES_DIR` → `CSCS_RFM_UENV_RECIPES_DIR`
  - `RFM_UENV_IMAGE_INVENTORY` → `CSCS_RFM_UENV_IMAGE_INVENTORY`
  - `RFM_UENV_TARGET_SYSTEMS` → `CSCS_RFM_UENV_TARGET_SYSTEMS`
- Clarified README description of when the `CSCS_RFM_UENV` runtime path is bypassed.

---

## [1.5.0] - 2026-06-22

### Added
- Matrix mode support for tag-based coverage.
- `uenv.py` implementation for fetching UEnv tests within the reporter.
- Utilities and snapshots for generating/managing JSON UEnv inventories.
- Initial tests with pytest

### Changed
- Removed single system run option (to simplify the code)
  - Should use matrix mode with single item instead
- Refactored command building and filename logic for improved reliability.
- Renamed UEnv environment variable to `CSCS_RFM_UENV`.
- Improved Markdown report formatting, including timestamps and alphabetical grouping for matrix runs.

### Fixed
- Fixed missing CLI arguments during matrix execution.
- Corrected documentation gaps and repository links.

---

## [1.4.0] - 2026-06-10

### Changed
- Refactored `list_tests.py` into an object-oriented architecture.
- Introduced a cleaner, more intuitive API.
- Simplified the interface specifically for matrix mode operations.

### Added
- `run_report.py`: The new primary entry point for running the reporter.
- `orchestrator.py`: Manages execution flow, command construction, and result processing.
- `renderers.py`: Handles Markdown report generation for both single and matrix modes.
- `cli.py`: Provides a structured CLI interface for interacting with the reporter.
- `executor.py`: Manages ReFrame CLI command execution and output parsing.
- `models.py` and `utils.py`: Core data models and shared utility functions.

For more details, see [README.md](README.md).

---

## [1.3.0] - 2026-06-03

### Added
- Added support for explicit per-system UENV inventory queries via `CSCS_RFM_UENV_TARGET_SYSTEMS`.
- Added merging of multiple `uenv image find --json @<system>` lookups so multi-system availability can be checked from a single run.
- Added support for two data retrieval paths: direct UENV output on a target system, or pre-generated inventory JSON from `generate_uenv_image_inventory.py`.

### Changed
- Stopped relying on `config.yaml` for UENV recipe system mapping because it is not reliable.
- Documented direct UENV output and inventory generator usage as the preferred retrieval options.

## [1.2.0] - 2026-06-02

### Added
- Added exact deployment mapping for local UENV recipes using `alps-uenv/config.yaml`.
- Local UENV recipe mode now assigns `target_systems` only for systems explicitly declared in `config.yaml`.

### Changed
- Switched local UENV recipe discovery from generic global availability to explicit system mapping.

---

## [1.1.1] - 2026-06-02

### Added
- Added `--uenv-recipes-dir` option to list UENV-enabled tests from local recipe metadata without installed uenv images.
- Local recipe mode is enabled by setting `CSCS_RFM_UENV_RECIPES_DIR` for ReFrame subprocesses.

---

## [1.1.0] - 2026-05-30

### Changed
- Swapped fragile `reframe -L` textual/regex stdout parsing for native `reframe --describe` JSON serialization.
- Replaced custom stateful line matching with robust `json.loads()` processing, successfully addressing edge cases involving cropped or multi-line wrapped descriptions.
- Removed obsolete `--list-type` and `--exclude-related` CLI options since `--describe` strictly lists selected checks natively without tree entities.

---

## [1.0.0] - 2026-05-28

### Added
- Matrix mode for cross-system coverage visualization:
  - `--matrix-mode label:system:mode`
  - `--matrix-tag label:system:tag`
- Matrix tables grouped by category
- Eligibility matrix with ✅ / ❌ indicators
- Summary table with totals per column
- Timestamp in matrix report
- Explicit debug output showing full ReFrame commands

### Improved
- Clear separation of mode and tag selection in matrix CLI
- Markdown formatting for summary tables
- Output files generated relative to script location
- Reuse of helper utilities (links, categories, filenames)

### Fixed
- Ensured `-R` is correctly propagated for recursive discovery
- Fixed `-L` / `--list` CLI conflict
- Fixed malformed TOTAL row in Markdown output
- Resolved inconsistencies between matrix and single-system results

### Behavior
- Single-system mode remains fully backward compatible
- Matrix mode is opt-in via `--matrix-*`

---

## [0.9.0] - 2026-05-27

### Added
- Initial matrix prototype combining multiple system runs
- Basic ✅ / ❌ matrix output
- First implementation of category grouping

### Notes
- Used generic `--target` CLI (later replaced)
- Partial formatting differences with original script


---

## [< 0.9.0] - Initial versions

### Features
- Single-system Markdown report generation
- Parsing of `reframe -L` output
- Category-based grouping
- Clickable links to test files
- Support for `--system`, `--mode`, `--tag`
- Support for `-C`, `-c`, `-R`
- Raw `.reframe.out` output capture

### Design principle
- Reuse ReFrame’s selection logic instead of reimplementing filtering
- Retrieve test data using ReFrame's JSON output from --describe
