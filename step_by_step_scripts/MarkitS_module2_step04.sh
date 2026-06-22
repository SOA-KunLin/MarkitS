#!/bin/bash
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/configure.sh"
python() {
    "${PROJECT_PATH:-.}/.venv_molscribe/bin/python" "$@"
}

[[ "$OUTPUT_DIR" = /* ]] || OUTPUT_DIR="$(pwd)/${OUTPUT_DIR#./}"
INPUT_DIR="${OUTPUT_DIR}/inputs"
cd "${OUTPUT_DIR}"

python "$PROJECT_PATH"/SMILES_generate.py