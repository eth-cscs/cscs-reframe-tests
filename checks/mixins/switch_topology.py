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

import json
import re
import subprocess


def _get_l0_switches():
    """Return the list of live Level-0 switch names.

    Called at module import time (on a login node) to populate ReFrame
    test parameters. Returns an empty list if `scontrol` is not
    available (e.g. CI runners, non-Slurm systems), in which case
    parameterized tests will have no variants and effectively skip.
    """
    try:
        output = subprocess.check_output(
            ['scontrol', 'show', 'topology'], universal_newlines=True,
            stderr=subprocess.STDOUT,
        )
    except (OSError, subprocess.CalledProcessError):
        return []

    pattern = re.compile(r'SwitchName=(\S+)\s+Level=(\d+)')
    switches = []
    for line in output.splitlines():
        match = pattern.match(line)
        if match and int(match.group(2)) == 0:
            switches.append(match.group(1))

    return switches


def _run(cmd):
    return subprocess.check_output(cmd, universal_newlines=True,
                                   stderr=subprocess.STDOUT)


def expand_hostlist(nodelist):
    """Expand a Slurm compressed hostlist into a list of node names."""
    if not nodelist:
        return []

    out = _run(['scontrol', 'show', 'hostnames', nodelist])
    return [n.strip() for n in out.strip().splitlines() if n.strip()]


def expand_reservation(name):
    """Return the list of nodes in the given Slurm reservation."""
    try:
        out = _run(['scontrol', 'show', 'reservation', name])
    except subprocess.CalledProcessError:
        return []

    match = re.search(r'Nodes=(\S+)', out)
    if not match:
        return []

    return expand_hostlist(match.group(1))


def get_switch_groups(level=0):
    """Return a dict mapping switch name to node list for the given level.

    Invokes `scontrol show topology` on the host.  The output cannot be
    supplied from a ReFrame test's `self.stdout` because that is a
    deferred expression, not a plain string, at the point helpers run
    (during `setup`/`run` hooks).  See `SwitchTopologyCheck` for the
    known trade-off: it runs `scontrol` as its own executable *and*
    this helper spawns a second, redundant call.
    """
    output = _run(['scontrol', 'show', 'topology'])

    groups = {}
    pattern = re.compile(
        r'SwitchName=(\S+)\s+Level=(\d+)\s+LinkSpeed=\d+\s+Nodes=(\S+)'
    )
    for line in output.splitlines():
        match = pattern.match(line)
        if match:
            switch_name, switch_level, nodelist = match.groups()
            if int(switch_level) == level:
                groups[switch_name] = expand_hostlist(nodelist)

    return groups


def get_switch_group_names(level=0):
    """Return a sorted list of switch names at the given level.

    Wraps :func:`get_switch_groups` and returns only the keys.
    """
    return sorted(get_switch_groups(level).keys())


def get_partition_nodes(partition, reservation=None):
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
        all_nodes = _all_partition_nodes(partition)
        return reserved & all_nodes

    out = _run(['scontrol', 'show', 'nodes', '--json'])
    data = json.loads(out)
    # Exclude COMPLETING: a node in IDLE+COMPLETING matches as IDLE but
    # Slurm won't allocate it, causing indefinite hangs.
    exclude = ('DRAIN', 'MAINTENANCE', 'COMPLETING')
    nodes = set()
    for node in data.get('nodes', []):
        if partition not in node.get('partitions', []):
            continue

        state = node.get('state', [])
        if 'IDLE' not in state:
            continue

        if any(flag in state for flag in exclude):
            continue

        nodes.add(node['name'])

    return nodes


def _all_partition_nodes(partition):
    """Return all node names in *partition* regardless of state."""
    out = _run(['scontrol', 'show', 'nodes', '--json'])
    data = json.loads(out)
    return {
        node['name'] for node in data.get('nodes', [])
        if partition in node.get('partitions', [])
    }


def select_nodes_across_groups(num_nodes, partition, reservation=None):
    """Return up to *num_nodes* usable nodes from distinct Level-0 groups.

    The switch groups are processed in the order reported by
    `scontrol show topology`.  The first usable node of each group is
    selected until *num_nodes* nodes have been picked.  If fewer than
    *num_nodes* groups have usable nodes, the returned list is shorter.
    """
    groups = get_switch_groups(level=0)
    usable = get_partition_nodes(partition, reservation=reservation)
    selected = []
    for nodes in groups.values():
        candidates = [n for n in nodes if n in usable]
        if candidates:
            selected.append(candidates[0])

        if len(selected) == num_nodes:
            break

    return selected
