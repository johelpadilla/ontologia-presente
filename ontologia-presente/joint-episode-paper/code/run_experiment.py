#!/usr/bin/env python3
"""
Convenience launcher for the Joint Score comparison experiment.

From the joint-episode-paper/ directory:
    python code/run_experiment.py

Or from inside code/:
    python run_experiment.py
"""

import sys
from pathlib import Path

# Ensure we can import local packages
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    # Delegate to the full runner
    from experiments.run_comparison import main
    main()
