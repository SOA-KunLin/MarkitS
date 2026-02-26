#!/bin/bash
set -e

echo "📝 Setting up YOLOv7 environment..."
uv venv .venv_yolo --python 3.10
uv pip install --python .venv_yolo/bin/python \
torch==2.0.1 torchvision==0.15.2 \
--index-url https://download.pytorch.org/whl/cu118
uv pip install --python .venv_yolo/bin/python -r yolov7/requirements.txt
#    torch==2.1.0 torchvision==0.16.0 \
#    "protobuf<3.21" "numpy<1.24" "opencv-python==4.7.0.72"

echo "📝 Setting up TexTeller environment..."
uv venv .venv_texteller --python 3.10
uv pip install --python .venv_texteller/bin/python \
torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 \
--index-url https://download.pytorch.org/whl/cu118
uv pip install --python .venv_texteller/bin/python ./TexTeller

echo "📝 Setting up MolScribe environment..."
uv venv .venv_molscribe --python 3.10
uv pip install --python .venv_molscribe/bin/python \
torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 \
--index-url https://download.pytorch.org/whl/cu118
uv pip install --python .venv_molscribe/bin/python ./MolScribe
uv pip install --python .venv_molscribe/bin/python matplotlib huggingface_hub JPype1 cairosvg

echo "📝 Download the pre-built CDK library JAR file..."
wget https://github.com/cdk/cdk/releases/download/cdk-2.11/cdk-2.11.jar

echo "📝 Download the YOLOv7 model weights..."
#wget https://github.com/SOA-KunLin/MarkitS/releases/download/v0.1/weights.tar.gz
#tar zxvf weights.tar.gz

echo "📝 Install MarkitS..."
sed -i "s|^PROJECT_PATH=.*|PROJECT_PATH=\"$(pwd)\"|" "MarkitS"
chmod +x MarkitS

echo "📝 Download Markush image datasets..."
#wget https://github.com/SOA-KunLin/MarkitS/releases/download/v0.1/datasets.tar.gz
#tar zxvf datasets.tar.gz

echo "Installation complete."
