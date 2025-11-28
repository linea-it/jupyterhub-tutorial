#!/usr/bin/env bash
set -e

# =============================================================================
# SETTINGS
# =============================================================================
ENV_NAME="astro"
ENV_PATH="$HOME/.conda/envs/$ENV_NAME"
YAML_FILE="astro.yml"

echo ">> Environment name: $ENV_NAME"
echo ">> Environment path: $ENV_PATH"
echo ">> YAML file: $YAML_FILE"

# =============================================================================
# HELPER: Run conda quietly and without upgrade warnings
# =============================================================================
conda_silent() {
    conda "$@" --quiet 2> >(grep -v "A newer version of conda exists" >&2)
}

# =============================================================================
# Use libmamba as solver
# =============================================================================
echo ">> Setting libmamba solver..."
conda_silent config --set solver libmamba

# =============================================================================
# CREATE ENVIRONMENT IF NOT EXISTS
# =============================================================================
if [ ! -d "$ENV_PATH" ]; then
    echo ">> Environment not found. Performing cleanup before install..."
    conda_silent clean -a -y
    rm -rf ~/.cache/pip/*

    echo ">> Creating environment $ENV_NAME ..."
    conda_silent env create -f "$YAML_FILE" -p "$ENV_PATH" -y
else
    echo ">> Environment already exists at $ENV_PATH"
fi

# =============================================================================
# EXPORT ENVIRONMENT VARIABLES FOR THIS SESSION
# =============================================================================
echo ">> Exporting environment variables..."

export CONDA_DEFAULT_ENV="$ENV_NAME"
export CONDA_PREFIX="$ENV_PATH"
export PATH="$ENV_PATH/bin:/opt/conda/condabin:/opt/conda/bin:$PATH"
export XML_CATALOG_FILES="file://$ENV_PATH/etc/xml/catalog file:///etc/xml/catalog"
export GSETTINGS_SCHEMA_DIR="$ENV_PATH/share/glib-2.0/schemas"

echo "CONDA_DEFAULT_ENV=$CONDA_DEFAULT_ENV"
echo "CONDA_PREFIX=$CONDA_PREFIX"
echo "PATH=$PATH"
echo "XML_CATALOG_FILES=$XML_CATALOG_FILES"
echo "GSETTINGS_SCHEMA_DIR=$GSETTINGS_SCHEMA_DIR"

echo ""
echo ">> Python inside this environment:"
"$ENV_PATH/bin/python" -c "import sys; print(sys.executable)"

echo ""
echo ">> Environment setup complete."