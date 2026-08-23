"""Cascading-failure propagation on the infrastructure graph (Eq. 3).
Assets fail stochastically with their damage probability; failures remove
nodes and we track the largest surviving connected component."""
import networkx as nx
import numpy as np

G = nx.Graph()
# nodes: (id, damage probability); edges: functional dependencies
assets = {"sub_A": 0.30, "sub_B": 0.65, "bridge_1": 0.55,
          "hosp_1": 0.20, "pump_1": 0.40, "metro_1": 0.50}
G.add_nodes_from(assets)
G.add_edges_from([("sub_A", "hosp_1"), ("sub_A", "pump_1"),
                  ("sub_B", "metro_1"), ("bridge_1", "metro_1"),
                  ("sub_A", "sub_B"), ("pump_1", "hosp_1")])

def simulate(G, pfail, n=2000, seed=0):
    rng = np.random.default_rng(seed)
    base = G.number_of_nodes()
    frac = []
    for _ in range(n):
        failed = {v for v in G if rng.random() < pfail[v]}
        H = G.subgraph([v for v in G if v not in failed])
        gcc = max((len(c) for c in nx.connected_components(H)), default=0)
        frac.append(gcc / base)
    return float(np.mean(frac)), float(np.std(frac))

mean_gcc, std_gcc = simulate(G, assets)
print(f"Mean surviving giant component: {mean_gcc:.2f} +/- {std_gcc:.2f}")
# rank assets by betweenness -> criticality for prioritisation
crit = nx.betweenness_centrality(G)
print("Most critical:", max(crit, key=crit.get))
