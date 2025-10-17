#!/bin/bash
# Build PyInstaller sidecar binary for Python vs_bridge service

set -e  # Exit on error

echo "🔨 Building Python sidecar binary..."

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller not found. Installing..."
    pip install -r vs_bridge/requirements.txt
fi

# Detect platform and set target binary name
PLATFORM=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

case "$PLATFORM" in
    darwin*)
        if [ "$ARCH" = "arm64" ]; then
            TARGET="aarch64-apple-darwin"
        else
            TARGET="x86_64-apple-darwin"
        fi
        BINARY_EXT=""
        ;;
    linux*)
        TARGET="x86_64-unknown-linux-gnu"
        BINARY_EXT=""
        ;;
    msys*|mingw*|cygwin*)
        TARGET="x86_64-pc-windows-msvc"
        BINARY_EXT=".exe"
        ;;
    *)
        echo "❌ Unsupported platform: $PLATFORM"
        exit 1
        ;;
esac

echo "📦 Platform: $PLATFORM ($ARCH)"
echo "🎯 Target: $TARGET"

# Create binaries directory
mkdir -p src-tauri/binaries

# Build with PyInstaller
echo "🔧 Running PyInstaller..."
pyinstaller vs_bridge.spec --distpath dist --workpath build --clean

# Copy binary to Tauri binaries directory with target-specific name
BINARY_NAME="vs-bridge-${TARGET}${BINARY_EXT}"
echo "📂 Copying binary to src-tauri/binaries/${BINARY_NAME}"
cp "dist/vs-bridge${BINARY_EXT}" "src-tauri/binaries/${BINARY_NAME}"

# Make executable (Unix-like systems)
if [ -z "$BINARY_EXT" ]; then
    chmod +x "src-tauri/binaries/${BINARY_NAME}"
fi

echo "✅ Sidecar binary built successfully!"
echo "   Location: src-tauri/binaries/${BINARY_NAME}"

# Test health check (optional)
echo ""
echo "🧪 Testing sidecar health check..."
"src-tauri/binaries/${BINARY_NAME}" &
SIDECAR_PID=$!
sleep 2

if curl -s http://127.0.0.1:8765/api/v1/health | grep -q "ok"; then
    echo "✅ Health check passed!"
else
    echo "⚠️  Health check failed (this may be expected if dependencies are missing)"
fi

# Cleanup
kill $SIDECAR_PID 2>/dev/null || true

echo "🎉 Build complete!"
