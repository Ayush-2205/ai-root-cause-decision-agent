"""
Phase 12, Step 2: Copy the original 6-case pilot's processed files
into data/demo/ - a small, deliberately committed subset for
deployment, separate from the full 30-case reproducible set.
"""

import shutil
import os
import pandas as pd

selected = pd.read_csv("data/processed/selected_cases.csv")  # the original 6, not expanded
os.makedirs("data/demo", exist_ok=True)

selected.to_csv("data/demo/selected_cases.csv", index=False)

for case_name in selected["case"]:
    src = f"data/processed/{case_name}"
    dst = f"data/demo/{case_name}"
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    print(f"Copied {case_name}")

total_size = sum(
    os.path.getsize(os.path.join(root, f))
    for root, _, files in os.walk("data/demo")
    for f in files
)
print(f"\nTotal data/demo size: {total_size / 1_000_000:.2f} MB")