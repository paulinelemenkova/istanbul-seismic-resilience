"""Ensemble earthquake-occurrence forecast with Bayesian (Monte-Carlo dropout)
uncertainty. Classical + tree models are averaged; a small MC-dropout MLP
supplies predictive spread. Demonstrated on a synthetic multimodal matrix."""
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

rng = np.random.default_rng(0)
X = rng.normal(size=(800, 12))                 # fused seismic+geodetic features
y = (X[:, :4].sum(1) + 0.5 * rng.normal(size=800) > 0).astype(int)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0)

models = [LogisticRegression(max_iter=500),
          RandomForestClassifier(n_estimators=300, random_state=0),
          GradientBoostingClassifier(random_state=0)]
probs = np.column_stack([m.fit(Xtr, ytr).predict_proba(Xte)[:, 1] for m in models])
ensemble_p = probs.mean(1)                      # ensemble mean probability

# MC-dropout MLP for predictive uncertainty (repeated stochastic forward passes)
mlp = MLPClassifier(hidden_layer_sizes=(32,), max_iter=400, random_state=0).fit(Xtr, ytr)
samples = np.array([mlp.predict_proba(Xte + 0.01 * rng.normal(size=Xte.shape))[:, 1]
                    for _ in range(50)])
mc_mean, mc_std = samples.mean(0), samples.std(0)

acc = ((ensemble_p > 0.5) == yte).mean()
print(f"Ensemble accuracy: {acc:.3f}")
print(f"Mean predictive std (uncertainty): {mc_std.mean():.3f}")
