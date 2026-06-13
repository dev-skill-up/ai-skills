#!/usr/bin/env bash
# Install Kokoro (the ONNX build — NO PyTorch, NO GPU) and fetch the model weights.
#
# Why the ONNX build: the default `kokoro` PyPI package pulls in PyTorch (a ~400MB
# wheel that also takes a long time to unpack). `kokoro-onnx` runs the exact same
# Kokoro v1.0 weights through onnxruntime instead — a few-MB dependency that
# installs in seconds and needs no GPU. Same voice, far lighter footprint.
#
# Usage: bash setup.sh [DEST_DIR]
#   DEST_DIR defaults to the current directory; model files land there.
set -euo pipefail
DEST="${1:-.}"
mkdir -p "$DEST"

echo "Installing kokoro-onnx + onnxruntime + soundfile ..."
# --break-system-packages is needed on Debian/Ubuntu-style PEP668 environments.
pip install --break-system-packages -q kokoro-onnx onnxruntime soundfile

BASE="https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
# -c makes the download resumable if it gets interrupted (large file).
if [ ! -f "$DEST/kokoro-v1.0.onnx" ]; then
  echo "Downloading acoustic model (~310MB) ..."
  wget -q -c "$BASE/kokoro-v1.0.onnx" -O "$DEST/kokoro-v1.0.onnx"
fi
if [ ! -f "$DEST/voices-v1.0.bin" ]; then
  echo "Downloading voices pack (~27MB) ..."
  wget -q -c "$BASE/voices-v1.0.bin" -O "$DEST/voices-v1.0.bin"
fi

python3 - <<'PY'
import onnxruntime, kokoro_onnx
print("kokoro-onnx ready; onnxruntime", onnxruntime.__version__)
PY
echo "Model files in: $DEST"
