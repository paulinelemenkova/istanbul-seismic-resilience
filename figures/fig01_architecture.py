#!/usr/bin/env python3
"""
fig01_architecture.py
Six-layer reference architecture (I -> VI, top to bottom) for an AI + digital-twin
earthquake-resilience system:
  I   Multimodal data acquisition
  II  Data management and preprocessing
  III Multimodal fusion and feature engineering
  IV  AI forecasting and earthquake early warning
  V   City-scale digital twin of Istanbul
  VI  Decision support and smart-city services

Data / control flow runs downward (I -> VI); a feedback / synchronisation loop
runs upward on the right. Outputs vector PDF + 600-dpi PNG. Font: Nimbus Sans.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Nimbus Sans", "Helvetica", "Arial"],
    "mathtext.default": "regular",
    "pdf.fonttype": 42, "ps.fonttype": 42,
})

NAVY, SUB, FLOW, FB, GREYC = "#20344A", "#5A6672", "#33475B", "#A85238", "#6B7280"
# each layer colour = (band fill, stroke/title/box-edge)
BLUE   = ("#E9EEF6", "#2F6BA6")
GREEN  = ("#E7F0E9", "#3C8C5A")
GOLD   = ("#F3ECDA", "#B7861F")
PURPLE = ("#ECE6F4", "#6E4FB0")
TEAL   = ("#E1EFF0", "#2E8385")
RED    = ("#F3E6E1", "#A85238")
DASH   = (0, (5, 3))          # dashed style for the inner sub-blocks
LW     = 1.0                  # all outlines (bands + boxes) = 1.0 pt

# layers ordered I -> VI, top to bottom
layers = [
 dict(num="I", title="MULTIMODAL DATA ACQUISITION", col=BLUE, cap=None,
   boxes=[("Seismic\nwaveforms", None), ("GNSS", None), ("Sentinel-1\nInSAR", None),
          ("Sentinel-2 /\nDEM", None), ("Building and\nlifeline inventory", None),
          ("IoT / SHM\nand traffic", None)]),
 dict(num="II", title="DATA MANAGEMENT AND PREPROCESSING", col=GREEN, cap=None,
   boxes=[("Ingestion\n(stream / batch)", None), ("Denoising and\ncorrection", None),
          ("Standardisation", None), ("Data lake and\nmetadata", None)]),
 dict(num="III", title="MULTIMODAL FUSION AND FEATURE ENGINEERING", col=GOLD, cap=None,
   boxes=[("Quality control", None), ("Spatio-temporal\nalignment", None),
          ("Attention-based\nfusion", None), ("Unified feature space", None)]),
 dict(num="IV", title="AI FORECASTING AND EARTHQUAKE EARLY WARNING", col=PURPLE,
   cap="pre-event forecasting   \u2194   real-time P-wave detection and source estimation",
   weights=[1, 1, 1, 1, 1, 3.0],   # last box widened so its subtitle fits
   boxes=[("CNN", "spatial"), ("LSTM / GRU", "temporal"), ("Transformer", "long-range"),
          ("GNN / GAT", "network"), ("Bayesian NN", "uncertainty"),
          ("Ensemble forecast + EEW outputs",
           "occurrence prob., Mw, PGA/MMI, lead time, confidence")]),
 dict(num="V", title="CITY-SCALE DIGITAL TWIN OF ISTANBUL", col=TEAL,
   cap="spatial + time-series data lake   (PostGIS / InfluxDB / object store)",
   boxes=[("GIS / 3D city model", "buildings, terrain"),
          ("Physical-asset layer", "lifelines, hospitals"),
          ("Dynamic state layer", "sensor streams"),
          ("Simulation engine", "damage, cascades"),
          ("Assimilation and\nsynchronisation", "state update")]),
 dict(num="VI", title="DECISION SUPPORT AND SMART-CITY SERVICES", col=RED, cap=None,
   boxes=[("Early warning\ndissemination", "alerts, lead time"),
          ("Situational\nawareness", "dashboards, 2D/3D"),
          ("Evacuation and\nlogistics", "routing, shelters"),
          ("Infrastructure\nprioritisation", "inspection ranking"),
          ("Public and\nagency APIs", "OGC, REST")]),
]

# per-layer geometry: (band_top, band_bottom, title_y, box_cy, box_h, caption_y)
geom = {
 "I":   (95.0, 82.5, 93.1, 87.0, 7.6, None),
 "II":  (79.8, 68.3, 78.1, 73.2, 7.2, None),
 "III": (65.6, 54.1, 63.9, 59.0, 7.2, None),
 "IV":  (51.4, 35.0, 49.7, 43.4, 8.2, 36.4),
 "V":   (32.3, 16.5, 30.6, 24.6, 8.0, 17.6),
 "VI":  (13.8,  2.6, 12.1,  6.9, 7.6, None),
}
BX0, BX1, GAP = 4.0, 93.0, 1.8
FS = dict(band=11.0, btitle=10.5, sub=9.2, cap=10.5, leg=10.5, cross=10.5, fb=9.5)

fig, ax = plt.subplots(figsize=(14, 8.7))
ax.set_xlim(0, 101)
ax.set_ylim(0, 100)
ax.axis("off")


def place(weights):
    n = len(weights)
    avail = (BX1 - BX0) - (n - 1) * GAP
    unit = avail / sum(weights)
    out, cur = [], BX0
    for w in weights:
        ww = unit * w
        out.append((cur + ww / 2, ww))
        cur += ww + GAP
    return out


def draw_box(cx, cy, w, h, edge, title, sub):
    # inner sub-blocks: dashed outline, 1.0 pt
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                 boxstyle="round,pad=0,rounding_size=1.0",
                 fc="white", ec=edge, lw=LW, ls=DASH, zorder=4))
    if sub:
        ax.text(cx, cy + h * 0.15, title, ha="center", va="center",
                fontsize=FS["btitle"], fontweight="bold", color=NAVY, zorder=5, linespacing=1.05)
        ax.text(cx, cy - h * 0.24, sub, ha="center", va="center",
                fontsize=FS["sub"], color=SUB, zorder=5, linespacing=1.0)
    else:
        ax.text(cx, cy, title, ha="center", va="center",
                fontsize=FS["btitle"], fontweight="bold", color=NAVY, zorder=5, linespacing=1.05)


for L in layers:
    top, bot, ty, bcy, bh, capy = geom[L["num"]]
    fill, stroke = L["col"]
    ax.add_patch(FancyBboxPatch((2, bot), 93, top - bot,
                 boxstyle="round,pad=0,rounding_size=1.4", fc=fill, ec=stroke, lw=LW, zorder=1))
    # band title: plain (non-bold), reduced size
    ax.text(4.2, ty, f'{L["num"]}   {L["title"]}', ha="left", va="center",
            fontsize=FS["band"], color=stroke, zorder=3)
    weights = L.get("weights", [1] * len(L["boxes"]))
    for (cx, cw), (t, s) in zip(place(weights), L["boxes"]):
        draw_box(cx, bcy, cw, bh, stroke, t, s)
    if L["cap"]:
        ax.text(47.5, capy, L["cap"], ha="center", va="center",
                fontsize=FS["cap"], style="italic", color=SUB, zorder=3)

# downward inter-layer arrows: data / control flow  (I -> VI)
order = ["I", "II", "III", "IV", "V", "VI"]
for a, b in zip(order[:-1], order[1:]):
    ya, yb = geom[a][1], geom[b][0]
    for x in (24, 49, 74):
        ax.add_patch(FancyArrowPatch((x, ya), (x, yb), arrowstyle="-|>",
                     mutation_scale=13, lw=1.8, color=FLOW, shrinkA=0, shrinkB=0, zorder=2))

# feedback / synchronisation loop (right), running upward to layer I
ax.add_patch(FancyArrowPatch((97, 3.0), (97, 94.0), arrowstyle="-|>",
             mutation_scale=13, lw=1.7, ls=(0, (6, 4)), color=FB, shrinkA=0, shrinkB=0, zorder=2))
ax.text(98.7, 48, "feedback, continuous learning and twin synchronisation",
        ha="center", va="center", rotation=90, fontsize=FS["fb"], color=FB)

# top legend
ax.plot([3, 6.5], [97.6, 97.6], color=FLOW, lw=2.0, zorder=3)
ax.text(7.2, 97.6, "data / control flow (downward)", ha="left", va="center", fontsize=FS["leg"], color="#333")
ax.plot([34, 37.5], [97.6, 97.6], color=FB, lw=2.0, ls=(0, (6, 4)), zorder=3)
ax.text(38.2, 97.6, "feedback and synchronisation", ha="left", va="center", fontsize=FS["leg"], color="#333")

# cross-cutting footer
ax.text(48.5, 0.9,
        "Cross-cutting: cloud/edge computing  |  5G/6G  |  cybersecurity and privacy  |  "
        "interoperability (OGC/FDSN)  |  explainable AI",
        ha="center", va="center", fontsize=FS["cross"], color=GREYC)

fig.savefig("fig01_architecture.pdf", bbox_inches="tight", pad_inches=0.05)
fig.savefig("fig01_architecture.png", dpi=600, bbox_inches="tight", pad_inches=0.05)
print("wrote fig01_architecture.pdf / .png")
