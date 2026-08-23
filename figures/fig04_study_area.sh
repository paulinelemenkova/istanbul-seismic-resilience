#!/usr/bin/env bash
# ============================================================================
# fig04_study_area — Istanbul & the Sea of Marmara study-area map (GMT 6, shell)
#
# Shaded-relief basemap: topo15 bathymetry in the sea + a fine land DEM on land,
# with the North Anatolian Fault, cities, a Turkiye locator inset and a NAF-system
# tectonic inset, plus scale / north arrow / graticule / elevation colour bar.
#
#   Backend  : GMT 6 modern mode            run:  bash plot_study_area.sh
#   Sea/base : /Volumes/TOSHIBA/DATA/topo15.grd  (SRTM15+ / Tozer "topo_15")
#   Land     : fine DEM overlaid on land (default @earth_relief_03s ~90 m)
#   Coast    : GSHHG full resolution (-Df), shipped with GMT
#   Palette  : terra (hard-hinged at 0 m)
#   Output   : fig04_study_area.pdf (vector) + .png (300 dpi), auto-cropped
#
# NOTES
#  * The land DEM is overlaid as a SAFE layer: if it can't be fetched/read the
#    script warns and falls back to topo15 land, so the map ALWAYS renders.
#  * @earth_relief_01s (~30 m) is finer but its tiles are not hosted for every
#    1x1 cell (that's the "does not exist on the remote server" error) — so the
#    default is @earth_relief_03s (~90 m), which is reliably available. For the
#    best land relief, download a Copernicus GLO-30 or FABDEM grid once and point
#    LAND_DEM at it (a local file never depends on the GMT data server).
#  * Turkish glyphs: GMT's PostScript fonts can't encode Ist/Sile/Buyukcekmece's
#    special letters, so place names are ASCII. (PyGMT + a Unicode font can do
#    proper Turkish — ask if you want that port.)
#  * The NAF trace (naf.txt) is APPROXIMATE. Replace with Emre et al. (2018) /
#    EMME / GEM Global Active Faults before publishing.
# ============================================================================
set -e

# ---------------------------------------------------------------- CONFIG -----
DATA_ROOT="${DATA_ROOT:-$HOME/DATA}"
TOPO="$DATA_ROOT/topo15.grd"                       # SRTM15+ (sea + fallback land)
REGION="-R28.35/30.55/40.55/41.35"                # W/E/S/N (Istanbul + Marmara)
PROJ="-JM17c"                                      # Mercator, 17 cm wide
OUT="fig04_study_area"
CLIM="-1500/1500"                                  # colour range (m), hinged at 0
CPT="terra"                                        # topo-bathy master CPT
SEA_SMOOTH_KM=5                                    # Gaussian smooth (km) on topo15 bathy
                                                   # before upsampling (kills dimples; 0=off)

# Fine LAND DEM overlaid on land. Default = your local Copernicus GLO-30 (~30 m).
#   Local COP30/FABDEM (best, no server): LAND_DEM="$DATA_ROOT/COP30_marmara.tif"
#   Reliable remote fallback (~90 m):     LAND_DEM="@earth_relief_03s"
#   Disable (topo15 land only):           LAND_DEM=""
LAND_DEM="$DATA_ROOT/COP30_marmara.tif"

# OPTIONAL open-data overlays — plotted only if the file exists ---------------
ADM1="$DATA_ROOT/geoBoundaries-TUR-ADM1.geojson"   # province boundaries
ADM2="$DATA_ROOT/geoBoundaries-TUR-ADM2.geojson"   # district boundaries
ROADS_GEOJSON="$DATA_ROOT/osm_marmara_transport.geojson"  # OSM lines (optional)

# ---------------------------------------------------------------- DATA -------
rm -f relief.nc int.nc cop.nc cop0.nc bath_fine.nc mask.nc relief_sm.nc

# base grid = topo15 (bathymetry + fallback land)
gmt grdcut "$TOPO" $REGION -Grelief.nc

# merge a fine land DEM INTO one grid (land from the DEM, sea from topo15), then
# hillshade + draw it in a single grdimage. This avoids grdimage -Q (NaN
# transparency), which some GMT builds refuse to combine with -I intensities.
USE_BLEND=0
if [ -n "$LAND_DEM" ]; then
  case "$LAND_DEM" in
    @*) : ;;                                        # remote GMT grid (auto-download)
    *) [ -f "$LAND_DEM" ] || { echo "! LAND_DEM not found: $LAND_DEM (using topo15 land)"; LAND_DEM=""; } ;;
  esac
fi
if [ -n "$LAND_DEM" ] && gmt grdcut "$LAND_DEM" $REGION -Gcop.nc 2>/dev/null && gmt grdinfo cop.nc >/dev/null 2>&1; then
  gmt grdmath cop.nc 0 AND = cop0.nc                 # land DEM: NaN -> 0
  if [ "${SEA_SMOOTH_KM:-0}" != 0 ]; then
    gmt grdfilter relief.nc -Fg${SEA_SMOOTH_KM} -D4 -Grelief_sm.nc  # smooth 15" sea
  else
    cp relief.nc relief_sm.nc
  fi
  gmt grdsample relief_sm.nc -Rcop0.nc -Gbath_fine.nc  # (smoothed) topo15 bathymetry on the fine grid
  gmt grdmath cop0.nc 0 GT = mask.nc                 # 1 on land (>0 m), 0 on sea
  gmt grdmath mask.nc cop0.nc MUL  1 mask.nc SUB bath_fine.nc MUL  ADD = relief.nc
  USE_BLEND=1
else
  [ -n "$LAND_DEM" ] && echo "! could not read $LAND_DEM — using topo15 land relief"
fi

# hillshade on the (possibly merged) grid
gmt grdgradient relief.nc -A315 -Nt1.1 -Gint.nc

# North Anatolian Fault — APPROXIMATE Main Marmara branch (lon lat) -----------
cat > naf.txt <<'EOF'
28.35 40.86
28.55 40.84
28.80 40.82
29.05 40.81
29.25 40.80
29.45 40.77
29.65 40.74
29.85 40.75
30.05 40.76
30.25 40.77
30.45 40.78
EOF

# cities — dots (lon lat); labels handled per-city below ----------------------
cat > cities.txt <<'EOF'
28.98 41.03
28.46 41.14
28.59 41.02
29.61 41.18
29.43 40.80
29.92 40.77
30.42 40.78
29.28 40.66
EOF
# labels that sit to the RIGHT of the dot
cat > cities_L.txt <<'EOF'
28.98 41.03 Istanbul
29.61 41.18 Sile
29.43 40.80 Gebze
29.92 40.77 Izmit
29.28 40.66 Yalova
EOF

# ---------------------------------------------------------------- PLOT -------
gmt begin "$OUT" pdf,png
  gmt set MAP_FRAME_TYPE plain FONT_ANNOT_PRIMARY 9p,Helvetica FONT_LABEL 9p,Helvetica \
          FONT_TITLE 13p,Helvetica-Bold MAP_GRID_PEN_PRIMARY 0.25p,white \
          MAP_TICK_LENGTH_PRIMARY 4p

  gmt makecpt -C${CPT} -T${CLIM}/10 -Z -H > topo.cpt

  # 1. basemap: merged relief (COP30 land + topo15 bathymetry) + white graticule
  gmt grdimage relief.nc -Iint.nc -Ctopo.cpt $PROJ $REGION \
      -BWSne+t"Study area @~\055@~ Istanbul and the Sea of Marmara, North Anatolian Fault" \
      -Bxa0.5f0.25g0.5 -Bya0.25f0.125g0.25

  # 2. full-resolution coastline (+ light province borders from DCW)
  gmt coast -Df -W0.6p,50/50/50 -N2/0.4p,110/110/110

  # 2b. OPTIONAL open-data overlays. GMT truncates long GeoJSON text records at
  #     4094 bytes (mangling big polygons), so convert to OGR_GMT first if
  #     ogr2ogr is available; otherwise fall back to the raw file.
  for spec in "$ADM2|0.25p,150/150/150" "$ADM1|0.5p,90/90/90" "$ROADS_GEOJSON|0.8p,230/120/30"; do
    f="${spec%%|*}"; pen="${spec##*|}"
    [ -f "$f" ] || continue
    g="${f%.*}.gmt"
    [ -f "$g" ] || ogr2ogr -f OGR_GMT "$g" "$f" 2>/dev/null || g="$f"
    gmt plot "$g" -W"$pen"
  done

  # 3. North Anatolian Fault (line + fault ticks + label)
  gmt plot naf.txt -W2p,200/30/30
  gmt plot naf.txt -Sf1c/0.12c+r+t -W1p,200/30/30 -G200/30/30
  echo "28.95 40.815 North Anatolian Fault" | \
      gmt text -F+f8.5p,Helvetica-BoldOblique,lavenderblush+a-5+jLM

  # 4. cities (right-labelled group + three special placements)
  gmt plot cities.txt -Sc0.16c -Gblack -W0.6p,white
  gmt text cities_L.txt -F+f8.5p,Helvetica-Bold,black+jLM -D0.18c/0.12c -Gwhite@25 -C0.05c/0.03c
  echo "30.42 40.78 Adapazari"     | gmt text -F+f8.5p,Helvetica-Bold,black+jRM -D-0.18c/0.12c -Gwhite@25 -C0.05c/0.03c
  echo "28.66 41.055 Buyukcekmece" | gmt text -F+f8p,Helvetica-Bold,black+jBC -Gwhite@25 -C0.05c/0.03c
  echo "28.46 41.135 Catalca"      | gmt text -F+f8.5p,Helvetica-Bold,black+jTC -D0/-0.16c -Gwhite@25 -C0.05c/0.03c

  # 5. sea + European/Asian-side labels
  echo "28.95 40.60 Sea of Marmara" | gmt text -F+f10p,Helvetica-Oblique,20/64/110+jCM
  echo "29.10 41.31 Black Sea"      | gmt text -F+f10p,Helvetica-Oblique,20/64/110+jCM
  echo "28.52 40.90 European Side"  | gmt text -F+f9p,Helvetica-Bold,200/30/30+jCM
  echo "29.55 41.25 Asian Side"     | gmt text -F+f9p,Helvetica-Bold,200/30/30+jCM

  # 6. furniture: north arrow, scale, elevation colour bar
  gmt basemap -TdjBR+w1.1c+f2+l,,,N+o0.3c/0.3c
  gmt basemap -LjBL+w25k+o0.6c/0.6c+f+u+c40.9
  gmt colorbar -Ctopo.cpt -DJBC+w11c/0.35c+o0c/1.3c+h \
      -Bxa500f250+l"Elevation / bathymetry" -By+lm

  # 7. inset A — Turkiye locator (height set to Mercator aspect -> no white space)
  gmt inset begin -DjTL+w3.9c/1.9c+o0.15c -F+p0.8p+gwhite
    gmt coast -R25.5/45/35.5/42.6 -JM3.9c -Ggray85 -S219/231/240 -Di \
              -W0.2p,gray40 -N1/0.4p,gray55
    printf "28.35 40.55\n30.55 40.55\n30.55 41.35\n28.35 41.35\n28.35 40.55\n" | \
        gmt plot -W1.1p,200/30/30
    echo "35 41.6 TURKIYE" | gmt text -F+f5.5p,Helvetica-Bold,gray30+jCM
  gmt inset end

  # 8. inset B — North Anatolian Fault system (plates + main strand)
  gmt inset begin -DjTR+w4.4c/1.8c+o0.15c -F+p0.8p+gwhite
    gmt coast -R26/42/38/43 -JM4.4c -Ggray88 -S219/231/240 -Di -W0.2p,gray50
    printf "26.3 40.4\n27.6 40.7\n29.0 40.8\n30.5 40.7\n31.6 40.9\n33.2 41.0\n35.2 40.9\n37.2 40.7\n39.2 40.5\n40.8 40.3\n" | \
        gmt plot -W1.5p,200/30/30
    echo "33 42.55 EURASIAN PLATE" | gmt text -F+f5.5p,Helvetica-Bold,gray30+jCM
    echo "33 38.6 ANATOLIAN PLATE" | gmt text -F+f5.5p,Helvetica-Bold,gray30+jCM
    echo "30.6 41.35 NAF"          | gmt text -F+f6p,Helvetica-Bold,200/30/30+jCM
    printf "28.98 41.02\n32.85 39.93\n" | gmt plot -Sc0.1c -Gblack
    echo "28.98 41.6 Istanbul" | gmt text -F+f5p,Helvetica,black+jCM
    echo "32.85 39.5 Ankara"   | gmt text -F+f5p,Helvetica,black+jCM
  gmt inset end
gmt end show

echo "wrote ${OUT}.pdf and ${OUT}.png  (USE_BLEND=$USE_BLEND)"
