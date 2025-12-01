#!/usr/bin/env bash
set -e

ENV_NAME="astro-mini"
ENV_PATH="$HOME/.conda/envs/$ENV_NAME"
DISPLAY_NAME="Astro (mini)"

echo ">> Checking if kernel is already registered..."

KERNEL_DIR="$HOME/.local/share/jupyter/kernels/$ENV_NAME"

if [ ! -d "$ENV_PATH" ]; then
    echo "ERROR: Environment not found at $ENV_PATH"
    exit 1
fi

# =============================================================================
# Register kernel only if not already installed
# =============================================================================
if [ ! -d "$KERNEL_DIR" ]; then
    echo ">> Kernel not found. Installing ipykernel and registering kernel..."

    "$ENV_PATH/bin/python" -m pip install --upgrade ipykernel

    "$ENV_PATH/bin/python" -m ipykernel install \
        --user \
        --name "$ENV_NAME" \
        --display-name "$DISPLAY_NAME"

    echo ">> Kernel registered."
else
    echo ">> Kernel already registered at:"
    echo "   $KERNEL_DIR"
fi

echo ""
echo ">> Installed kernels:"
jupyter kernelspec list