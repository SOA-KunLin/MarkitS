#!/bin/bash
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/configure.sh"
python() {
    "${PROJECT_PATH:-.}/.venv_molscribe/bin/python" "$@"
}

[[ "$OUTPUT_DIR" = /* ]] || OUTPUT_DIR="$(pwd)/${OUTPUT_DIR#./}"
INPUT_DIR="${OUTPUT_DIR}/inputs"
cd "${OUTPUT_DIR}"

cp SMILES_first.csv MarkitS_module1_output.csv