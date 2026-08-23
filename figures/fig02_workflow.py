#!/usr/bin/env python3
"""
fig02_workflow.py
Two-panel figure:
  (a) AI forecasting and Digital-Twin data-processing workflow (6-stage pipeline
      with a continuous-learning feedback arc).
  (b) Real-time EEW latency budget and warning lead time.

Outputs vector PDF + 600-dpi PNG. Requires matplotlib >= 3.6. Font: Nimbus Sans.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Nimbus Sans", "Helvetica", "Arial"],
    "mathtext.default": "regular",
    "pdf.fonttype": 42, "ps.fonttype": 42,
})

BLUE, GREEN, LOOP = "#2F5C8A", "#3C8C40", "#A0442E"
BARF, DRED, GRN   = "#DCE6F1", "#9B2D20", "#2E8B57"
GREY, NOTE, GRID  = "#555555", "#777777", "#D5D5D5"
FS = dict(ptitle=15.5, btitle=12.5, bsub=11.5, cap=13, axl=14.5,
          tick=12.5, bar=12, lat=12, sw=12, green=13, note=11)

fig = plt.figure(figsize=(11, 8.2))
gs = fig.add_gridspec(2, 1, height_ratios=[0.92, 1.4], hspace=0.11,
                      left=0.055, right=0.985, top=0.955, bottom=0.075)
A = fig.add_subplot(gs[0])
B = fig.add_subplot(gs[1])

# ---------------- panel (a): workflow ----------------
A.set_xlim(0, 100)
A.set_ylim(33, 100)
A.axis("off")
A.text(0.0, 1.0, "(a)  AI forecasting and Digital-Twin data-processing workflow",
       transform=A.transAxes, ha="left", va="top",
       fontsize=FS["ptitle"], fontweight="bold", color="#222")

Hb, ycen = 30, 59
W = [13, 13, 13, 20, 13, 13]              # box 4 (Model ensemble) is the widest
gap = (94 - sum(W)) / 5.0
cx, cur = [], 3.0
for w in W:
    cx.append(cur + w / 2)
    cur += w + gap

titles = ["Multimodal\nacquisition", "Preprocessing\n& QC", "Spatio-temporal\nfusion",
          "Model ensemble\n(CNN/LSTM/Transformer/\nGNN/BNN)",
          "Uncertainty\nquantification", "Forecast &\nEEW products"]
subs   = ["seismic, GNSS,\nInSAR, IoT, GIS", "denoise, align,\nstandardise",
          "attention-based\nfeature space", "supervised training,\nk-fold CV",
          "Bayesian /\nensemble spread", "prob., Mw, PGA,\nlead time"]

for i, x in enumerate(cx):
    ec = GREEN if i == 3 else BLUE
    A.add_patch(FancyBboxPatch((x - W[i] / 2, ycen - Hb / 2), W[i], Hb,
                boxstyle="round,pad=0,rounding_size=2.2",
                fc="white", ec=ec, lw=1.8, zorder=3))
    A.text(x, ycen + 7.5, titles[i], ha="center", va="center",
           fontsize=FS["btitle"], fontweight="bold", color="#222", zorder=4, linespacing=1.1)
    A.text(x, ycen - 8.5, subs[i], ha="center", va="center",
           fontsize=FS["bsub"], color="#444", zorder=4, linespacing=1.1)

for i in range(5):                         # forward arrows
    A.add_patch(FancyArrowPatch((cx[i] + W[i] / 2, ycen), (cx[i + 1] - W[i + 1] / 2, ycen),
                arrowstyle="-|>", mutation_scale=16, lw=2.0, color=BLUE,
                shrinkA=0, shrinkB=0, zorder=3))

# continuous-learning feedback arc (Forecast -> Acquisition)
A.add_patch(FancyArrowPatch((cx[5], ycen + Hb / 2), (cx[0], ycen + Hb / 2),
            connectionstyle="arc3,rad=0.16", arrowstyle="-|>", mutation_scale=15,
            lw=2.0, ls=(0, (6, 4)), color=LOOP, shrinkA=3, shrinkB=3, zorder=2))
A.text(50, ycen - Hb / 2 - 8,
       "continuous learning: post-event observations retrain the ensemble and update the Digital Twin",
       ha="center", va="center", fontsize=FS["cap"], style="italic", color=LOOP)

# ---------------- panel (b): latency budget ----------------
B.set_xlim(-0.4, 20.7)
B.set_ylim(0, 10.7)
B.text(0.0, 1.02, "(b)  Real-time EEW latency budget and warning lead time",
       transform=B.transAxes, ha="left", va="bottom",
       fontsize=FS["ptitle"], fontweight="bold", color="#222")

for gx in range(0, 21):                    # faint vertical grid
    B.axvline(gx, color=GRID, lw=0.6, zorder=0)

# staircase of latency stages: left edge = cumulative start time (s);
# boxes share one generous width so the labels sit comfortably inside;
# the "~Xs" annotation is the cumulative elapsed time at each stage.
stages = [("Data\ntransmission",       0.0, "~1.0s"),
          ("AI phase\ndetection",       1.0, "~2.0s"),
          ("Source\nestimation",        2.0, "~3.5s"),
          ("Ground-motion\nprediction", 3.5, "~6.0s"),
          ("Alert generation\n& dissemination", 6.0, "~8.5s")]
Wbar, bh, y0, step = 2.5, 1.05, 9.2, 1.35
for i, (nm, s, lab) in enumerate(stages):
    y = y0 - i * step
    B.add_patch(Rectangle((s, y - bh / 2), Wbar, bh, fc=BARF, ec=BLUE, lw=1.5, zorder=3))
    B.text(s + Wbar / 2, y, nm, ha="center", va="center",
           fontsize=FS["bar"], color="#222", zorder=4, linespacing=1.05)
    B.text(s + Wbar + 0.3, y, lab, ha="left", va="center",
           fontsize=FS["lat"], color=GREY, zorder=4)

B.axvline(8.6, color=DRED, lw=2.2, zorder=2)                 # S-wave 30 km (solid)
B.axvline(20,  color=DRED, lw=2.0, ls=(0, (6, 4)), zorder=2) # S-wave 70 km (dashed)
# S-wave labels sit to the LEFT of their lines (right-aligned)
B.text(8.4, 10.55, "S-wave 30 km\n(~9s)", ha="right", va="top",
       fontsize=FS["sw"], color=DRED, linespacing=1.05)
B.text(19.8, 10.55, "S-wave 70 km\n(~20s)", ha="right", va="top",
       fontsize=FS["sw"], color=DRED, linespacing=1.05)

B.add_patch(FancyArrowPatch((8.6, 2.7), (20, 2.7), arrowstyle="<|-|>",
            mutation_scale=15, lw=2.2, color=GRN, zorder=3))
B.text((8.6 + 20) / 2, 2.0, "usable warning lead time (70 km)",
       ha="center", va="center", fontsize=FS["green"], color=GRN)
B.text(19.9, 0.85, "latency values are indicative and depend on network geometry and system load",
       ha="right", va="center", fontsize=FS["note"], style="italic", color=NOTE)

B.set_xticks(range(0, 21, 2))
B.tick_params(axis="x", labelsize=FS["tick"])
B.set_xlabel("time after origin (s)", fontsize=FS["axl"])
B.get_yaxis().set_visible(False)
for sp in ["top", "right", "left"]:
    B.spines[sp].set_visible(False)

fig.savefig("fig02_workflow.pdf", bbox_inches="tight", pad_inches=0.05)
fig.savefig("fig02_workflow.png", dpi=600, bbox_inches="tight", pad_inches=0.05)
print("wrote fig02_workflow.pdf / .png")
