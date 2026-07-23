# Proposal: Handling test changes staged on the TDS

The admins stage upcoming changes on the TDS (starlex) before a maintenance of the production systems (daint, clariden). The tests must be adapted to validate these changes on starlex, and the same adaptations must be applied to the production systems right after the maintenance.

## Option 1: feature/extras toggles in the system config

Each change staged on the TDS is expressed as a partition `features` entry (or `extras` for values) added **only to the starlex config**. Tests change their behaviour based on it, more info in [portable_tests.md](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/portable_tests.md).

How it would work:

1. **Before the maintenance** — add a feature/extra to the starlex partition config and adapt the tests to key off it:
   - when new tests are needed we can add the feature in the `valid_systems` or `valid_prog_environs`, eg: `valid_systems = ['+<new-feature>']`
   - existing tests can change their behaviour based on
     `self.current_partition.features` / `self.current_partition.extras`

   Everything is merged to `main` as usual; production systems are unaffected because they don't have the feature. Each staged feature is also recorded in a tracking file, `pending-maintenance-features.md`:

   | Feature/extra | Description | Tests affected | Apply to | Target maintenance |
   |---|---|---|---|---|
   | `cuda12.9` | New CUDA driver | `checks/...` | daint, clariden | 2026-08 |

2. **Validation** — the regular starlex pipeline picks up the new behaviour automatically, no special flags needed.

3. **After the maintenance** — add the features listed in the tracking file to the production system configs with a PR, run the production pipelines, and remove the entries from the file.

4. **Cleanup** — once a feature is present on all systems, drop the conditional logic in the tests and the feature itself, so toggles stay short-lived.

## Option 2: staging branch

Test changes are committed to a dedicated branch and the starlex pipeline runs that branch with `--system daint`.
This offers full flexibility, but the branch drifts from `main` until the maintenance, and running starlex as `daint` means perf references, partition details and paths may not match the actual system.
It can still be useful as a fallback for changes too disruptive for a toggle (e.g. a full rewrite of a test suite).
