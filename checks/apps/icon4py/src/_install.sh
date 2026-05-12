#!/bin/bash

date
echo "# SLURM_JOBID=$SLURM_JOBID"

unset PYTHONPATH

git clone --depth 1 --single-branch --branch main https://github.com/C2SM/icon4py.git
cd icon4py

# Install uv locally
curl -LsSf https://astral.sh/uv/install.sh | UV_UNMANAGED_INSTALL="$PWD/bin" sh
export PATH="$PWD/bin:$PATH"

# Install ICON4Py
HOME="$PWD/_home" uv python install $ICON4PY_PYTHON_VERSION
if [ -z "$UV_GPU_SUPPORT" ]; then
    echo "ERROR: UV_GPU_SUPPORT must be set" >&2
    exit 1
elif [ "$UV_GPU_SUPPORT" = "rocm6" ]; then
    echo "Branch: rocm6 (no --extra \$UV_GPU_SUPPORT flag)"
    echo "Running: uv sync --extra all --python $PWD/_home/.local/bin/python$ICON4PY_PYTHON_VERSION"
    uv sync --extra all --python $PWD/_home/.local/bin/python$ICON4PY_PYTHON_VERSION
    uv_sync_rc=$?
else
    echo "Branch: generic GPU support ($UV_GPU_SUPPORT)"
    echo "Running: uv sync --extra all --extra $UV_GPU_SUPPORT --python $PWD/_home/.local/bin/python$ICON4PY_PYTHON_VERSION"
    uv sync --extra all --extra "$UV_GPU_SUPPORT" --python $PWD/_home/.local/bin/python$ICON4PY_PYTHON_VERSION
    uv_sync_rc=$?
fi

# If uv sync failed, wipe the uv cache so subsequent runs start clean.
# A corrupted/partial cache is a common cause of repeat failures.
if [ "$uv_sync_rc" -ne 0 ]; then
    echo "ERROR: uv sync failed with exit code $uv_sync_rc" >&2
    cache_to_clear="${UV_CACHE_DIR:-${SCRATCH:+$SCRATCH/.cache/uv}}"
    if [ -n "$cache_to_clear" ] && [ -d "$cache_to_clear" ]; then
        echo "# Removing uv cache for subsequent runs: $cache_to_clear"
        rm -rf "$cache_to_clear"
    else
        echo "# uv cache dir not found or not set (UV_CACHE_DIR='$UV_CACHE_DIR', SCRATCH='$SCRATCH')" >&2
    fi
    exit "$uv_sync_rc"
fi

source .venv/bin/activate

# Compatibility for both Daint & Beverin
mpi4py_ver=$(uv pip show mpi4py | awk '/Version:/ {print $2}')
uv pip uninstall mpi4py && uv pip install --no-binary mpi4py "mpi4py==$mpi4py_ver"
if [ "$UV_GPU_SUPPORT" = "rocm6" ]; then
    uv pip install git+https://github.com/cupy/cupy.git@v13.6.0
elif [[ "$UV_GPU_SUPPORT" == rocm* ]]; then
    echo "Applying CuPy hip_workaround.cuh patch for ROCm support (CuPy 14.0.1 bug)"
    CUPY_HIP_WORKAROUND=$(python3 -c "import cupy, os; print(os.path.join(os.path.dirname(cupy.__file__), '_core', 'include', 'cupy', 'hip_workaround.cuh'))" 2>/dev/null)
    if [ -f "$CUPY_HIP_WORKAROUND" ]; then
        sed -i 's/#if (HIP_VERSION < 60200000) || defined(HIP_DISABLE_WARP_SYNC_BUILTINS)/#if 1  \/\/ Patched: force mask-stripping for all ROCm versions (CuPy 14.0.1 bug)/' "$CUPY_HIP_WORKAROUND"
        echo "# Patched CuPy hip_workaround.cuh: $CUPY_HIP_WORKAROUND"
    fi
fi

################################################################################
# NVHPC runtime auto-discovery for serialbox (libnvhpcatm.so)
################################################################################
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
else
    echo "LD_LIBRARY_PATH not modified for NVHPC (libnvhpcatm.so not found). Is this expected?"
fi

# Persist a dynamic NVHPC discovery into .venv/bin/activate so that every
# future activation re-discovers libnvhpcatm.so (if present on that cluster).
cat >> .venv/bin/activate <<'EOF'

# Added automatically to make serialbox work (needs libnvhpcatm.so)
nvhpc_lib=$(find /user-environment -type f -name 'libnvhpcatm.so' 2>/dev/null | head -n1 || true)
if [ -n "$nvhpc_lib" ]; then
    nvhpc_dir=$(dirname "$nvhpc_lib")
    if [ -d "$nvhpc_dir" ]; then
        case ":$LD_LIBRARY_PATH:" in
            *:"$nvhpc_dir":*) : ;;
            *) export LD_LIBRARY_PATH="$nvhpc_dir${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" ;;
        esac
    fi
fi

EOF

################################################################################
# Serialbox / libstdc++ auto-discovery
################################################################################

# 1) Fix for the current script run: find libSerialboxC.so, ask ldd which
#    libstdc++.so it uses, and prepend that directory to LD_LIBRARY_PATH.
serialbox_so="$(find "$PWD/.venv" -maxdepth 7 -type f -name 'libSerialboxC.so*' 2>/dev/null | head -n1 || true)"
if [ -n "$serialbox_so" ] && [ -f "$serialbox_so" ]; then
    libstdcpp_path="$(ldd "$serialbox_so" 2>/dev/null | awk '/libstdc\+\+\.so/ {print $3; exit}')"
    if [ -n "$libstdcpp_path" ] && [ -f "$libstdcpp_path" ]; then
        libstdcpp_dir="$(dirname "$libstdcpp_path")"

        case ":$LD_LIBRARY_PATH:" in
            *":$libstdcpp_dir:"*) : ;;
            *) export LD_LIBRARY_PATH="${libstdcpp_dir}${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" ;;
        esac

        echo "# Serialbox library      : $serialbox_so"
        echo "# Serialbox libstdc++    : $libstdcpp_path"
        echo "# Adding libstdc++ dir to LD_LIBRARY_PATH: $libstdcpp_dir"
    else
        echo "# WARNING: Could not determine libstdc++.so used by $serialbox_so"
    fi
else
    echo "# NOTE: libSerialboxC.so not found under .venv yet (is serialbox installed?)."
fi

# 2) Persist this logic into .venv/bin/activate so every future activation
#    automatically discovers Serialbox and its libstdc++ and updates LD_LIBRARY_PATH.
cat >> .venv/bin/activate <<'EOF'

# Added automatically so Serialbox can always find the right libstdc++
if [ -n "$VIRTUAL_ENV" ]; then
    serialbox_so=$(find "$VIRTUAL_ENV" -maxdepth 7 -type f -name 'libSerialboxC.so*' 2>/dev/null | head -n 1)
    if [ -n "$serialbox_so" ] && [ -f "$serialbox_so" ]; then
        libstdcpp_path=$(ldd "$serialbox_so" 2>/dev/null | awk '/libstdc\+\+\.so/ {print $3; exit}')
        if [ -n "$libstdcpp_path" ] && [ -f "$libstdcpp_path" ]; then
            libstdcpp_dir=$(dirname "$libstdcpp_path")
            case ":$LD_LIBRARY_PATH:" in
                *:"$libstdcpp_dir":*) : ;;
                *) export LD_LIBRARY_PATH="$libstdcpp_dir${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" ;;
            esac
        fi
    fi
fi

EOF

################################################################################
# Trim uv cache to keep Lustre happy
################################################################################
if command -v uv >/dev/null 2>&1; then
    echo "# Pruning uv cache (--ci: keep source-built wheels, drop the rest)"
    uv cache prune --ci || echo "# WARNING: 'uv cache prune --ci' failed (non-fatal)" >&2
fi

################################################################################

echo "# install done"
date
