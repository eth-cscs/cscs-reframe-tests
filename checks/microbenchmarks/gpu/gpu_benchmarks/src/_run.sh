#!/bin/bash

date
cd icon4py
source .venv/bin/activate

pytest -v \
    -m continuous_benchmarking \
    --benchmark-only \
    --benchmark-warmup=on \
    --benchmark-warmup-iterations=30 \
    --benchmark-json=icon4py_benchmarks.json \
    --backend=dace_gpu \
    --grid=icon_benchmark_regional \
    model/atmosphere/diffusion/tests/diffusion/integration_tests/test_benchmark_diffusion.py::test_diffusion_benchmark
echo

echo "# run done"
date

# TODO: Add this test once gt4py cache works as expected
# model/atmosphere/dycore/tests/dycore/integration_tests/test_benchmark_solve_nonhydro.py::test_benchmark_solve_nonhydro[True-False]
