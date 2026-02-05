#!/bin/bash
set -e

# Configuration
VENV_PATH=".venv"
ACTIVATE_SCRIPT="$VENV_PATH/bin/activate"
PYTHON_VERSION="3.10"
UV_CMD="uv"
REQUIREMENTS_FILE="requirements.txt"  # Default to CPU

# Parse arguments
MODE="cpu"
if [[ "$1" == "--gpu" ]]; then
    MODE="gpu"
    REQUIREMENTS_FILE="requirements.gpu.txt"
elif [[ "$1" == "--cpu" ]]; then
    MODE="cpu"
    REQUIREMENTS_FILE="requirements.txt"
elif [[ -n "$1" ]]; then
    echo "Unknown argument: $1"
    echo "Usage: ./setup_linux.sh [--cpu | --gpu]"
    exit 1
fi

echo "Setting up for mode: $MODE"
echo "Using requirements file: $REQUIREMENTS_FILE"

# Functions
ensure_uv_exists() {
    if ! command -v "$UV_CMD" &> /dev/null; then
        echo "Error: 'uv' is not installed or not on PATH."
        echo "Install uv and retry (e.g., 'curl -LsYz https://astral.sh/uv/install.sh | sh')."
        exit 1
    fi
}

ensure_venv() {
    if [[ -d "$VENV_PATH" ]]; then
        echo ".venv already exists. Skipping creation."
        return
    fi

    echo ".venv not found. Creating virtual environment with Python $PYTHON_VERSION using uv..."
    if ! "$UV_CMD" venv --python "$PYTHON_VERSION" "$VENV_PATH"; then
        echo "Error: uv failed to create the virtual environment."
        exit 1
    fi
}

activate_venv() {
    if [[ ! -f "$ACTIVATE_SCRIPT" ]]; then
        echo "Error: Activation script not found at $ACTIVATE_SCRIPT"
        exit 1
    fi

    echo "Activating virtual environment..."
    # shellcheck source=/dev/null
    source "$ACTIVATE_SCRIPT"
    echo "Virtual environment activated."
    
    if command -v python &> /dev/null; then
        python --version
    else
        echo "Warning: python not found in the activated environment."
    fi
}

install_requirements() {
    if [[ ! -f "$REQUIREMENTS_FILE" ]]; then
        echo "Error: $REQUIREMENTS_FILE not found. Skipping dependency installation."
        return
    fi

    echo "Installing dependencies from $REQUIREMENTS_FILE using uv..."
    if ! "$UV_CMD" pip install -r "$REQUIREMENTS_FILE"; then
        echo "Error: uv pip failed to install requirements."
        exit 1
    fi

    echo "Dependencies installed successfully."
}

# Main flow
ensure_uv_exists
ensure_venv
activate_venv
install_requirements