# AGENTS.md — OSU mbw_mr switch-topology tests

Two ReFrame checks measure `osu_mbw_mr` aggregate point-to-point bandwidth across Slurm Level-0 switch groups on the GH200 vclusters (daint, starlex, clariden, santis). They use a Container Engine MPICH image (with the CXI hook for native Slingshot) as the *vehicle*, but the test purpose is **fabric health and topology validation**, not container engine testing.

See the file header in `omb_mbw_mr.py` for benchmark theory, expected results, and the SC23 paper reference.

## Checks

| Check | Tag | valid_systems | References |
|-------|-----|---------------|------------|
| `OMB_MBW_MR_PerSwitch` | `maintenance` | daint, starlex, clariden, santis | daint + starlex only; clariden and santis run **record-only** until baselines are collected |
| `OMB_MBW_MR_FullTopology` | `maintenance` | daint, starlex, clariden, santis | Shared per-switch-count baselines (N=2–8) across all four vclusters |

Both are tagged `maintenance` because `normal`-partition jobs can wait indefinitely for nodes and eventually time out, producing daily false positives. Use a reservation.

## How to run

```bash
# Activate ReFrame (see top-level AGENTS.md §1)
source $RFM_STABLE/$CLUSTER_NAME/rfm-env/bin/activate

# Dry-run (generates sbatch scripts, no submission)
reframe -C config/cscs.py --system starlex:normal -n OMB_MBW_MR --dry-run

# Dry-run a single PerSwitch variant
reframe -C config/cscs.py --system starlex:normal \
    -n 'OMB_MBW_MR_PerSwitch %switch_group=group37' --dry-run

# Real run inside a maintenance reservation
reframe -C config/cscs.py --system starlex:normal \
    -n OMB_MBW_MR_PerSwitch -S 'reservation=maint_2026_09_30' -r

# FullTopology with a cap on groups (scaling study)
reframe -C config/cscs.py --system daint:normal \
    -n OMB_MBW_MR_FullTopology -S 'max_switch_groups=4' -r --performance-report
```

## What to expect

- **PerSwitch skips are normal on a busy system.** Each variant requires 4 idle nodes in its switch group; today on starlex, 2 of 3 variants skipped because groups had only 1–2 idle nodes. Use a reservation for reliable coverage.
- **FullTopology skips when fewer than `min_switch_groups` (default 2) groups have usable nodes.**
- **osu_mbw_mr is O(n²) in rank pairs.** At 16 ranks (4 nodes × 4 ranks/node) there are 120 pairs (~30 s). Keep `num_tasks_per_node` and `num_nodes` small.
- **First run pulls a ~9.6 GB container image** (20–30 min), cached in `$SCRATCH/.edf_imagestore`. Subsequent runs complete in < 1 minute. `time_limit = '1h'` is set in the base class to allow for this.

## Key files

| File | Purpose |
|------|---------|
| `omb_mbw_mr.py` (this directory) | `OMB_MBW_MR_Base`, `OMB_MBW_MR_PerSwitch`, `OMB_MBW_MR_FullTopology` |
| `switch_topology.py` (this directory) | Slurm topology helpers: `get_l0_switches()`, `get_switch_groups()`, `get_partition_nodes()`, `all_partition_nodes()`, `select_nodes_across_groups()`, `expand_reservation()` |
| `checks/mixins/container_engine.py` | `ContainerEngineMixin` — Sarus container launch, image caching |
| `checks/mixins/slurm_mpi_pmi2.py` | `SlurmMpiPmi2Mixin` — `--mpi=pmi2` launcher |

## Operational notes

- Switch groups are discovered via `scontrol show topology` at ReFrame import time. Check the live topology with:
  ```bash
  scontrol show topology | grep 'Level=0'
  ```
- The number and names of switch groups are **volatile** — they change as nodes are added, removed, or reassigned. Do not hard-code group names outside the test's `parameter()` call.
- Some groups may be in `xfer`-only partitions (not `normal`); the test automatically excludes them via `all_partition_nodes()`.
- Each rank is bound to one CPU LDOM (`--cpu-bind=ldoms`) so that Cray MPICH selects the nearest Slingshot NIC. With 4 ranks per node on GH200 (4 NICs per node), all NICs are exercised. See the file header in `omb_mbw_mr.py` for why multi-NIC per process is not possible (`MPIDI_OFI_ENABLE_SCALABLE_ENDPOINTS=0`).

## TODO

- [ ] Collect PerSwitch baselines on clariden and santis during the next maintenance window, then add `reference` entries (currently record-only).
- [ ] Replace hardcoded partition names with a feature (e.g. `slingshot11` or `gh200`) once a suitable feature is added to the system configs. `+ce +nvgpu` is too broad (includes bristen A100).
