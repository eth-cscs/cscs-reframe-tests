#!/bin/bash

date

unset PYTHONPATH

cd icon4py
source .venv/bin/activate

pytest -sv \
-m continuous_benchmarking \
--benchmark-only \
--benchmark-warmup=on \
--benchmark-min-rounds=100 \
--benchmark-warmup-iterations=30 \
--benchmark-disable-gc \
--benchmark-json=icon4py_benchmarks.json \
--backend=dace_gpu \
--grid=icon_benchmark_regional \
--benchmark-time-unit=ms \
"model/atmosphere/diffusion/tests/diffusion/integration_tests/test_benchmark_diffusion.py::test_diffusion_benchmark" \
"model/atmosphere/dycore/tests/dycore/integration_tests/test_benchmark_solve_nonhydro.py::test_benchmark_solve_nonhydro[True-False]"
pytest_exit_code=$?
echo

# If pytest failed, wipe the gt4py on-disk build cache so the next run starts clean.
if [ "$pytest_exit_code" -ne 0 ]; then
    echo "# pytest failed with exit code $pytest_exit_code"
    if [ -n "$GT4PY_BUILD_CACHE_DIR" ] && [ -d "$GT4PY_BUILD_CACHE_DIR" ]; then
        echo "# Deleting gt4py build cache: $GT4PY_BUILD_CACHE_DIR"
        rm -rf -- "$GT4PY_BUILD_CACHE_DIR"
    else
        echo "# GT4PY_BUILD_CACHE_DIR is not set or does not exist; nothing to clear."
    fi
fi

# Cleanup
deactivate
cd ..
rm -rf icon4py

echo "# run done"
date
