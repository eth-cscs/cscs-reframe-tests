# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Helpers for selecting Slurm nodes based on the tree topology.

The functions parse `scontrol show topology` and optionally intersect the
reported switch groups with the currently available nodes of a target
partition.  This lets ReFrame checks place jobs on nodes that span distinct
Level-0 switch groups.
"""

import functools
import json
import re
import subprocess

# Default timeout (seconds) for scontrol invocations.  A hung scontrol
# during setup on a live cluster is a real failure, not a silent skip;
# only get_l0_switches() catches TimeoutExpired (returning [] so that
# parameterized tests have no variants on non-Slurm systems).
_SCONTROL_TIMEOUT = 30

# Pre-compiled regexes for parsing ``scontrol show topology`` output.
# Fields are searched independently so that reordering, extra whitespace,
# or omitted fields (e.g. LinkSpeed) do not silently drop switches.
_SWITCH_NAME_RE = re.compile(r'SwitchName=(\S+)')
_SWITCH_LEVEL_RE = re.compile(r'Level=(\d+)')
_SWITCH_NODES_RE = re.compile(r'Nodes=(\S+)')


def get_l0_switches() -> list[str]:
    """Return the list of live Level-0 switch names.

    Called at module import time (on a login node) to populate ReFrame
    test parameters. Returns an empty list if `scontrol` is not
    available (e.g. CI runners, non-Slurm systems), in which case
    parameterized tests will have no variants and effectively skip.
    """
    try:
        output = subprocess.check_output(
            ['scontrol', 'show', 'topology'], text=True,
            stderr=subprocess.STDOUT, timeout=_SCONTROL_TIMEOUT,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return []

    switches = []
    for line in output.splitlines():
        name_match = _SWITCH_NAME_RE.search(line)
        level_match = _SWITCH_LEVEL_RE.search(line)
        if name_match and level_match and int(level_match.group(1)) == 0:
            switches.append(name_match.group(1))

    return switches


def _run(cmd: list[str], timeout: int = _SCONTROL_TIMEOUT) -> str:
    """Run *cmd* and return its stdout as text.

    Wraps :func:`subprocess.check_output` with a default timeout and
    ``text=True``.  Raises :class:`subprocess.CalledProcessError`,
    :class:`subprocess.TimeoutExpired`, or :class:`OSError` to the
    caller — a failing or hung ``scontrol`` during setup on a live
    cluster is a real problem, not a silent skip.
    """
    return subprocess.check_output(
        cmd, text=True, stderr=subprocess.STDOUT, timeout=timeout,
    )


def expand_hostlist(nodelist: str) -> list[str]:
    """Expand a Slurm compressed hostlist into a list of node names."""
    if not nodelist:
        return []

    try:
        out = _run(['scontrol', 'show', 'hostnames', nodelist])
    except subprocess.CalledProcessError:
        return []

    return [n.strip() for n in out.strip().splitlines() if n.strip()]


def expand_reservation(name: str) -> list[str]:
    """Return the list of nodes in the given Slurm reservation."""
    try:
        out = _run(['scontrol', 'show', 'reservation', name])
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return []

    match = re.search(r'Nodes=(\S+)', out)
    if not match:
        return []

    return expand_hostlist(match.group(1))


@functools.lru_cache(maxsize=None)
def get_switch_groups(level: int = 0) -> dict[str, list[str]]:
    """Return a dict mapping switch name to node list for the given level.

    Invokes `scontrol show topology` on the host.  The output cannot be
    supplied from a ReFrame test's `self.stdout` because that is a
    deferred expression, not a plain string, at the point helpers run
    (during `setup`/`run` hooks).  See `SwitchTopologyCheck` for the
    known trade-off: it runs `scontrol` as its own executable *and*
    this helper spawns a second, redundant call.

    The result is cached with :func:`functools.lru_cache` because the
    topology is static for the duration of a ReFrame session.
    """
    output = _run(['scontrol', 'show', 'topology'])

    groups = {}
    for line in output.splitlines():
        name_match = _SWITCH_NAME_RE.search(line)
        level_match = _SWITCH_LEVEL_RE.search(line)
        nodes_match = _SWITCH_NODES_RE.search(line)
        if not (name_match and level_match and nodes_match):
            continue

        if int(level_match.group(1)) != level:
            continue

        groups[name_match.group(1)] = expand_hostlist(nodes_match.group(1))

    return groups


def get_switch_group_names(level: int = 0) -> list[str]:
    """Return a sorted list of switch names at the given level.

    Wraps :func:`get_switch_groups` and returns only the keys.
    """
    return sorted(get_switch_groups(level).keys())


def _partition_nodes_json(partition: str) -> list[tuple[str, set[str]]]:
    """Fetch node names and state sets for *partition* from ``scontrol``.

    Runs ``scontrol show nodes --json``, parses the output, and returns a
    list of ``(name, states)`` tuples for every node that belongs to
    *partition*.  A ``scontrol`` timeout or corrupt JSON is a real
    failure on a live cluster — this function does not catch
    :class:`subprocess.TimeoutExpired` or :class:`json.JSONDecodeError`.
    """
    out = _run(['scontrol', 'show', 'nodes', '--json'])
    data = json.loads(out)
    result = []
    for node in data.get('nodes', []):
        name = node.get('name')
        if name is None:
            continue

        if partition not in node.get('partitions', []):
            continue

        result.append((name, set(node.get('state', []))))

    return result


def get_partition_nodes(
    partition: str, reservation: str | None = None
) -> set[str]:
    """Return the set of usable nodes in *partition*.

    When *reservation* is given, only nodes belonging to that Slurm
    reservation are returned (no state filtering — the reservation
    guarantees access).  This is the path used during maintenance, where
    nodes carry the `RESERVED` flag and would otherwise be excluded.

    Without a reservation, only `IDLE` nodes are returned, with `DRAIN`
    and `MAINTENANCE` nodes excluded.
    """
    if reservation:
        reserved = set(expand_reservation(reservation))
        all_nodes = all_partition_nodes(partition)
        return reserved & all_nodes

    # Exclude COMPLETING: a node in IDLE+COMPLETING matches as IDLE but
    # Slurm won't allocate it, causing indefinite hangs.
    exclude = ('DRAIN', 'MAINTENANCE', 'COMPLETING')
    nodes = set()
    for name, state in _partition_nodes_json(partition):
        if 'IDLE' not in state:
            continue

        if any(flag in state for flag in exclude):
            continue

        nodes.add(name)

    return nodes


def all_partition_nodes(partition: str) -> set[str]:
    """Return all node names in *partition* regardless of state."""
    return {name for name, _ in _partition_nodes_json(partition)}


def select_nodes_across_groups(
    num_nodes: int, partition: str, reservation: str | None = None
) -> list[str]:
    """Return up to *num_nodes* usable nodes from distinct Level-0 groups.

    The switch groups are processed in the order reported by
    `scontrol show topology`.  The first usable node of each group is
    selected until *num_nodes* nodes have been picked.  If fewer than
    *num_nodes* groups have usable nodes, the returned list is shorter.
    """
    if num_nodes <= 0:
        return []

    groups = get_switch_groups(level=0)
    usable = get_partition_nodes(partition, reservation=reservation)
    selected = []
    for nodes in groups.values():
        candidates = list(set(nodes) & usable)
        if candidates:
            selected.append(candidates[0])

        if len(selected) == num_nodes:
            break

    return selected
