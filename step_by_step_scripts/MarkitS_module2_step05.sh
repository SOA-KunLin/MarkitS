#!/bin/bash
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/configure.sh"
python() {
    "${PROJECT_PATH:-.}/.venv_molscribe/bin/python" "$@"
}

[[ "$INPUT_DIR" = /* ]] || INPUT_DIR="$(pwd)/${INPUT_DIR#./}"
[[ "$OUTPUT_DIR" = /* ]] || OUTPUT_DIR="$(pwd)/${OUTPUT_DIR#./}"
cd "${OUTPUT_DIR}"

python "$PROJECT_PATH"/markitS_intermediate_no_gen.py "MarkitS_module2_output.csv" "false"