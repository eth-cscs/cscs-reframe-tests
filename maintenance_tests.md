# Handling test changes staged on the TDS

The admins stage upcoming changes on the TDS (starlex) before a maintenance of the production systems (daint, clariden). The tests must be adapted to validate these changes on starlex, and the same adaptations must be applied to the production systems right after the maintenance.

## Feature/extras toggles in the system config

Each change staged on the TDS is expressed as a partition `features` entry (or `extras` for values) added **only to the starlex config**. Tests change their behaviour based on it, more info in [portable_tests.md](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/portable_tests.md).

How it works:

1. **Staging on the TDS**

   Add a feature/extra to the starlex partition config and adapt the tests to key off it:
   - when new tests are needed we can add the feature in the `valid_systems` or `valid_prog_environs`, eg: `valid_systems = ['+<new-feature>']`
   - existing tests can change their behaviour based on
     `self.current_partition.features` / `self.current_partition.extras`

   Everything is merged to `main` as usual; production systems are unaffected because they don't have the feature. Each staged feature is also recorded in a tracking file, `pending-maintenance-features.md`:

   | Feature/extra | Description | Tests affected | Apply to | Target maintenance |
   |---|---|---|---|---|
   | `cuda12.9` | New CUDA driver | `checks/...` | daint, clariden | 2026-08 |

2. **Validation on the TDS**

   The regular starlex pipeline picks up the new behaviour automatically, no special flags needed.

3. **Preparing the maintenance PR**

   Shortly before the maintenance, a branch (e.g. `maint/2026-08-daint`) is cut from the current `main`. Its only diff is adding the features listed in `pending-maintenance-features.md` to the production system's config. It is opened as a PR and reviewed in advance, so nothing needs to be written on the day itself. The branch must be pushed to the `eth-cscs/cscs-reframe-tests` repository itself, not to a fork, because the pipeline clones the branch directly from there.

4. **On the maintenance day**

   - *Before-run*: the pipeline runs on the normal daily-deployed clone of `main` which is the current production state.
   - *After-run*: the tests are redeployed for that cluster from the maintenance branch.

5. **After the maintenance**

   Once the validation passes, the PR should be merged to main.

6. **Cleanup**

   Once a feature is present on all systems, drop the conditional logic in the tests and the feature itself, so toggles stay short-lived.
