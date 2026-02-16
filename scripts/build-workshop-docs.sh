#!/bin/bash
#
# Build workshop documentation using Antora
# Outputs to ./www/ directory
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "Building workshop documentation..."

# Check if podman is available
if ! command -v podman &> /dev/null; then
    echo "Error: podman is required but not installed"
    exit 1
fi

# Change to project root
cd "${PROJECT_ROOT}"

# Verify default-site.yml exists
if [ ! -f "default-site.yml" ]; then
    echo "Error: default-site.yml not found in ${PROJECT_ROOT}"
    exit 1
fi

# Build documentation using official Antora container
echo "Running Antora build..."
podman run --rm \
  -v "${PROJECT_ROOT}:/antora:z" \
  docker.io/antora/antora:3.1.14 \
  default-site.yml

# Verify build output
if [ ! -d "www" ] || [ ! -f "www/index.html" ]; then
    echo "Error: Build failed - www/index.html not found"
    exit 1
fi

echo "Build complete!"
echo "Output directory: ${PROJECT_ROOT}/www"
echo ""
echo "To deploy the documentation:"
echo "  ./scripts/deploy-workshop-docs.sh"
