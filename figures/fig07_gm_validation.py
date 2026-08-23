#!/usr/bin/env python3
# =============================================================================
# Fig. (reserved slot 1) — Measured vs predicted ground motion (PGA & MMI)
#   Observed PGA from recorded waveforms (AFAD SMD-TR flatfile) vs predicted PGA
#   from the Listing-3 ground-motion model (gmm_pga), with a 1:1 reference line,
#   factor-of-2 / +-1-unit guides, MC-dropout predictive spread (Listing 10),
#   and residual statistics. PGA -> MMI via Worden et al. (2012).
#
# Run:  python3 fig_gm_validation.py
#   Put an AFAD SMD-TR strong-motion flatfile at FLATFILE with (any-case) columns:
#     Mw / magnitude , Rrup|Rjb|Rhyp|Repi (km) , Vs30 (m/s) , PGA (g or cm/s^2)
#   If the file is absent, the script renders a clearly-labelled SYNTHETIC demo.
# =============================================================================
import os, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ------------------------------------------------------------------ TUNE HERE
_cands = ["SMD_TR_flatfile.csv", "../data/derived/SMD_TR_flatfile.csv",
          os.path.join(os.path.dirname(os.path.abspath(__file__)), "SMD_TR_flatfile.csv")]
FLATFILE = next((p for p in _cands if os.path.exists(p)), _cands[0])
OUT      = "fig_gm_validation"
PGA_UNIT = "auto"          # "auto" | "g" | "cm/s2"
GMM      = "AkkarEtAlRjb2014"   # Türkiye/Europe (Rjb+Vs30). Alt: "KaleEtAl2015Turkey", "BooreEtAl2014"
RAKE     = 0.0             # NAF is strike-slip (rake 0). Use -90 normal, 90 reverse.
# ----------------------------------------------------------------------------

# ---- calibrated ground-motion model via OpenQuake --------------------------
try:
    from openquake.hazardlib import valid, const
    from openquake.hazardlib.imt import PGA
    from openquake.hazardlib.contexts import RuptureContext
except ImportError:
    raise SystemExit("[!] OpenQuake not installed. In your (base) env run one of:\n"
                     "      pip install openquake.engine\n"
                     "      conda install -c conda-forge openquake.engine")
try:
    _gsim = valid.gsim(GMM)
except Exception as e:
    raise SystemExit(f"[!] Unknown GMM '{GMM}': {e}\n"
        "    List candidates:  python3 -c \"from openquake.hazardlib.gsim import get_available_gsims as g;"
        " print([k for k in g() if any(s in k for s in ('Akkar','Kale','Boore','Bindi'))])\"")

def gmm_pga(mw, r_rup, vs30):
    """Median PGA (g) from the chosen OpenQuake GMM, over arrays of mw, Rjb, Vs30."""
    mw = np.atleast_1d(np.asarray(mw, float))
    r  = np.atleast_1d(np.asarray(r_rup, float))
    vs = np.atleast_1d(np.asarray(vs30, float))
    n = len(mw); ctx = RuptureContext()
    ctx.mag = mw; ctx.rake = np.full(n, RAKE)
    ctx.rjb = r;  ctx.rrup = r                     # data are Rjb; rrup≈rjb if the GMM needs it
    ctx.vs30 = vs
    ctx.hypo_depth = np.full(n, 10.0); ctx.ztor = np.full(n, 0.0)
    ctx.dip = np.full(n, 90.0); ctx.width = np.full(n, 12.0)
    mean, _ = _gsim.get_mean_and_stddevs(ctx, ctx, ctx, PGA(), [const.StdDev.TOTAL])
    return np.exp(mean)                            # PGA in g

# sanity check on load (Mw7 at Rjb 10 km, rock ~760 m/s should be ~0.2-0.4 g)
print(f"[GMM] {GMM}: PGA(Mw7, Rjb=10 km, Vs30=760) = {float(np.ravel(gmm_pga(7.0,10.0,760.0))[0]):.3f} g")

# ---- PGA (g) -> MMI : Worden et al. (2012) GMICE ---------------------------
def pga_to_mmi(pga_g):
    a = np.log10(np.clip(pga_g, 1e-6, None) * 980.665)     # cm/s^2
    mmi = np.where(a < 1.57, 1.78 + 1.55*a, -1.60 + 3.70*a)
    return np.clip(mmi, 1.0, 10.0)

# ---- load observed data, or synthesise a labelled demo ---------------------
DEMO = not os.path.exists(FLATFILE)
if not DEMO:
    df = pd.read_csv(FLATFILE)
    cols = {c.lower(): c for c in df.columns}
    def pick(*ns, req=True):
        for n in ns:
            for lc, o in cols.items():
                if n in lc: return o
        if req: raise KeyError(f"need one of {ns} in {list(df.columns)}")
        return None
    mw   = pd.to_numeric(df[pick("mw","magnitude","mag")], errors="coerce")
    dist = pd.to_numeric(df[pick("rrup","rjb","rhyp","repi","dist")], errors="coerce")
    vs30 = pd.to_numeric(df[pick("vs30")], errors="coerce")
    pga_o= pd.to_numeric(df[pick("pga")], errors="coerce")
    d = pd.DataFrame({"mw":mw,"r":dist,"vs30":vs30,"pga_o":pga_o}).dropna()
    d = d[(d.pga_o>0)&(d.r>0)&(d.vs30>0)].reset_index(drop=True)
    if len(d) == 0:
        raise SystemExit(f"[!] {FLATFILE} has no usable rows — re-run build_smdtr_flatfile.py "
                         "(it should print 'Wrote ... N records' with N>0).")
    unit_g = (d.pga_o.median() < 5) if PGA_UNIT=="auto" else (PGA_UNIT=="g")
    d["pga_o_g"] = d.pga_o if unit_g else d.pga_o/980.665
else:
    rng0 = np.random.default_rng(1)
    n = 350
    mw   = rng0.uniform(4.0, 7.4, n)
    r    = 10**rng0.uniform(0.3, 2.3, n)                 # ~2-200 km
    vs30 = rng0.uniform(180, 760, n)
    d = pd.DataFrame({"mw":mw,"r":r,"vs30":vs30})
    d["pga_o_g"] = gmm_pga(mw, r, vs30) * np.exp(0.60*rng0.normal(size=n))  # obs = model x scatter

# ---- predicted PGA (Listing 3) + MC-dropout predictive spread (Listing 10) --
d["pga_p_g"] = gmm_pga(d.mw.values, d.r.values, d.vs30.values)
rng = np.random.default_rng(0)
MC = 200
mc = np.array([gmm_pga(d.mw.values + 0.05*rng.normal(size=len(d)),
                       np.clip(d.r.values*(1+0.05*rng.normal(size=len(d))), 0.5, None),
                       d.vs30.values) * np.exp(0.15*rng.normal(size=len(d)))
               for _ in range(MC)])
d["pga_p_sd"] = mc.std(0)                                  # predictive 1-sigma (g)
d["mmi_o"] = pga_to_mmi(d.pga_o_g.values)
d["mmi_p"] = pga_to_mmi(d.pga_p_g.values)

# ---- residual statistics ---------------------------------------------------
def stats_ln(o, p):
    r = np.log(o) - np.log(p)
    return dict(n=len(r), bias=r.mean(), sigma=r.std(ddof=1),
                rmse=np.sqrt((r**2).mean()),
                R2=np.corrcoef(np.log(o), np.log(p))[0,1]**2,
                within=100*np.mean(np.abs(r) < np.log(2)))
def stats_lin(o, p, tol=1.0):
    r = o - p
    return dict(n=len(r), bias=r.mean(), sigma=r.std(ddof=1),
                rmse=np.sqrt((r**2).mean()),
                R2=np.corrcoef(o, p)[0,1]**2,
                within=100*np.mean(np.abs(r) < tol))
sp = stats_ln(d.pga_o_g.values, d.pga_p_g.values)
sm = stats_lin(d.mmi_o.values, d.mmi_p.values, 1.0)

# ---- figure ----------------------------------------------------------------
fig, ax = plt.subplots(1, 2, figsize=(11, 5.2))

# (a) PGA, log-log
lo = min(d.pga_p_g.min(), d.pga_o_g.min())*0.7
hi = max(d.pga_p_g.max(), d.pga_o_g.max())*1.4
L = [lo, hi]
lower = np.clip(d.pga_p_g - d.pga_p_sd, lo*0.5, None)
ax[0].errorbar(d.pga_p_g, d.pga_o_g,
               xerr=[d.pga_p_g-lower, d.pga_p_sd], fmt="none",
               ecolor="gray", alpha=.25, lw=.6, zorder=2)
oa = d.mw.values.argsort()          # ascending -> high Mw (light) plotted last = on top
sc = ax[0].scatter(d.pga_p_g.values[oa], d.pga_o_g.values[oa], c=d.mw.values[oa],
                   s=20, cmap="viridis", edgecolor="k", lw=.3, zorder=3)
ax[0].plot(L, L, "k-", lw=1.6, label="1:1", zorder=4)
ax[0].plot(L, [2*x for x in L], "k--", lw=.8, alpha=.6, zorder=4)
ax[0].plot(L, [.5*x for x in L], "k--", lw=.8, alpha=.6, label="factor 2", zorder=4)
ax[0].set(xscale="log", yscale="log", xlim=L, ylim=L,
          xlabel=f"Predicted PGA (g) — {GMM}", ylabel="Observed PGA (g)")
ax[0].set_title("(a) Peak ground acceleration")
ax[0].set_aspect("equal")
fig.colorbar(sc, ax=ax[0], fraction=.046, pad=.03).set_label(r"M$_w$")
t1 = (f"N = {sp['n']}\n"+r"bias$_{\ln}$ = "+f"{sp['bias']:+.2f}\n"
      +r"$\sigma_{\ln}$ = "+f"{sp['sigma']:.2f}\n"
      +f"RMSE = {sp['rmse']:.2f}\n"+r"R$^2$ = "+f"{sp['R2']:.2f}\n"
      +f"within ×2 = {sp['within']:.0f}%")
ax[0].text(.04,.96,t1,transform=ax[0].transAxes,va="top",ha="left",fontsize=8,
           bbox=dict(fc="white",ec="gray",alpha=.85))
ax[0].legend(loc="lower right",fontsize=8)

# (b) MMI, linear
ob = d.r.values.argsort()           # ascending -> far (light) plotted last = on top
sc2 = ax[1].scatter(d.mmi_p.values[ob], d.mmi_o.values[ob], c=d.r.values[ob],
                    s=20, cmap="cividis", edgecolor="k", lw=.3, zorder=3)
M = [2, 9]
ax[1].plot(M, M, "k-", lw=1.6, label="1:1", zorder=4)
ax[1].plot(M, [m+1 for m in M], "k--", lw=.8, alpha=.6, zorder=4)
ax[1].plot(M, [m-1 for m in M], "k--", lw=.8, alpha=.6, label="±1 unit", zorder=4)
ax[1].set(xlim=M, ylim=M, xlabel=f"Predicted MMI (from {GMM} PGA)", ylabel="Observed MMI")
ax[1].set_title("(b) Macroseismic intensity")
ax[1].set_aspect("equal")
cb = fig.colorbar(sc2, ax=ax[1], fraction=.046, pad=.03); cb.set_label("Distance (km)")
t2 = (f"N = {sm['n']}\nbias = {sm['bias']:+.2f}\n"+r"$\sigma$ = "+f"{sm['sigma']:.2f}\n"
      +f"RMSE = {sm['rmse']:.2f}\n"+r"R$^2$ = "+f"{sm['R2']:.2f}\n"
      +f"within ±1 = {sm['within']:.0f}%")
ax[1].text(.04,.96,t2,transform=ax[1].transAxes,va="top",ha="left",fontsize=8,
           bbox=dict(fc="white",ec="gray",alpha=.85))
ax[1].legend(loc="lower right",fontsize=8)

for a in ax:
    a.grid(which="both", alpha=.25); a.minorticks_on()

if DEMO:
    fig.suptitle("SYNTHETIC DEMO — replace FLATFILE with AFAD SMD-TR records",
                 color="crimson", fontsize=11, y=1.02)

fig.tight_layout()
fig.savefig(OUT+".png", dpi=300, bbox_inches="tight")
fig.savefig(OUT+".pdf", bbox_inches="tight")
print(f"{'DEMO ' if DEMO else ''}Done -> {OUT}.png / {OUT}.pdf")
print(f"PGA: N={sp['n']} bias(ln)={sp['bias']:+.2f} sigma={sp['sigma']:.2f} "
      f"RMSE={sp['rmse']:.2f} R2={sp['R2']:.2f} within2={sp['within']:.0f}%")
print(f"MMI: N={sm['n']} bias={sm['bias']:+.2f} sigma={sm['sigma']:.2f} "
      f"RMSE={sm['rmse']:.2f} R2={sm['R2']:.2f} within1={sm['within']:.0f}%")
