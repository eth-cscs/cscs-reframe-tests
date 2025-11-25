#!/bin/bash

py_version=$(python3 --version 2>&1 |awk '{print $2}')
minor_version=$(echo "$py_version" |cut -d \. -f2)
# echo "$py_version $minor_version"

if [ "$minor_version" -gt "13" ] ;then export RFM_ICON4PY_STOP='Y' ; else export RFM_ICON4PY_STOP='N' ; fi

if [ "$RFM_ICON4PY_STOP" == "Y" ] ;then
    echo "# INFO: $0: python/$py_version is incompatible with this test (try python/3.13), exiting..."
    exit 0

else

    date
    echo "# SLURM_JOBID=$SLURM_JOBID"

    git clone https://github.com/C2SM/icon4py.git
    cd icon4py
    # git checkout 5485bcacb1dbc7688b1e7d276d4e2e28362c5444  # Commit: Update to GT4Py v1.1.0 (#933)
    rm -f uv.lock

    python -m venv .venv

    # --- NVHPC runtime auto-discovery for serialbox (libnvhpcatm.so) ---
    nvhpc_lib="$(find /user-environment -type f -name 'libnvhpcatm.so' 2>/dev/null | head -n1 || true)"
    if [ -n "$nvhpc_lib" ]; then
        nvhpc_dir="$(dirname "$nvhpc_lib")"

        # Export for the current script run (dedupe-safe)
        case ":$LD_LIBRARY_PATH:" in
            *":$nvhpc_dir:"*) : ;;
            *) export LD_LIBRARY_PATH="${nvhpc_dir}${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" ;;
        esac

        echo "# Found libnvhpcatm.so at: $nvhpc_lib"
        echo "# Adding NVHPC lib dir to LD_LIBRARY_PATH: $nvhpc_dir"

        # Persist it for future `source .venv/bin/activate`
        cat >> .venv/bin/activate <<EOF

# Added automatically to make serialbox work (needs libnvhpcatm.so)
nvhpc_dir="$nvhpc_dir"
if [ -d "\$nvhpc_dir" ]; then
    case ":\$LD_LIBRARY_PATH:" in
        *:"\$nvhpc_dir":*) : ;;
        *) export LD_LIBRARY_PATH="\$nvhpc_dir\${LD_LIBRARY_PATH:+:\$LD_LIBRARY_PATH}" ;;
    esac
fi

EOF
    else
        echo "LD_LIBRARY_PATH not modified. Is this expected?"
    fi
    # -------------------------------------------------------------------

    source .venv/bin/activate

    pip install --upgrade pip
    pip install uv

    uv sync --extra all --python $(which python) --active

    uv pip uninstall mpi4py && \
    uv pip install --no-binary mpi4py mpi4py && \
    uv pip install git+https://github.com/cupy/cupy.git

    echo "# install done"
    date

fi
