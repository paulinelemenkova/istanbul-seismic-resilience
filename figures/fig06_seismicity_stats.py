import os
#!/usr/bin/env python3
# =============================================================================
# Fig. 6  —  Seismicity statistics of the Marmara catalogue
#   (a) Gutenberg-Richter frequency-magnitude + b-value (this is the runnable
#       core from the earlier message), (b) magnitude histogram,
#       (c) depth histogram, (d) cumulative events vs time.
#   Replaces the illustrative ROC curve with a real, quantitative analysis.
#
# Run:  python3 fig06_seismicity_stats.py
# =============================================================================
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ------------------------------------------------------------------ TUNE HERE
CAT = os.environ.get("IEB_CATALOG", "../data/inputs/IEB_Marmara.csv")  # place your catalogue here
# CAT = "/Volumes/TOSHIBA/DATA/TURKEY/IEB_3000_Marmara.csv"  # includes big historical events
OUT = "fig06_seismicity_stats"
dM  = 0.1                                              # magnitude bin width
# ----------------------------------------------------------------------------

# --- load, robust to column-name variants ---------------------------------
d = pd.read_csv(CAT)
cols = {c.lower(): c for c in d.columns}
pick = lambda *ns: next(o for n in ns for lc, o in cols.items() if n in lc)
mag = pd.to_numeric(d[pick("mag", "ml", "mw")], errors="coerce")
dep = pd.to_numeric(d[pick("depth")],           errors="coerce")
dt  = pd.to_datetime(dict(year=d[pick("year")], month=d[pick("month")],
                          day=d[pick("day")]),  errors="coerce")
m = mag.dropna().values

# --- completeness Mc (maximum curvature +0.2) and Aki-Utsu b-value MLE ------
bins = np.arange(np.floor(m.min()*10)/10, m.max()+dM, dM)
h, _ = np.histogram(m, bins=bins)
Mc   = round(bins[np.argmax(h)] + 0.2, 1)
mm   = m[m >= Mc]
b    = np.log10(np.e) / (mm.mean() - (Mc - dM/2))
a    = np.log10(len(mm)) + b*Mc
b_err = 2.30 * b**2 * np.sqrt(((mm-mm.mean())**2).sum() / (len(mm)*(len(mm)-1)))  # Shi & Bolt 1982

# --- figure ----------------------------------------------------------------
fig, ax = plt.subplots(2, 2, figsize=(10, 8))

# (a) Gutenberg-Richter
ms  = np.sort(m); N = np.arange(len(ms), 0, -1)
edges = np.arange(m.min(), m.max()+dM, dM); cnt, _ = np.histogram(m, bins=edges)
ax[0,0].semilogy(ms, N, 'o', ms=4, mfc='none', color='steelblue', label='cumulative')
ax[0,0].semilogy((edges[:-1]+edges[1:])/2, np.where(cnt>0, cnt, np.nan), 's',
                 ms=3, color='gray', alpha=.6, label='non-cumulative')
xx = np.linspace(Mc, m.max(), 50)
ax[0,0].semilogy(xx, 10**(a - b*xx), 'r-', lw=2,
                 label=f'GR fit: b={b:.2f}\u00b1{b_err:.2f}, Mc={Mc:.1f}')
ax[0,0].axvline(Mc, ls='--', color='gray')
ax[0,0].set(xlabel='Magnitude', ylabel='N (M \u2265 m)', title='(a) Frequency\u2013magnitude')
ax[0,0].legend(fontsize=8)

# (b) magnitude histogram
ax[0,1].hist(m, bins=edges, color='steelblue', edgecolor='k', lw=.3)
ax[0,1].set(xlabel='Magnitude', ylabel='Count', title='(b) Magnitude distribution')

# (c) depth histogram
ax[1,0].hist(dep.dropna(), bins=25, color='indianred', edgecolor='k', lw=.3)
ax[1,0].set(xlabel='Depth (km)', ylabel='Count', title='(c) Depth distribution')

# (d) cumulative number vs time
ok = dt.notna(); ts = np.sort(dt[ok].values)
ax[1,1].plot(ts, np.arange(1, len(ts)+1), '-', color='seagreen')
ax[1,1].set(xlabel='Year', ylabel='Cumulative events', title='(d) Temporal evolution')

for a_ in ax.ravel():
    a_.minorticks_on(); a_.grid(which='both', alpha=.25)

fig.suptitle(f'Marmara seismicity (N={len(m)} events)', y=1.00, fontsize=12)
fig.tight_layout()
fig.savefig(OUT+".png", dpi=300)
fig.savefig(OUT+".pdf")                       # vector, for LaTeX
print(f"Done -> {OUT}.png / {OUT}.pdf   N={len(m)}  Mc={Mc}  b={b:.2f}\u00b1{b_err:.2f}  a={a:.2f}")
