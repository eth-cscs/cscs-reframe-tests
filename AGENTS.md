# AGENTS.md — Working with ReFrame on Alps

This file captures the essential knowledge for an AI agent (or a new
contributor) starting from a fresh context in the `cscs-reframe-tests`
repository.  It is *not* a general ReFrame tutorial — it is a cheat-sheet
of environment setup, Alps-specific gotchas, and the conventions shared
across the GH200 vclusters (**daint**, **starlex**, **clariden**,
**santis**) and the MI300/MI200 system **beverin**.

---

## 1.  ReFrame environment

```bash
export CLUSTER_NAME=$(hostname -s | cut -d- -f1)
export RFM_STABLE=/capstor/store/cscs/cscs/public/reframe/reframe-stable/$CLUSTER_NAME
source $RFM_STABLE/rfm-env/bin/activate
```

The config file for CSCS systems is `config/cscs.py`:

```bash
reframe -C config/cscs.py -c checks/path/to/test.py -n 'TestName' -r --performance-report
```

- The rfm-env above provides reframe **4.10.3**.  If a `reframe` is
  already on `PATH` (e.g. `~/.local/bin/reframe`, 4.10.2) it may shadow
  the rfm-env binary; activate the rfm-env first so you run the
  supported version rather than a stale install.
- Two warnings appear on every run and are **harmless**:
  `redefinition of environment '*:builtin'` and
  `V-Cluster config file not found: …/checks/system/integration/…/systems_data/cluster_data.json`.

Useful flags:

| Flag | Purpose |
|------|---------|
| `-n 'PATTERN'` | Select tests by name (supports `%param` wildcards) |
| `-r` | Run selected tests |
| `--performance-report` | Print bandwidth / timing summary table |
| `-S 'key=value'` | Set a ReFrame test variable (e.g. `-S 'reservation=maint_2026_09_16'`) |
| `-t production` | Filter by tag |
| `--dry-run` | Generate sbatch scripts without submitting (useful for verification) |
| `-J OPT` | Pass a Slurm option (e.g. `-J--account=csstaff`) |
| `--system <name>:<partition>` | Target a specific system/partition (NOT `-p`, which filters programming environments) |

---

## 2.  Alps / Slurm conventions

### Use `$SCRATCH`, never `/tmp`

- `$SCRATCH` is `/capstor/scratch/<user>` — use it for all temporary files,
  container images, and ReFrame output.
- `/tmp` is local to the node and may be cleaned or too small.

### Container image cache

The Container Engine tests pull large `.sqsh` images (several GB).  They
are cached in `$SCRATCH/.edf_imagestore/`.  The first pull per account
can take 20-30 minutes; subsequent runs complete in under a minute.

### Job submission

- ReFrame submits jobs via Slurm (`sbatch`).  Jobs that cannot start
  immediately are queued — there is **no need to pre-check for idle
  nodes**.  Let Slurm schedule them.
- The default walltime for tests should be set conservatively (e.g.
  `1h00m00s`).  If a ReFrame process is killed mid-run, the queued
  Slurm job is **not** automatically cancelled and will keep running
  with the original time limit.  Use `scancel <jobid>` to clean up.
- `squeue -u <user>` to list queued/running jobs.
- `sinfo -p <partition> --state=IDLE -o "%g %D %N"` to see idle nodes
  per group (useful for ad-hoc checks, but not required for test
  submission).

### Maintenance reservations

- List: `scontrol show reservation`
- Submit a test into a reservation with `-S 'reservation=<name>'`.
- `-J` options (like `--reservation`) must go in `sched_options` or be
  set via the `-S` flag.  Adding them to `self.job.options` inside a
  `run_before('run')` hook is **too late** — the job script has already
  been generated.

---

## 3.  GH200 vclusters (daint, starlex, clariden, santis)

All four share the same shape: a `login` partition (scheduler `local`)
and a single **`normal`** GPU partition (scheduler `slurm`, launcher
`srun`) with **4 × `sm_90`** GPUs per node.  The `normal` partition
carries the `uenv` and `hugepages_slurm` features; daint additionally
carries the `cpe_ce` machinery when `CSCS_RFM_CPE_CE` is set.

### Selecting the partition

Use `--system <vcluster>:normal`.  Do **not** use `-p <partition>`: in
ReFrame `-p` filters *programming environments*, not partitions.

```bash
reframe -C config/cscs.py --system starlex:normal -n HostnameCheck --dry-run
```

### Slurm account

The default Slurm account is inferred from the user's primary group
(e.g. `csstaff`) via `osext.osgroup()` in `config/systems/<system>.py`,
so `--account` is **optional** on all four GH200 vclusters.

- **clariden** uses `--account=a-<group>` (note the `a-` prefix);
- daint, starlex and santis use `--account=<group>`.

To override the group, pass it explicitly:

```bash
reframe -C config/cscs.py --system starlex:normal -J--account=csstaff ...
```

### Uenvs — the single most important fact

By default only the `builtin` environ is available on each `normal`
partition, so only the ~59 `builtin` tests are valid.  To run any test
that requires `+openmp`, `+mpi`, `+rocm` or `+prgenv`, you **must** set
`CSCS_RFM_UENV` to a uenv label (e.g. `prgenv-gnu/<ver>:<tag>`).  Loaded
by `config/utilities/uenv.py`, the resulting environ has
`target_systems: ['*']`, so it is available on every `normal` partition
that has the `uenv` feature.

```bash
# pull once, pinning the system so the right image is fetched
uenv image pull prgenv-gnu/25.11:v1@starlex
# expose it to ReFrame WITHOUT the @<system> suffix
export CSCS_RFM_UENV=prgenv-gnu/25.11:v1
```

- The `prgenv-gnu` uenv provides the features ReFrame tests look for,
  including `rocm`, `mpi`, `openmp` and `prgenv`.
- The ReFrame environ is named `<label>_default` with `. / : @`
  replaced by `_` — e.g. `prgenv-gnu/25.11:v1` →
  `prgenv-gnu_25_11_v1_default`.
- Each vcluster has its own `prgenv-gnu` version; pull with the matching
  `@<system>` suffix and set `CSCS_RFM_UENV` to the bare label.

### Verified dry-run examples (starlex-ln001)

Without uenv (only `builtin` tests valid, ~59 checks):

```bash
$ source $RFM_STABLE/starlex/rfm-env/bin/activate
$ reframe -C config/cscs.py --system starlex:normal -n HostnameCheck --dry-run
[ DRY ] HostnameCheck /8d47d01b @starlex:normal+builtin
```

With uenv (`+openmp` tests become valid):

```bash
$ CSCS_RFM_UENV=prgenv-gnu/25.11:v1 \
    reframe -C config/cscs.py --system starlex:normal -n StreamTest --dry-run
[ DRY ] StreamTest /cdf4820d @starlex:normal+prgenv-gnu_25_11_v1_default
```

The `builtin` case was also confirmed to dry-run on `clariden:normal`,
`santis:normal` and `daint:normal`.  In both cases the generated sbatch
scripts auto-include `--account=<group>` and `--gpus-per-node=4`; the
uenv case additionally adds `--uenv=<path>/store.squashfs` and
`--view=default`.

---

## 4.  Beverin-specific notes

### Slurm account

Unlike the GH200 vclusters, `config/systems/beverin.py` does **not** set
a default Slurm account.  ReFrame also explicitly unsets `SBATCH_ACCOUNT`,
so setting that environment variable is not enough.  Pass the account
explicitly on the command line:

```bash
reframe -C config/cscs.py ... -J--account=csstaff
```

### Selecting a partition

Beverin has two GPU partitions: `mi300` and `mi200`.  Use
`--system beverin:<partition>` to target one.  Do **not** use
`-p <partition>`: in ReFrame `-p` filters *programming environments*,
not partitions.

```bash
reframe -C config/cscs.py ... --system beverin:mi300
```

### Remote topology detection

ReFrame's remote topology detection for `mi300`/`mi200` may fail because
the detection job needs internet access to install `uv` and then write
`topo.json`.  A quick workaround is to seed a local topology file so
ReFrame skips the remote detection:

```bash
mkdir -p ~/.reframe/topology/beverin-mi300 ~/.reframe/topology/beverin-mi200
cp ~/.reframe/topology/beverin-login/processor.json    ~/.reframe/topology/beverin-mi300/processor.json
cp ~/.reframe/topology/beverin-login/processor.json    ~/.reframe/topology/beverin-mi200/processor.json
```

### Uenvs

Many tests on beverin require a uenv (e.g. `prgenv-gnu`).  Pull it with
the `@beverin` suffix, but expose it to ReFrame without the system
qualifier:

```bash
uenv image pull prgenv-gnu/25.07-6.3.3:v12@beverin
export CSCS_RFM_UENV=prgenv-gnu/25.07-6.3.3:v12
```

The `prgenv-gnu` uenv provides the features ReFrame tests look for,
including `rocm`, `mpi`, and `prgenv`.

---

## 5.  Key files and mixins

| File | Purpose |
|------|---------|
| `config/cscs.py` | Main ReFrame entry point; loads all `config/systems/*.py` and the uenv loader |
| `config/common.py` | Shared environs (`builtin`, `builtin-gcc`), logging, and ReFrame *modes* (`production`, `maintenance`, `uenv_production`, …) |
| `config/utilities/uenv.py` | Loads uenv images from `CSCS_RFM_UENV` (or recipes) and exposes them as ReFrame environs |
| `config/systems/<system>.py` | Per-system config: `daint.py`, `starlex.py`, `clariden.py`, `santis.py`, `beverin.py`, … |
| `checks/mixins/container_engine.py` | `ContainerEngineMixin` / `ContainerEngineCPEMixin` — Sarus/container launch, image caching |
| `checks/mixins/slurm_mpi_pmi2.py` | `SlurmMpiPmi2Mixin` — `--mpi=pmi2` launcher |
| `uenv_checks/mixins/` | Uenv-specific mixins: `UenvSetup`, `SlurmMpiPmi2Mixin`, `SlurmMpiPmixMixin`, `ContainerEngineCPEMixin`, `UenvSlurmMpiOptionsMixin`, … |

---

## 6.  Git and GitHub workflow

- The fork remote (named **`origin`** in this checkout) →
  `git@github.com:gppezzi/cscs-reframe-tests.git`.
- The upstream remote (`upstream`) →
  `git@github.com:eth-cscs/cscs-reframe-tests.git`.
- The `gh` CLI is **not installed** on the Alps login nodes.  PR
  descriptions must be updated manually via the web UI at
  `https://github.com/eth-cscs/cscs-reframe-tests/pull/<PR_NUMBER>`.
- If a push is rejected (remote has new commits), `git pull --rebase
  origin <branch>` then push again.

---

## 7.  Common pitfalls

1. **`-J` / `self.job.options` timing**: Slurm options must be set
   before the job script is generated.  Use `sched_options` or the `-S`
   flag, not `self.job.options` in a late `run_before('run')` hook.
2. **`/tmp` vs `$SCRATCH`**: Always use `$SCRATCH` for large files and
   persistent state.  `/tmp` is per-node and unreliable.
3. **Killed ReFrame leaves orphan jobs**: If you kill the ReFrame
   process, queued Slurm jobs are not cancelled.  Run `squeue -u <user>`
   and `scancel` as needed.
4. **`-p` vs `--system`**: `-p` filters *programming environments*
   (e.g. `PrgEnv-ce`); `--system <name>:<partition>` is how you select
   a partition.  Mixing them up is a common source of "no checks
   matched".
