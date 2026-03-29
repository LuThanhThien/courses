#!/usr/bin/env bash
set -e

echo "🔹 Installing system dependencies..."
sudo apt update
sudo apt install -y wslu curl

# -------------------------------
# Check if conda exists
# -------------------------------
if ! command -v conda >/dev/null 2>&1; then
    echo "⚠️ Conda not found. Installing Miniconda..."

    MINICONDA=Miniconda3-latest-Linux-x86_64.sh
    curl -fsSL https://repo.anaconda.com/miniconda/$MINICONDA -o $MINICONDA

    bash $MINICONDA -b -p $HOME/miniconda
    rm $MINICONDA

    # Initialize conda
    eval "$($HOME/miniconda/bin/conda shell.bash hook)"
    conda init bash
else
    echo "✅ Conda already installed."
    eval "$(conda shell.bash hook)"
fi

# -------------------------------
# Create / activate environment
# -------------------------------
ENV_NAME=fpcv
PYTHON_VERSION=3.8

if conda env list | grep -q "^$ENV_NAME"; then
    echo "✅ Conda environment '$ENV_NAME' already exists."
else
    echo "🔹 Creating conda environment '$ENV_NAME'..."
    conda create -y -n $ENV_NAME python=$PYTHON_VERSION
fi

conda activate $ENV_NAME

# -------------------------------
# Install Python requirements
# -------------------------------
if [ -f requirements.txt ]; then
    echo "🔹 Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "⚠️ requirements.txt not found!"
fi

echo "🎉 Setup complete. Environment '$ENV_NAME' is ready."
