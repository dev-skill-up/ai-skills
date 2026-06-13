#!/usr/bin/env bash
# Download a calm 1920x1080 still image for the meditation backdrop.
#
# Pass your own direct image URL as the 2nd argument once you've picked a scene.
# Good free sources (no API key needed):
#   * Unsplash CDN direct URLs:  https://images.unsplash.com/photo-<id>?w=1920&h=1080&fit=crop&q=80
#   * Picsum (random):           https://picsum.photos/1920/1080
# Prefer a deliberately chosen, low-contrast, slow scene (mist, water, sky,
# forest) over a random image — the backdrop sets the tone before a word is said.
#
# Usage: bash fetch_image.sh [OUT.jpg] [URL]
set -euo pipefail
OUT="${1:-image.jpg}"
URL="${2:-https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=1920&h=1080&fit=crop&q=80}"
wget -q -L "$URL" -O "$OUT"
file "$OUT"
