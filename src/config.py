"""
Phase 12, Step 3: Shared config. DATA_DIR defaults to the full
local processed data, but can be overridden (e.g. on Render, where
we only bundle the small demo subset in data/demo).
"""

import os

DATA_DIR = os.environ.get("DATA_DIR", "data/processed")
