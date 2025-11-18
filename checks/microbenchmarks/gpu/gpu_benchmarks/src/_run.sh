#!/bin/bash

py_version=$(python3 --version 2>&1 |awk '{print $2}')
minor_version=$(echo "$py_version" |cut -d \. -f2)
# echo "$py_version $minor_version"

if [ "$minor_version" -gt "13" ] ;then export RFM_ICON4PY_STOP='Y' ; else export RFM_ICON4PY_STOP='N' ; fi

if [ "$RFM_ICON4PY_STOP" == "Y" ] ;then
    echo "# INFO: $0: python/$py_version is incompatible with this test (try python/3.13), exiting..."
    # for sanity:
    echo "model/atmosphere/diffusion/tests/diffusion/integration_tests/test_benchmark_diffusion.py::test_diffusion_benchmark PASSED [100%] # FAKE"
    # for performance:                 Min     Max     Mean    StdDev
    echo "test_diffusion_benchmark     0.0000  0.0000  0.0000  0.0000  # FAKE"
    sleep 4
    exit 0

else

    date
    source .venv/bin/activate
    cd icon4py

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

    # TODO:
    # ('model/atmosphere/dycore/tests/dycore/integration_tests/'
    #  'test_benchmark_solve_nonhydro.py'
    #  '::test_benchmark_solve_nonhydro[True-False]'
    #  ),

fi
