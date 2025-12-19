#!/bin/bash

date
echo "# SLURM_JOBID=$SLURM_JOBID"

unset PYTHONPATH

git clone https://github.com/C2SM/icon4py.git
cd icon4py
git checkout 15b7406d9385a189abaaa71b14851d1491b231f1  # Commit: Update to GT4Py v1.1.2 (#969)

# Install uv locally
curl -LsSf https://astral.sh/uv/install.sh | UV_UNMANAGED_INSTALL="$PWD/bin" sh
export PATH="$PWD/bin:$PATH"

# Install ICON4Py
HOME="$PWD/_home" uv python install $ICON4PY_PYTHON_VERSION
uv sync --extra all --python $PWD/_home/.local/bin/python$ICON4PY_PYTHON_VERSION

# Activate virtual environment
source .venv/bin/activate

# Compatibility for both Daint & Beverin
mpi4py_ver=$(uv pip show mpi4py | awk '/Version:/ {print $2}')
uv pip uninstall mpi4py && uv pip install --no-binary mpi4py "mpi4py==$mpi4py_ver"
uv pip install git+https://github.com/cupy/cupy.git

# Patch Gt4Py to avoid cache issues
uv pip uninstall gt4py
git clone --branch v1.1.2 https://github.com/GridTools/gt4py.git
python3 -c '
import sys
from pathlib import Path

file_path = Path("gt4py/src/gt4py/next/otf/stages.py")
lines = file_path.read_text().splitlines()

new_lines = []
iterator = iter(lines)

found = False
for line in iterator:
    # 1. Detect the start of the block we want to change
    if "program_hash = utils.content_hash(" in line:
        found = True
        # Insert the NEW pre-calculation line
        # We steal the indentation from the current line to be safe
        indent = line[:line.find("program_hash")]
        new_lines.append(f"{indent}offset_provider_arrays = {{key: value.ndarray if hasattr(value, \"ndarray\") else value for key, value in offset_provider.items()}}")
        
        # Add the modified content_hash call
        new_lines.append(f"{indent}program_hash = utils.content_hash(")
        new_lines.append(f"{indent}    (")
        new_lines.append(f"{indent}        program.fingerprint(),")
        new_lines.append(f"{indent}        sorted(offset_provider_arrays.items(), key=lambda el: el[0]),")
        
        # Skip the OLD lines from the iterator until we hit "column_axis"
        # We blindly consume lines until we find the one we keep
        while True:
            skipped_line = next(iterator)
            if "column_axis," in skipped_line:
                new_lines.append(skipped_line) # Add column_axis line back
                break
    else:
        new_lines.append(line)

if found:
    file_path.write_text("\n".join(new_lines) + "\n")
    print("Patch applied.")
else:
    print("Target line not found.")
    sys.exit(1)
'
uv pip install -e ./gt4py

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

echo "# install done"
date
