"""Hospital-accessibility analysis (Eq. 4) on the surviving road network.
Damaged edges are removed; shortest travel time gives each district's
access to its nearest functioning hospital."""
import networkx as nx

# weighted road graph: edge weight = length / speed * (1 + gamma * congestion)
R = nx.Graph()
edges = [  # (u, v, length_km, speed_kmh, congestion, damaged)
    ("D1", "J1", 3.0, 50, 0.2, False), ("J1", "H1", 2.0, 40, 0.5, False),
    ("D2", "J1", 4.0, 60, 0.1, True),  ("D2", "J2", 5.0, 50, 0.3, False),
    ("J2", "H2", 2.5, 45, 0.4, False), ("D3", "J2", 3.5, 55, 0.2, False),
]
gamma = 0.8
for u, v, L, s, c, dmg in edges:
    if dmg:
        continue                        # damaged edge is impassable
    R.add_edge(u, v, w=(L / s) * 60 * (1 + gamma * c))  # minutes

hospitals = ["H1", "H2"]
for d in ["D1", "D2", "D3"]:
    best = min(
        (nx.shortest_path_length(R, d, h, weight="w")
         for h in hospitals if nx.has_path(R, d, h)), default=float("inf"))
    tag = f"{best:.1f} min" if best < float("inf") else "ISOLATED"
    print(f"District {d}: nearest hospital {tag}")
