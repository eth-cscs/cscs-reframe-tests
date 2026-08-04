#!/usr/bin/env python

import hatchet as ht
import pandas as pd
import sys
import time

from contextlib import contextmanager
from hatchet.node import Node
from hatchet.readers.hpctoolkit_v4_reader import HPCToolkitV4Reader


@contextmanager
def _allow_nan_int_columns():
    """
    Temporarily make int64 casts tolerate NaN in line/core/node_pid columns
    """
    original_astype = pd.Series.astype

    def fixed_astype(self, dtype, *args, **kwargs):
        if dtype == "int64" and self.name in ("line", "core", "node_pid"):
            self = self.fillna(-1)
        return original_astype(self, dtype, *args, **kwargs)

    pd.Series.astype = fixed_astype
    try:
        yield
    finally:
        pd.Series.astype = original_astype


_original_create_graphframe = HPCToolkitV4Reader.create_graphframe


def _patched_create_graphframe(self):
    with _allow_nan_int_columns():
        gf = _original_create_graphframe(self)

    # Drop duplicate (node, rank, thread) index rows that arise from
    # thread=NaN entries in the HPCT database, then ensure the index is
    # lexicographically sorted so that .loc lookups return scalars.
    gf.dataframe = gf.dataframe[~gf.dataframe.index.duplicated(keep="first")]
    gf.dataframe.sort_index(inplace=True)

    return gf


HPCToolkitV4Reader.create_graphframe = _patched_create_graphframe


# Workaround for hatchet Node comparison with non-Node objects (e.g. pandas
# slices) raising AttributeError on newer pandas versions.
def _node_eq(self, other):
    if not isinstance(other, Node):
        return NotImplemented
    return self._hatchet_nid == other._hatchet_nid


def _node_lt(self, other):
    if not isinstance(other, Node):
        return NotImplemented
    return self._hatchet_nid < other._hatchet_nid


def _node_gt(self, other):
    if not isinstance(other, Node):
        return NotImplemented
    return self._hatchet_nid > other._hatchet_nid


Node.__eq__ = _node_eq
Node.__lt__ = _node_lt
Node.__gt__ = _node_gt


@contextmanager
def timer(label):
    """Time a block and print elapsed seconds."""
    t0 = time.time()
    yield
    print(f'## {label} in {time.time() - t0} seconds')


def main():
    hpct_rpt = sys.argv[1]
    mymetric = 'GXCOPY:H2D (b) (inc)'
    # mymetric = 'CPUTIME (s) (inc)'
    # mymetric = 'PAPI_TOT_CYC (inc)'
    # mymetric = 'GKER (s)'
    print(
        f'hpct_rpt:{hpct_rpt} '
        f'hatchet:{ht.version.__version__} '
        f'pandas:{pd.__version__} '
        f'mymetric:{mymetric}'
    )
    with timer(f'{hpct_rpt} loaded'):
        gf = ht.GraphFrame.from_hpctoolkit(hpct_rpt)

    print(f'default_metric: {gf.default_metric}')
    print(f'collected metrics: {gf.show_metric_columns()}')
    print(f'columns: {list(gf.dataframe.columns)}')
    print(f'index names: {gf.dataframe.index.names}')
    # index names: ['node', 'rank', 'thread']

    # --- https://hatchet.readthedocs.io/en/latest/basic_tutorial.html
    #     -> analyzing-the-graphframe

    # method1: gf.tree
    # print(gf.tree(metric_column=mymetric, depth=1) # default is rk=0,thd=0 !
    with timer('print tree rank 0'):
        print(gf.tree(metric_column=mymetric, depth=2, rank=0, thread=0))
    with timer('print tree rank 1'):
        print(gf.tree(metric_column=mymetric, depth=2, rank=1, thread=0))
    with timer('print tree rank 2'):
        print(gf.tree(metric_column=mymetric, depth=2, rank=2, thread=0))
    with timer('print tree rank 3'):
        print(gf.tree(metric_column=mymetric, depth=2, rank=3, thread=0))

    # method2: direct sum over ranks from the GraphFrame dataframe
    # There are two top-level roots; pick the one whose name starts with "main"
    # That gf.graph.roots has two top-level roots here:
    #   gf.graph.roots[0] -> unknown entry
    #   gf.graph.roots[1] -> main thread         <---
    # + for each rank there are two rows for the root node:
    #   thread == # 0.0 (the value tree() shows) <---
    #   thread == NaN (value 0).
    with timer('direct sum'):
        main_root = next(
            r for r in gf.graph.roots
            if gf.dataframe.loc[r, 'name'].iloc[0].startswith('main')
        )
        per_rank = gf.dataframe.loc[main_root, mymetric]
        # tree() displays the thread==0 row for each rank
        total = per_rank[per_rank.index.get_level_values('thread') == 0].sum()
        print(f'### direct sum over ranks: {total:.3f} / {mymetric}')

    # --- postproc:
    with timer('dot file'):
        with open("_rpt.dot", "w") as dot_file:
            dot_file.write(gf.to_dot())

#     with timer('flamegraph file'):
#         with open("_flame.txt", "w") as folded_stack:
#             folded_stack.write(gf.to_flamegraph(metric=mymetric))


if __name__ == "__main__":
    main()
