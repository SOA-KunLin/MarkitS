# MarkitS

This is the repository for **MarkitS: An Image-to-SMILES Parsing Workflow for Markush Structures structure**.

## Requirements
1. Install Python
```bash
apt update
apt install -y python3 python3-pip python3-venv
```
2. Install uv (Python package manager)
```bash
pip install uv
```
3. Install the OpenCV dependency
```bash
apt update
apt install -y libgl1-mesa-glx libglib2.0-0
```
4. Install the Cairo Graphics Library (System-level dependencies required by CairoSVG)
```bash
apt update
apt install -y libcairo2-dev libffi-dev python3-dev
```
5. Install Java
```bash
apt update
apt install -y default-jdk
```

## Installation
1. Run the following command to install the package and its dependencies.
```bash
git clone --recursive git@github.com:SOA-KunLin/MarkitS.git
cd MarkitS
chmod +x install.sh
./install.sh
```
> [!NOTE]
> The `install.sh` script uses the CUDA 11.8 runtime.

> [!TIP]
> MarkitS can also be run with Docker. Refer to [Run MarkitS with docker](#docker) for setup and usage instructions.


## Usage
```bash
MarkitS -i <input_folder> -o <output_folder> [--output-intermediate]
```
* `<input_folder>` is the path to the folder containing the Markush structure images to be processed.
* `<output_folder>` is the path where the final output file (`MarkitS.csv`) and all intermediate files are stored.
* `--output-intermediate` (optional) enables the output of intermediate SMILES to `MarkitS.csv`. If not specified, intermediate SMILES will not be generated.

## Experiments
The commands below reproduce MarkitS’s results for the statistics shown in the manuscript tables.
```bash
MarkitS -i datasets/development -o development_MarkitS --output-intermediate
MarkitS -i datasets/validation -o validation_MarkitS --output-intermediate
MarkitS -i datasets/testing -o testing_MarkitS --output-intermediate
```
The resulting SMILES are saved in `development_MarkitS/MarkitS.csv`, `validation_MarkitS/MarkitS.csv`, and `testing_MarkitS/MarkitS.csv`, respectively.

## Docker
You can build a Docker image for MarkitS:
```bash
docker build . -t markits
```
Or pull a pre-built image from [Docker Hub](https://hub.docker.com/r/soakunlin/markits).

To use MarkitS with Docker, run the following command:
```bash
docker run --rm --gpus all -v "$(pwd):/workspace" \
   markits MarkitS -i <input_folder> -o <output_folder> --output-intermediate
```
> [!NOTE]
> The above command assumes that `<input_folder>` is located in the current working directory. The `<output_folder>` directory will be created in the same location.

To reproduce MarkitS’s results for the statistics shown in the manuscript tables, use the following commands:
```bash
docker run --rm --gpus all -v "$(pwd):/workspace" markits \
   MarkitS -i /MarkitS/datasets/development -o development_MarkitS --output-intermediate
docker run --rm --gpus all -v "$(pwd):/workspace" markits \
   MarkitS -i /MarkitS/datasets/validation -o validation_MarkitS --output-intermediate
docker run --rm --gpus all -v "$(pwd):/workspace" markits \
   MarkitS -i /MarkitS/datasets/testing -o testing_MarkitS --output-intermediate
```