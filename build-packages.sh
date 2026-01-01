#!/bin/bash
# Build script for MSR605X Utility packages
# Run this script on Ubuntu to build .deb and/or .snap packages

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_help() {
    echo "MSR605X Utility Package Builder"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --deb         Build Debian package (.deb)"
    echo "  --snap        Build Snap package (.snap)"
    echo "  --all         Build all package formats"
    echo "  --clean       Clean build artifacts"
    echo "  --help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --deb      # Build only .deb package"
    echo "  $0 --snap     # Build only .snap package"
    echo "  $0 --all      # Build all packages"
}

install_deb_deps() {
    print_info "Installing Debian build dependencies..."
    sudo apt-get update
    sudo apt-get install -y \
        build-essential \
        debhelper \
        dh-python \
        python3-all \
        python3-setuptools \
        python3-gi \
        python3-hid \
        devscripts \
        fakeroot
}

install_snap_deps() {
    print_info "Installing Snap build dependencies..."
    sudo apt-get update
    sudo apt-get install -y snapcraft
}

build_deb() {
    print_info "Building Debian package..."

    # Check dependencies
    if ! command -v dpkg-buildpackage &> /dev/null; then
        print_warn "dpkg-buildpackage not found. Installing dependencies..."
        install_deb_deps
    fi

    # Clean previous builds
    rm -rf debian/.debhelper debian/msr605x-utility debian/files debian/*.debhelper* debian/*.substvars
    rm -f ../msr605x-utility_*.deb ../msr605x-utility_*.buildinfo ../msr605x-utility_*.changes

    # Build the package
    dpkg-buildpackage -us -uc -b

    # Move package to dist folder
    mkdir -p dist
    mv ../msr605x-utility_*.deb dist/ 2>/dev/null || true

    print_info "Debian package built successfully!"
    print_info "Package location: dist/"
    ls -la dist/*.deb 2>/dev/null || print_warn "No .deb files found in dist/"
}

build_snap() {
    print_info "Building Snap package..."

    # Check dependencies
    if ! command -v snapcraft &> /dev/null; then
        print_warn "snapcraft not found. Installing dependencies..."
        install_snap_deps
    fi

    # Clean previous builds
    snapcraft clean 2>/dev/null || true

    # Build the snap
    snapcraft

    # Move to dist folder
    mkdir -p dist
    mv *.snap dist/ 2>/dev/null || true

    print_info "Snap package built successfully!"
    print_info "Package location: dist/"
    ls -la dist/*.snap 2>/dev/null || print_warn "No .snap files found in dist/"
}

clean_build() {
    print_info "Cleaning build artifacts..."

    # Clean Debian build
    rm -rf debian/.debhelper debian/msr605x-utility debian/files
    rm -f debian/*.debhelper* debian/*.substvars
    rm -f ../msr605x-utility_*.deb ../msr605x-utility_*.buildinfo ../msr605x-utility_*.changes

    # Clean Snap build
    snapcraft clean 2>/dev/null || true
    rm -rf parts prime stage *.snap

    # Clean Python build
    rm -rf build dist *.egg-info
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true

    print_info "Build artifacts cleaned."
}

# Parse arguments
BUILD_DEB=false
BUILD_SNAP=false

if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        --deb)
            BUILD_DEB=true
            shift
            ;;
        --snap)
            BUILD_SNAP=true
            shift
            ;;
        --all)
            BUILD_DEB=true
            BUILD_SNAP=true
            shift
            ;;
        --clean)
            clean_build
            exit 0
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_error "This script must be run on Linux (Ubuntu)"
    exit 1
fi

# Build packages
if $BUILD_DEB; then
    build_deb
fi

if $BUILD_SNAP; then
    build_snap
fi

echo ""
print_info "Build complete!"
echo ""
echo "To install the .deb package:"
echo "  sudo dpkg -i dist/msr605x-utility_*.deb"
echo "  sudo apt-get install -f  # Fix dependencies if needed"
echo ""
echo "To install the .snap package:"
echo "  sudo snap install dist/*.snap --dangerous"
echo "  sudo snap connect msr605x-utility:raw-usb"
echo ""
