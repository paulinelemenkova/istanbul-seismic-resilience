#!/usr/bin/env python3
"""
fig03_eew_digital_twin.py
Single dense architecture figure for an Istanbul seismic-resilience paper:
three swim-lanes (physical sensing -> real-time early warning -> city digital
twin) sharing one telemetry bus, with the EEW<->twin couplings and a feedback
loop drawn explicitly.

Style: all solid strokes 1.0 pt, all dashed strokes 0.8 pt; lane headers set at
the top of each band in plain (non-bold) type; EEW<->twin coupling labels drawn
horizontally to the left of their arrows. Outputs vector PDF + 600-dpi PNG.
Font: Nimbus Sans / Helvetica / Arial.

NOTE: node labels use standard EEW + digital-twin terminology; swap them for the
exact wording of your original figures where they differ.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.transforms as mtr
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.path import Path

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Nimbus Sans", "Helvetica", "Arial"],
    "mathtext.default": "regular",
    "pdf.fonttype": 42, "ps.fonttype": 42,
})

EEW  = dict(dark="#D55E00", fill="#FBEAE0", edge="#D55E00", txt="#7A3500")
TWIN = dict(dark="#009E73", fill="#E4F3EC", edge="#009E73", txt="#04503B")
PHYS = dict(dark="#0072B2", fill="#E4EFF7", edge="#0072B2", txt="#083A57")
BUS  = dict(fill="#D9DEE3", edge="#5B6670", txt="#2A2F35")
CHIP = dict(fill="#EFF5FA", edge="#0072B2", txt="#083A57")
CROSS, FEED, LOOP = "#333333", "#1F3B63", "#CC79A7"

SOLID_LW, DASH_LW = 1.0, 0.8          # all solid lines 1.0 pt, all dashed lines 0.8 pt
LANE_TITLE_FS = 8.4

fig, ax = plt.subplots(figsize=(8.5, 6.0))
ax.set_xlim(-5.5, 111)
ax.set_ylim(-7.0, 100)
ax.axis("off")


def band(x0, x1, y0, y1, s):
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0,
                 boxstyle="round,pad=0,rounding_size=1.8",
                 fc=s["fill"], ec=s["edge"], lw=SOLID_LW, alpha=0.9, zorder=1))


def box(cx, cy, w, h, s, text, fs=7.4, z=3):
    # inner sub-blocks: dashed outline at 0.8 pt
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                 boxstyle="round,pad=0,rounding_size=1.1",
                 fc=s["fill"], ec=s["edge"], lw=DASH_LW, ls="--", zorder=z))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs,
            color=s["txt"], zorder=z + 1, linespacing=1.15)
    return dict(top=cy + h / 2, bot=cy - h / 2, l=cx - w / 2, r=cx + w / 2)


def straight(p0, p1, c, lw=SOLID_LW, ls="-", head=12, z=4):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=head,
                 lw=lw, ls=ls, color=c, shrinkA=0, shrinkB=0,
                 connectionstyle="arc3,rad=0", zorder=z))


def elbow(verts, c, lw=SOLID_LW, z=4, head=12):
    codes = [Path.MOVETO] + [Path.LINETO] * (len(verts) - 1)
    ax.add_patch(FancyArrowPatch(path=Path(verts, codes), arrowstyle="-|>",
                 mutation_scale=head, lw=lw, color=c, shrinkA=0, shrinkB=0, zorder=z))


XC = [13.5, 32.25, 51.0, 69.75, 88.5]
WB, HB = 16, 16

# -- lane backgrounds + headers (all titles plain, not bold) ------------------
band(3, 97, 61, 87, TWIN)
band(3, 97, 29, 55, EEW)
band(3, 97, 3, 22.5, PHYS)
ax.text(5, 84.4, "DIGITAL TWIN", ha="left", va="center",
        fontsize=LANE_TITLE_FS, color=TWIN["dark"])
ax.text(19, 84.4, "· city-scale analytics & decision support  (minutes \u2013 days)",
        ha="left", va="center", fontsize=8.2, color=TWIN["txt"])
ax.text(5, 52.4, "EARLY WARNING", ha="left", va="center",
        fontsize=LANE_TITLE_FS, color=EEW["dark"])

# -- digital-twin row ---------------------------------------------------------
dt = ["Data assimilation\n& monitoring\n(SHM)",
      "City model\ninventory · geotech\nsite response",
      "Physics + ML\nsimulation &\nscenario engine",
      "Damage & loss\nfragility · exposure",
      "Decision support\nresponse · recovery\n· planning"]
DT = [box(XC[i], 72, WB, HB, TWIN, dt[i]) for i in range(5)]
for i in range(4):
    straight((DT[i]["r"], 72), (DT[i + 1]["l"], 72), TWIN["dark"])

# -- early-warning row --------------------------------------------------------
ew = ["P-wave detection\n& phase picking",
      "Source estimation\nlocation & mag.",
      "Ground-motion\nprediction\n(ShakeMap)",
      "Alert decision\nwarning / lead time",
      "Dissemination &\nauto. response\napps · metro · gas"]
EW = [box(XC[i], 40, WB, HB, EEW, ew[i]) for i in range(5)]
for i in range(4):
    straight((EW[i]["r"], 40), (EW[i + 1]["l"], 40), EEW["dark"])

# -- shared telemetry bus -----------------------------------------------------
ax.add_patch(FancyBboxPatch((5, 24.2), 90, 4.0,
             boxstyle="round,pad=0,rounding_size=1.0",
             fc=BUS["fill"], ec=BUS["edge"], lw=SOLID_LW, zorder=2))
ax.text(50, 26.2, "Real-time data acquisition & telemetry   "
        "(seismic · GNSS · MEMS/IoT · SHM streams)",
        ha="center", va="center", fontsize=8.8, color=BUS["txt"], zorder=3)

# -- physical layer: source block + sensor chips (header at bottom) -----------
box(15.5, 11.5, 21, 9.0, PHYS,
    "Istanbul metropolitan area\n& Main Marmara Fault\n(Mw \u2248 7+ seismic gap)", fs=7.0)
chips = ["Seismic BB +\nstrong-motion", "GNSS", "MEMS / IoT\naccelerometers",
         "Structural\nhealth monitoring", "Geotechnical\narrays"]
cxc = [34.8, 48.65, 62.5, 76.35, 90.2]                 # wider spacing, no text overlap
for c, x in zip(chips, cxc):
    box(x, 11.5, 12.6, 9.0, CHIP, c, fs=6.9)
for x in [15.5] + cxc:
    straight((x, 16.2), (x, 24.1), FEED, head=9)
ax.text(50, 4.7, "PHYSICAL CITY & SENSING   ·   Istanbul · Main Marmara Fault seismic gap",
        ha="center", va="center", fontsize=LANE_TITLE_FS, color=PHYS["dark"])

# -- bus -> both lanes --------------------------------------------------------
straight((XC[0], 28.3), (XC[0], EW[0]["bot"]), FEED)
elbow([(5, 26.2), (1.2, 26.2), (1.2, 72), (DT[0]["l"], 72)], FEED)
ax.text(-2.8, 49, "raw streams\nto twin", ha="center", va="center",
        fontsize=7.4, color=FEED, rotation=90, linespacing=1.1)
ax.text(XC[0] + 1.4, 30.5, "streams", ha="left", va="center", fontsize=7.4, color=FEED)

# -- EEW <-> twin coupling: labels horizontal, placed left of each arrow ------
def cross(x, up, label):
    i = XC.index(x)
    a, b = ((x, EW[i]["top"]), (x, DT[i]["bot"])) if up else \
           ((x, DT[i]["bot"]), (x, EW[i]["top"]))
    straight(a, b, CROSS, head=11)
    ax.text(x - 1.4, 58, label, ha="right", va="center", fontsize=7.6,
            color=CROSS, linespacing=1.05)

cross(32.25, True,  "event M,\nlocation")
cross(51.0,  True,  "shaking\nfield")
cross(69.75, False, "damage-informed\nthresholds")
cross(88.5,  True,  "alerts &\nactions")

# -- feedback / control loop --------------------------------------------------
elbow([(96.5, 72), (102.5, 72), (102.5, 26.2), (95.2, 26.2)], LOOP)
ax.text(107.0, 49, "feedback loop\nmodel updates · retrofit\nresponse · sensor tasking",
        ha="center", va="center", fontsize=7.6, color=LOOP, rotation=90, linespacing=1.15)

# -- key + footer -------------------------------------------------------------
def keyline(x, c, ls, label):
    lw = DASH_LW if ls == "--" else SOLID_LW
    ax.add_patch(FancyArrowPatch((x, 1.0), (x + 5, 1.0), arrowstyle="-|>",
                 mutation_scale=10, lw=lw, ls=ls, color=c, shrinkA=0, shrinkB=0))
    ax.text(x + 6, 1.0, label, ha="left", va="center", fontsize=7.6, color="#333")

keyline(4,  FEED,      "-",  "pipeline flow")
keyline(30, CROSS,     "-",  "EEW\u2013twin coupling")
keyline(60, LOOP,      "--", "feedback / control")
ax.text(50, -3.4, "Latency \u2014 EEW: seconds  ·  digital twin: minutes\u2013days  ·  "
        "feedback loop: days\u2013years.", ha="center", va="center", fontsize=7.5, color="#555")
ax.text(50, -5.8, "Software: Python, Matplotlib.   Source: authors.",
        ha="center", va="center", fontsize=7.4, color="#777")

# -- title (plain) auto-scaled to the full figure width -----------------------
title = ax.text(50, 96.3,
                "Coupled earthquake-early-warning and urban digital-twin "
                "architecture for Istanbul seismic resilience",
                ha="center", va="center", color="#111111", fontsize=11.3)
fig.canvas.draw()
r = fig.canvas.get_renderer()
boxes = []
for a in ax.get_children():
    if a is title:
        continue
    try:
        e = a.get_window_extent(r)
        if e.width > 1 and e.height > 1:
            boxes.append(e)
    except Exception:
        pass
full = mtr.Bbox.union(boxes)
tb = title.get_window_extent(r)
cxd = (full.x0 + full.x1) / 2.0
title.set_fontsize(11.3 * (full.width * 0.995) / tb.width)
title.set_position((ax.transData.inverted().transform((cxd, 0))[0], 96.3))

fig.savefig("fig03_eew_digital_twin.pdf", bbox_inches="tight", pad_inches=0.04)
fig.savefig("fig03_eew_digital_twin.png", dpi=600, bbox_inches="tight", pad_inches=0.04)
print("wrote fig03_eew_digital_twin.pdf / .png")
