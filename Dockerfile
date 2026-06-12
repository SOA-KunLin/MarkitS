FROM nvidia/cuda:11.8.0-devel-ubuntu22.04

ENV TORCH_CUDA_ARCH_LIST="7.0 8.0 8.6 9.0"
ENV FORCE_CUDA="1"

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates python3 python3-pip python3-venv git wget \
    libgl1-mesa-glx libglib2.0-0 \
    libcairo2-dev libffi-dev python3-dev \
    default-jdk \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /MarkitS

COPY . .

RUN chmod +x ./install.sh

RUN ./install.sh

ENV PATH="/MarkitS:/MarkitS/step_by_step_scripts:${PATH}"

WORKDIR /workspace

CMD ["MarkitS"]
