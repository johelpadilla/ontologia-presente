"""
Utilities for reproducible seeding across the Joint Episode comparison experiment.
"""

import numpy as np
import random


def set_global_seed(seed: int):
    """Set seeds for numpy, random, and python hash for full reproducibility."""
    np.random.seed(seed)
    random.seed(seed)
    # For sklearn etc if used
    try:
        from sklearn.utils import check_random_state
        # sklearn often respects numpy global in older versions
    except Exception:
        pass


def get_rng(seed: int) -> np.random.Generator:
    """Return a fresh Generator for local use (preferred over global)."""
    return np.random.default_rng(seed)
