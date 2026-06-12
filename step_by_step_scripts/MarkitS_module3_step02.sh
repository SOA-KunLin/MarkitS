#!/bin/bash
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/configure.sh"
python() {
    "${PROJECT_PATH:-.}/.venv_molscribe/bin/python" "$@"
}

[[ "$INPUT_DIR" = /* ]] || INPUT_DIR="$(pwd)/${INPUT_DIR#./}"
[[ "$OUTPUT_DIR" = /* ]] || OUTPUT_DIR="$(pwd)/${OUTPUT_DIR#./}"
cd "${OUTPUT_DIR}"

python "$PROJECT_PATH"/cut_R_image_gen.py