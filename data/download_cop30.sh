#!/usr/bin/env bash
# Download the Copernicus GLO-30 (COP30) land DEM for the extended Marmara window
# from the OpenTopography API. Insert your free API key (portal.opentopography.org).
set -euo pipefail
OUT="${1:-${DATA_ROOT:-$HOME/DATA}/TURKEY/COP30_marmara_ext.tif}"
API_KEY="${OPENTOPO_API_KEY:-YOUR_KEY}"
mkdir -p "$(dirname "$OUT")"
curl -o "$OUT" \
  "https://portal.opentopography.org/API/globaldem?demtype=COP30&south=39.8&north=41.8&west=25.5&east=31.5&outputFormat=GTiff&API_Key=${API_KEY}"
echo "Saved $OUT"
