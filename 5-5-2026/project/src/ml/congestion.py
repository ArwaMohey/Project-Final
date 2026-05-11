"""
ML BONUS — congestion prediction.

Trains a RandomForestRegressor on the per-edge, per-period traffic patterns
provided in the dataset.

Features : hour (int), period (one-hot), distance, capacity, condition
Target   : vehicles/hour

The dataset is expanded from per-edge per-period counts: each
(edge × period) entry is replicated with small Gaussian noise to give the
model a meaningful training signal.

API
---
    train_model()                           → (sklearn Pipeline, metrics dict)
    predict_congestion(model, edge_data, hour) → float (vph)
"""
from __future__ import annotations
from typing import Dict, Any, Tuple
import numpy as np

try:
    import pandas as pd
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import OneHotEncoder
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.metrics import mean_absolute_error
    SKLEARN_OK = True
except ImportError:
    SKLEARN_OK = False

PERIOD_HOURS = {
    "morning":   8,
    "afternoon": 14,
    "evening":   18,
    "night":     23,
}

NUM_NOISE_SAMPLES = 6   # noisy copies per (edge, period) pair
NOISE_SIGMA       = 80  # vehicles/hour standard deviation


def _build_dataset():
    """Build a pandas DataFrame from the Cairo graph's traffic attributes."""
    if not SKLEARN_OK:
        raise RuntimeError("pandas / scikit-learn not available")

    from src.data.loader import load_dataset
    ds = load_dataset()
    G  = ds["graph_existing"]

    rng  = np.random.default_rng(42)
    rows = []
    for u, v, d in G.edges(data=True):
        for period, base_vph in d["traffic"].items():
            for _ in range(NUM_NOISE_SAMPLES):
                noisy_vph = float(base_vph) + rng.normal(0, NOISE_SIGMA)
                rows.append({
                    "hour":      PERIOD_HOURS[period],
                    "period":    period,
                    "distance":  d["distance"],
                    "capacity":  d["capacity"],
                    "condition": d["condition"],
                    "vph":       max(0.0, noisy_vph),
                })
    return pd.DataFrame(rows)


def train_model() -> Tuple[Any, Dict[str, Any]]:
    """
    Train and return a (pipeline, metrics) pair.
    metrics: {'mae_vph', 'n_train', 'n_test'}
    """
    if not SKLEARN_OK:
        raise RuntimeError("scikit-learn not available")

    df = _build_dataset()
    X  = df[["hour", "period", "distance", "capacity", "condition"]]
    y  = df["vph"]

    pre = ColumnTransformer(
        [("period_oh", OneHotEncoder(sparse_output=False, handle_unknown="ignore"),
          ["period"])],
        remainder="passthrough",
    )
    model = Pipeline([
        ("pre", pre),
        ("rf",  RandomForestRegressor(
            n_estimators=120, random_state=42, n_jobs=-1)),
    ])

    n     = len(df)
    rng   = np.random.default_rng(0)
    perm  = rng.permutation(n)
    split = int(0.8 * n)
    tr, te = perm[:split], perm[split:]

    model.fit(X.iloc[tr], y.iloc[tr])
    preds = model.predict(X.iloc[te])
    mae   = float(mean_absolute_error(y.iloc[te], preds))

    return model, {"mae_vph": mae, "n_train": int(split), "n_test": int(n - split)}


def predict_congestion(model, edge_data: Dict[str, Any], hour: int) -> float:
    """
    Predict traffic (vph) on a given edge at the given hour.

    Parameters
    ----------
    model     trained sklearn Pipeline from train_model()
    edge_data dict with keys: distance, capacity, condition
    hour      0-23 integer
    """
    if not SKLEARN_OK:
        raise RuntimeError("scikit-learn not available")

    import pandas as pd  # local import keeps module importable without pandas

    period = (
        "morning"   if 5  <= hour < 11 else
        "afternoon" if 11 <= hour < 16 else
        "evening"   if 16 <= hour < 21 else
        "night"
    )
    X = pd.DataFrame([{
        "hour":      hour,
        "period":    period,
        "distance":  edge_data["distance"],
        "capacity":  edge_data["capacity"],
        "condition": edge_data["condition"],
    }])
    return float(model.predict(X)[0])