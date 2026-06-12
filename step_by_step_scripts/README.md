# MarkitS - Step-by-Step Scripts

This folder contains scripts for users who want to execute the MarkitS processing pipeline with greater control over each step.

## Usage
1. Set the paths for `<input_folder>` and `output_folder`:
```bash
export INPUT_DIR=<input_folder>
export OUTPUT_DIR='<output_folder>
```
2. Run the scripts in the order shown below:
```bash
MarkitS_module1_step01.sh
MarkitS_module1_step02.sh
MarkitS_module1_step03.sh
MarkitS_module1_step04.sh
MarkitS_module1_step05.sh
MarkitS_module1_step06.sh
MarkitS_module1_step07.sh
MarkitS_module1_step08.sh
MarkitS_module1_step09.sh
MarkitS_module1_step10.sh
MarkitS_module1_step11.sh
MarkitS_module1_step12.sh
MarkitS_module1_step13.sh
MarkitS_module1_step14.sh

MarkitS_module2_step01.sh
MarkitS_module2_step02.sh
MarkitS_module2_step03.sh
MarkitS_module2_step04.sh
MarkitS_module2_step05.sh

MarkitS_module3_step01.sh
MarkitS_module3_step02.sh
MarkitS_module3_step03.sh
MarkitS_module3_step04.sh
MarkitS_module3_step05.sh
MarkitS_module3_step06.sh
```

## Docker
To run the step-by-step scripts with Docker, use the following command:
```bash
docker run --rm --gpus all -v "$(pwd):/workspace" \
  -e INPUT_DIR="<input_folder>" \
  -e OUTPUT_DIR="<output_folder>" \
  markits MarkitS_module<module_number>_step<step_number>.sh
```
> [!NOTE]
> The above command assumes that `<input_folder>` is located in the current working directory. The `<output_folder>` directory will be created in the same location.