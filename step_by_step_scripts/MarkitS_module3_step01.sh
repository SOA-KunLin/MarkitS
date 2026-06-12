#!/bin/bash
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/configure.sh"
python() {
    "${PROJECT_PATH:-.}/.venv_yolo/bin/python" "$@"
}

[[ "$INPUT_DIR" = /* ]] || INPUT_DIR="$(pwd)/${INPUT_DIR#./}"
[[ "$OUTPUT_DIR" = /* ]] || OUTPUT_DIR="$(pwd)/${OUTPUT_DIR#./}"
cd "${WEIGHTS_PATH}"

python "${YOLO_PATH}"/detect.py --weights yolov7_R_generate_606sample_ep200.pt --source "${OUTPUT_DIR}"/generate_smiles/ --classes 0 1 2 3 5 6 7 8 13 14 16 --save-txt --project "${OUTPUT_DIR}"/ --name exp_gen --exist-ok  --conf-thres 0.72