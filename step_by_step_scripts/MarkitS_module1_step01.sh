#!/bin/bash
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/configure.sh"
python() {
    "${PROJECT_PATH:-.}/.venv_yolo/bin/python" "$@"
}

[[ "$INPUT_DIR" = /* ]] || INPUT_DIR="$(pwd)/${INPUT_DIR#./}"
[[ "$OUTPUT_DIR" = /* ]] || OUTPUT_DIR="$(pwd)/${OUTPUT_DIR#./}"
mkdir -p "${OUTPUT_DIR}"
cd "${WEIGHTS_PATH}"

python "${YOLO_PATH}"/detect.py --weights yolov7_circle_210sample_ep200.pt --source "${INPUT_DIR}"/ --classes 0 --save-txt --project "${OUTPUT_DIR}"/ --name exp_circle --exist-ok --conf-thres 0.93