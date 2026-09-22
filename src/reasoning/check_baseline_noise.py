"""
Phase 7, Step 2b: Confirm whether the zipkin WARN in 'carts' is
constant background noise (present in normal phase too) rather
than something caused by this fault.
"""

import pandas as pd

CASE = "re2ss_catalogue_cpu_2"

df = pd.read_parquet(f"data/processed/{CASE}/logs_labeled.parquet")
sub = df[df["service"] == "carts"]

zipkin_lines = sub[sub["message"].str.contains("zipkin", case=False, na=False)]
print(zipkin_lines["phase"].value_counts())
