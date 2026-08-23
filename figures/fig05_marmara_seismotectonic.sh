#!/usr/bin/env bash
# =============================================================================
# Fig. 5  —  Seismotectonic study-area map of the Marmara region & Istanbul
# GMT 6 (modern mode).  Validated on GMT 6.6.0.
#
# Relief : COP30 land topography (OpenTopography) OVER GEBCO_2026 bathymetry,
#          split by a coastline clip so the sea always shows GEBCO.
# Quakes : IEB catalogue circles  — SIZE = magnitude, COLOUR = depth.
# Mechan.: beachballs for several key large events — SIZE = magnitude,
#          COLOUR = one distinct colour per event (labelled on the map).
#
# ---------------------------------------------------------------------------
# GET THE EXTENDED LAND DEM (once):  OpenTopography Copernicus GLO-30, covering
# the extended region below (~113,000 km^2, well under the 450,000 km^2 limit).
#   1) Free API key: portal.opentopography.org  ->  My Account  ->  request key
#   2) Download (paste your key):
#      curl -o /Volumes/TOSHIBA/DATA/TURKEY/COP30_marmara_ext.tif \
#        "https://portal.opentopography.org/API/globaldem?demtype=COP30\
# &south=39.8&north=41.8&west=25.5&east=31.5&outputFormat=GTiff&API_Key=YOUR_KEY"
#   (Web alternative: portal.opentopography.org -> Find Data -> Global -> COP30
#    -> draw the box 25.5/31.5/39.8/41.8 -> GeoTIFF. Use COP90 for a lighter/faster file.)
# =============================================================================
set -e

# ------------------------------------------------------------------ TUNE HERE
DATA="${DATA_ROOT:-$HOME/DATA}"
COP=$DATA/TURKEY/COP30_marmara_ext.tif       # extended land DEM (see header)
GEB=$DATA/GEBCO_2026.nc                        # global bathymetry grid
CAT=$DATA/TURKEY/IEB_3000_Marmara.csv          # earthquake catalogue
CMT=marmara_cmt.txt                            # focal mechanisms (auto-created)
OUT=fig05_study_area
REG=-R25.5/31.5/39.8/41.8                       # extended W/E/S/N
J=-JM26c
RELIEF_CPT=terra                                # terra relief master (violet-blue sea, green/tan land)
BALL=0.4c                                        # beachball reference size (smaller = smaller balls)
# ----------------------------------------------------------------------------

gmt set FONT_TITLE=15p,Helvetica FONT_ANNOT_PRIMARY=9p FONT_LABEL=10p \
        MAP_FRAME_TYPE=plain MAP_GRID_PEN_PRIMARY=0.25p,white
# If GMT cannot read the GeoTIFF directly, convert once:
# gmt grdconvert "$COP" cop30.nc && COP=cop30.nc

# 1) catalogue -> plot table: lon lat depth size(cm)  (size grows with Mag)
awk -F, 'NR>1 && $8!="" {sub(/\r/,"");
         printf "%.4f %.4f %.2f %.4f\n", $6,$5,$7, 0.020*1.7^$8}' "$CAT" > eq_plot.txt

# 2) focal mechanisms of KEY LARGE EVENTS
#    columns:  lon lat depth strike dip rake mag  colour  label
#    Aki convention (strike/dip/rake), plotted with -Sa.
#    S/D/R for 1999 Izmit & Duzce are Global CMT (reliable); the older/smaller
#    events are literature estimates -> VERIFY at globalcmt.org before submission.
if [ ! -f "$CMT" ]; then
cat > "$CMT" <<'EOF'
# lon    lat    dep strike dip rake  mag  colour      label
29.86  40.75  17   91   87  -172  7.6  #d7191c  1999_Izmit
31.16  40.74  10  262   64  -172  7.1  #f07d00  1999_Duzce
28.23  40.30  10  250   45   -85  6.9  #1a9850  1964_Manyas
26.11  40.45  10   68   82  -175  6.6  #2c7bb6  1975_Saros
28.16  40.88  12  269   65  -173  5.8  #7b3294  2019_Silivri
EOF
fi

# 3) ------------------------------------------------------------- draw the map
gmt begin "$OUT" png,pdf E600
  gmt makecpt -C$RELIEF_CPT -T-2500/1500 -H > relief.cpt

  # crop the GLOBAL GEBCO grid to the region FIRST (fast), then shade
  gmt grdcut "$GEB" $REG -Ggeb_cut.nc
  gmt grdgradient geb_cut.nc -A315 -Nt0.8 -Ggeb_grad.nc
  gmt grdgradient "$COP"     -A315 -Nt0.8 -Gcop_grad.nc

  gmt grdimage geb_cut.nc $REG $J -Crelief.cpt -Igeb_grad.nc    # bathymetry
  gmt coast -Gc -Dh                                            # land clip
    gmt grdimage "$COP" -Crelief.cpt -Icop_grad.nc             # COP30 land on top
  gmt coast -Q
  gmt coast -Dh -Wthin,black -N1/0.5p,gray40                   # coast + borders

  # seismicity: circles (size = magnitude, colour = depth)
  gmt makecpt -Cseis -T0/50 -H > depth.cpt
  gmt plot eq_plot.txt -Sc -Cdepth.cpt -W0.2p,gray25 -t20

  # beachballs: one meca call per event -> distinct colour + label above it
  while read lon lat dep s d r m col lab; do
    case "$lon" in ''|\#*) continue;; esac
    echo "$lon $lat $dep $s $d $r $m" | gmt meca -Sa$BALL -G$col -W0.5p,black -L0.5p,black
    echo "$lon $lat ${lab//_/ }"      | gmt text -F+f6p,Helvetica-Bold,black+jCB -D0/0.3c -Gwhite@40 -N
  done < "$CMT"

  # place-name labels
  gmt text -F+f9p,Helvetica-Bold,black+jLM -Dj0.15c <<'EOF'
28.98 41.05 Istanbul
EOF
  echo "28.00 40.66 Sea of Marmara" | gmt text -F+f12p,Helvetica-BoldOblique,navy+jCM -Gwhite@30 -W0.25p,gray70 -N

  # frame + white graticule + title (small, non-bold) and scale bar
  gmt basemap -Bafg -BWSne+t"Seismotectonic setting of the Marmara region and Istanbul" \
              -LjBR+w100k+f+u+o0.6c/0.6c

  # elevation bar right; depth bar (LEFT) + magnitude legend (RIGHT) on one level below map
  gmt colorbar -Crelief.cpt -DJMR+w6c/0.35c+o0.25c/0c+v -Bxa1000+l"Elevation (m)"
  gmt colorbar -Cdepth.cpt  -DjBC+w10c/0.4c+o-7c/-1.8c+h -Bxa10f5+l"Hypocentre depth (km)"
  gmt legend -DjBC+w6.5c+o7c/-1.8c -F+gwhite@10+p0.5p,gray40 <<'EOF'
N 3
S 0.2c c 0.16c white 0.2p,gray25 0.5c M 3
S 0.2c c 0.29c white 0.2p,gray25 0.5c M 5
S 0.2c c 0.49c white 0.2p,gray25 0.5c M 7
EOF

  gmt text -N -D0/0.4c -F+cTC+f7p,gray30+t"Relief: Copernicus GLO-30 (land) + GEBCO 2026 (bathymetry).  Seismicity: IEB.  Mechanisms: Global CMT / literature."
gmt end
echo "Done -> ${OUT}.png  ${OUT}.pdf"
