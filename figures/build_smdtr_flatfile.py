#!/usr/bin/env python3
# =============================================================================
# build_smdtr_flatfile.py  —  assemble the ground-motion flatfile for
# fig_gm_validation.py from the AFAD SMD-TR database (NO ObsPy: the intensity
# measures are already computed). Merges:
#     Metadata.csv     -> Mw, distance, station/record key
#     IM_<COMP>.csv    -> observed PGA (RotD50 by default)
#     AFAD_vs30.csv    -> Vs30 per station   (if Vs30 not already in Metadata)
# Output: SMD_TR_flatfile.csv  with columns  record, Mw, Rjb, Vs30, PGA_g
#
# Keys are whitespace/dtype-normalised before joining, and the shared key is
# chosen by actual value-overlap (fixes the "0 records" case).
#
# 1st run: set PEEK=True to print every file's columns + ColumnInfo, then map
#          any column the auto-detector missed via the OVERRIDES block below.
# =============================================================================
import os, sys, glob, pandas as pd, numpy as np

# ------------------------------------------------------------------ TUNE HERE
SMDTR = os.environ.get("SMDTR_DIR", "../data/SMD-TR")  # AFAD SMD-TR (PRJ-3950); see data/README.md
COMP  = "RotD50"                      # RotD50 | Geo | RotD100 | EW | NS
OUT   = "SMD_TR_flatfile.csv"
PEEK  = False                         # True = just describe the files and exit
OVERRIDES = {                         # confirmed from your Metadata.csv headers
    "mw": "Mag",                      # numeric magnitude ('Mag_Type'/'Mag_Ref' are text)
    # "dist":"RJB_(km)", "vs30":"Vs30_(m/s)", "sta":"Station_Code",
}
# ----------------------------------------------------------------------------

META = os.path.join(SMDTR, "Metadata.csv")
IM   = os.path.join(SMDTR, "Intensity Measures", f"IM_{COMP}.csv")
VS30 = os.path.join(SMDTR, "AFAD_vs30.csv")

def load(p):
    for sep in (",", ";", "\t"):
        try:
            df = pd.read_csv(p, sep=sep, low_memory=False)
            if df.shape[1] > 1: return df
        except Exception: pass
    return pd.read_csv(p)

def norm(s):
    t = s.astype(str).str.strip()
    num = pd.to_numeric(t, errors="coerce")
    if num.notna().mean() > 0.95:                              # mostly-numeric key
        vals = num.dropna().values
        if vals.size and np.nanmax(np.abs(vals % 1)) < 1e-9:   # integer-valued
            return num.round().astype("Int64").astype(str)     # "1.0" -> "1", "01" -> "1"
        return num.astype(float).astype(str)
    return t                                                   # string key: just stripped

def find_first(df, keys, avoid=()):          # respects key PRIORITY order
    cols = {c.lower(): c for c in df.columns}
    for k in keys:
        for lc, o in cols.items():
            if k in lc and not any(a in lc for a in avoid): return o
    return None

def col(df, role, keys, avoid=()):
    if role in OVERRIDES and OVERRIDES[role] in df.columns: return OVERRIDES[role]
    c = find_first(df, keys, avoid=avoid)
    if c is None: raise SystemExit(
        f"[!] Could not find '{role}' in {list(df.columns)}. "
        f"Set OVERRIDES['{role}']='<exact column>' and re-run.")
    return c

def to_num(s):                               # numeric, tolerant of decimal-comma
    x = pd.to_numeric(s, errors="coerce")
    if x.notna().mean() < 0.5:
        x = pd.to_numeric(s.astype(str).str.replace(",", ".", regex=False), errors="coerce")
    return x

def numcol(df, role, keys, avoid=()):        # pick the name-matching column that is NUMERIC
    if role in OVERRIDES and OVERRIDES[role] in df.columns: return OVERRIDES[role]
    cols = {c.lower(): c for c in df.columns}
    cands = []
    for k in keys:
        for lc, o in cols.items():
            if k in lc and not any(a in lc for a in avoid) and o not in cands: cands.append(o)
    best, frac = None, 0.0
    for c in cands:
        f = to_num(df[c]).notna().mean()
        if f > frac: best, frac = c, f
    if best is None or frac < 0.5:
        raise SystemExit(
            f"[!] No numeric '{role}' column. Tried {cands} (best numeric fraction={frac:.2f}).\n"
            f"    All columns: {list(df.columns)}\n"
            f"    Set OVERRIDES['{role}']='<exact numeric column>' and re-run.")
    return best

meta = load(META); im = load(IM)
vs30 = load(VS30) if os.path.exists(VS30) else None

if PEEK:
    for name, df in [("Metadata", meta), (f"IM_{COMP}", im), ("AFAD_vs30", vs30)]:
        if df is None: print(f"\n== {name}: (missing) =="); continue
        print(f"\n== {name}  ({len(df)} rows) ==\ncolumns: {list(df.columns)}")
        print(df.head(3).to_string())
    for ci in (glob.glob(os.path.join(SMDTR, "ColumnInfo*.csv")) +
               glob.glob(os.path.join(SMDTR, "Intensity Measures", f"ColumnInfo_IM_{COMP}.csv"))):
        print(f"\n== {os.path.basename(ci)} =="); print(load(ci).to_string()[:1500])
    sys.exit(0)

# --- shared record key, chosen by max value-overlap (normalised) ------------
shared = [c for c in meta.columns if c in im.columns]
if OVERRIDES.get("key"):
    key = OVERRIDES["key"]
elif shared:
    key = max(shared, key=lambda c: (len(set(norm(meta[c])) & set(norm(im[c]))),
                                      im[c].nunique()/max(len(im), 1)))
else:
    raise SystemExit(f"[!] No shared column between Metadata {list(meta.columns)} "
                     f"and IM {list(im.columns)}. Set OVERRIDES['key'].")

overlap = len(set(norm(meta[key])) & set(norm(im[key])))
print(f"key='{key}'  overlap={overlap}/{len(im)}")
if overlap == 0:
    print("  Metadata", key, "samples:", list(norm(meta[key]))[:5])
    print("  IM      ", key, "samples:", list(norm(im[key]))[:5])
    raise SystemExit("[!] Keys share no values (format mismatch). "
                     "Check the two sample lists above; set OVERRIDES['key'] if needed.")

mw_c   = numcol(meta, "mw",   ["mw", "magnitude", "mag"], avoid=("type", "source", "ref", "author", "agency"))
dist_c = numcol(meta, "dist", ["rjb", "rrup", "rhyp", "repi", "joyner", "rupt", "epic"])
pga_c  = numcol(im,   "pga",  ["pga"], avoid=("psa", "spectral", "sa("))
print(f"columns -> Mw='{mw_c}', dist='{dist_c}', PGA='{pga_c}'")

meta["_k"] = norm(meta[key]); im["_k"] = norm(im[key])
df = (meta[["_k", mw_c, dist_c]]
      .merge(im[["_k", pga_c]], on="_k")
      .rename(columns={mw_c: "Mw", dist_c: "Rjb", pga_c: "PGA"}))

# --- Vs30: from Metadata if it has a populated column, else join AFAD_vs30 ---
vs_in_meta = find_first(meta, ["vs30"])
meta_vs_ok = vs_in_meta and pd.to_numeric(meta[vs_in_meta], errors="coerce").notna().mean() > 0.5
if meta_vs_ok:
    vs_by_k = pd.to_numeric(meta.set_index("_k")[vs_in_meta], errors="coerce")
    df["Vs30"] = df["_k"].map(vs_by_k).values
    print(f"Vs30 taken from Metadata['{vs_in_meta}']")
elif vs30 is not None:
    sta_v = col(vs30, "sta_v", ["station", "sta", "afad", "code", "no"], avoid=("distance",))
    vs_c  = col(vs30, "vs30",  ["vs30"])
    vkeys = set(norm(vs30[sta_v]))
    # auto-pick the Metadata station column: the one whose values overlap AFAD_vs30 most
    sta_m = OVERRIDES.get("sta") or max(meta.columns, key=lambda c: len(set(norm(meta[c])) & vkeys))
    matched = len(set(norm(meta[sta_m])) & vkeys)
    print(f"Vs30 station join: Metadata['{sta_m}'] <-> AFAD_vs30['{sta_v}']  (stations matched={matched})")
    if matched == 0:
        print("  Metadata  station samples:", list(norm(meta[sta_m]))[:5])
        print("  AFAD_vs30 station samples:", list(norm(vs30[sta_v]))[:5])
        raise SystemExit("[!] Station codes don't match. Set OVERRIDES['sta']='<Metadata col>'.")
    smap = dict(zip(norm(vs30[sta_v]), pd.to_numeric(vs30[vs_c], errors="coerce")))
    sta_by_k = meta.set_index("_k")[sta_m]
    df["Vs30"] = norm(df["_k"].map(sta_by_k)).map(smap).values
else:
    raise SystemExit("[!] No Vs30 in Metadata and AFAD_vs30.csv not found.")

before = len(df)
for c in ("Mw", "Rjb", "PGA", "Vs30"):
    df[c] = to_num(df[c])
nan_rep = {c: int(df[c].isna().sum()) for c in ("Mw", "Rjb", "PGA", "Vs30")}
df = df.dropna(subset=["Mw", "Rjb", "PGA", "Vs30"])
df = df[(df.PGA > 0) & (df.Rjb > 0) & (df.Vs30 > 0)]
if len(df) == 0:
    raise SystemExit(f"[!] All {before} merged rows dropped. NaN per field: {nan_rep}. "
                     "The field with ~all NaN is the culprit (usually Vs30) — see the join line above.")
print(f"kept {len(df)}/{before} rows (dropped as NaN: {nan_rep})")

# --- PGA units -> g  (SMD-TR IMs are often cm/s^2; convert if they look like gal)
gal = df.PGA.median() > 5
df["PGA_g"] = df.PGA/980.665 if gal else df.PGA
print(f"PGA units: {'cm/s^2 -> converted to g' if gal else 'g (kept)'}")

out = df[["_k", "Mw", "Rjb", "Vs30", "PGA_g"]].rename(columns={"_k": "record"})
out.to_csv(OUT, index=False)
print(f"Wrote {OUT}: {len(out)} records | dist='{dist_c}', PGA='{pga_c}'")
print(out.head(6).to_string(index=False))
print(f"\nNext: set  FLATFILE = '{os.path.abspath(OUT)}'  in fig_gm_validation.py")
