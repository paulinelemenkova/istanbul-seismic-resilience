"""Fragility-based damage probability (Eq. 2) for a building inventory.
Each asset carries a class whose (theta, beta) define a lognormal fragility."""
import numpy as np
import pandas as pd
from scipy.stats import norm

# median PGA capacity (g) and log-std per structural class, damage state >= DS2
FRAGILITY = {
    "pre1999_RC":   (0.18, 0.55),   # older reinforced concrete
    "post1999_RC":  (0.35, 0.50),   # post-code reinforced concrete
    "masonry":      (0.14, 0.60),
    "steel":        (0.45, 0.45),
}

def damage_prob(pga_g, cls):
    theta, beta = FRAGILITY[cls]
    return norm.cdf(np.log(pga_g / theta) / beta)

# inventory: building id, class, and site PGA sampled from the shakefield
inv = pd.DataFrame({
    "bid":  [1, 2, 3, 4],
    "cls":  ["pre1999_RC", "post1999_RC", "masonry", "steel"],
    "pga":  [0.42, 0.42, 0.30, 0.55],
})
inv["p_damage"] = [damage_prob(p, c) for p, c in zip(inv.pga, inv.cls)]
print(inv.to_string(index=False))
inv.to_csv("building_damage.csv", index=False)
