# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Helpers for selecting Slurm nodes based on the tree topology.

The functions parse `scontrol show topology` and optionally intersect the
reported switch groups with the currently available nodes of a target
partition.  This lets ReFrame checks place jobs on nodes that span distinct
Level-0 switch groups (or, conversely, keep all nodes inside a single group).
"""

import json
import re
import subprocess


def _run(cmd):
    return subprocess.check_output(cmd, universal_newlines=True,
                                   stderr=subprocess.STDOUT)


def expand_hostlist(nodelist):
    """Expand a Slurm compressed hostlist into a list of node names."""
    if not nodelist:
        return []

    out = _run(['scontrol', 'show', 'hostnames', nodelist])
    return [n.strip() for n in out.strip().splitlines() if n.strip()]


def get_switch_groups(level=0):
    """Return a dict mapping switch name to node list for the given level."""
    out = _run(['scontrol', 'show', 'topology'])
    groups = {}
    pattern = re.compile(
        r'SwitchName=(\S+)\s+Level=(\d+)\s+LinkSpeed=\d+\s+Nodes=(\S+)'
    )
    for line in out.splitlines():
        match = pattern.match(line)
        if match:
            switch_name, switch_level, nodelist = match.groups()
            if int(switch_level) == level:
                groups[switch_name] = expand_hostlist(nodelist)

    return groups


def get_partition_nodes(partition,
                        required_state=None,
                        exclude_states=None,
                        allow_reserved=False):
    """Return the set of usable nodes in *partition*.

    By default only nodes that contain the ``IDLE`` state flag are returned,
    and nodes with the ``RESERVED`` flag are excluded unless a reservation is
    being used.

    :param partition: Slurm partition name.
    :param required_state: List of state flags that must all be present.  If
        ``None``, defaults to ``['IDLE']``.
    :param exclude_states: List of state flags that must not be present.  If
        ``None``, defaults to common non-usable flags.
    :param allow_reserved: If ``False`` (default), exclude nodes with the
        ``RESERVED`` flag.  Set to ``True`` when the job is submitted with a
        Slurm reservation.
    :returns: A set of node names.
    """
    if required_state is None:
        required_state = ['IDLE']

    if exclude_states is None:
        exclude_states = [
            'DOWN', 'DRAIN', 'DRAINED', 'MAINTENANCE', 'ALLOCATED', 'MIXED',
            'COMPLETING', 'NOT_RESPONDING', 'UNKNOWN'
        ]

    if not allow_reserved:
        exclude_states = list(exclude_states) + ['RESERVED']

    out = _run(['scontrol', 'show', 'nodes', '--json'])
    data = json.loads(out)
    nodes = set()
    for node in data.get('nodes', []):
        partitions = node.get('partitions', [])
        if partition not in partitions:
            continue

        state = node.get('state', [])
        if not all(flag in state for flag in required_state):
            continue

        if any(flag in state for flag in exclude_states):
            continue

        nodes.add(node['name'])

    return nodes


def select_nodes_across_groups(num_nodes, partition,
                               required_state=None,
                               exclude_states=None,
                               allow_reserved=False):
    """Return up to *num_nodes* usable nodes from distinct Level-0 groups.

    The switch groups are processed in the order reported by
    ``scontrol show topology``.  The first usable node of each group is
    selected until *num_nodes* nodes have been picked.  If fewer than
    *num_nodes* groups have usable nodes, the returned list is shorter.
    """
    groups = get_switch_groups(level=0)
    usable_nodes = get_partition_nodes(partition, required_state,
                                       exclude_states,
                                       allow_reserved=allow_reserved)
    selected = []
    for nodes in groups.values():
        candidates = [n for n in nodes if n in usable_nodes]
        if candidates:
            selected.append(candidates[0])

        if len(selected) == num_nodes:
            break

    return selected


def select_nodes_in_group(num_nodes, partition,
                          required_state=None,
                          exclude_states=None,
                          allow_reserved=False):
    """Return up to *num_nodes* usable nodes that all belong to one Level-0
    group.

    The group with the largest number of available nodes is chosen so that
    the request is most likely satisfiable.
    """
    groups = get_switch_groups(level=0)
    usable_nodes = get_partition_nodes(partition, required_state,
                                       exclude_states,
                                       allow_reserved=allow_reserved)
    best_group = []
    for nodes in groups.values():
        candidates = [n for n in nodes if n in usable_nodes]
        if len(candidates) > len(best_group):
            best_group = candidates

    return best_group[:num_nodes]
