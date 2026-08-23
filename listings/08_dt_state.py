"""Digital-Twin asset-state store: a spatially indexed, time-stamped table.
Uses SQLite/SpatiaLite here; swap the DSN for PostGIS in production."""
import sqlite3
import datetime as dt

conn = sqlite3.connect("twin_state.db")
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS asset_state (
    asset_id   TEXT,
    asset_type TEXT,
    lon        REAL,
    lat        REAL,
    status     TEXT,          -- operational | degraded | failed
    p_damage   REAL,
    updated_at TEXT,
    PRIMARY KEY (asset_id, updated_at))""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_geo ON asset_state(lon, lat)")

def upsert(asset_id, atype, lon, lat, status, p_damage):
    cur.execute("INSERT INTO asset_state VALUES (?,?,?,?,?,?,?)",
                (asset_id, atype, lon, lat, status, p_damage,
                 dt.datetime.now(dt.timezone.utc).isoformat()))
    conn.commit()

upsert("hosp_1", "hospital", 29.03, 41.01, "degraded", 0.42)
upsert("bridge_1", "bridge", 29.06, 41.05, "failed", 0.71)
n = cur.execute("SELECT COUNT(*) FROM asset_state").fetchone()[0]
print(f"asset_state rows: {n}")
conn.close()
