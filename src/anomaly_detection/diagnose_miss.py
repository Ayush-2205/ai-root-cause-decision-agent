"""
Phase 4, Step 2: Diagnose why re2ss_orders_disk_1 missed its
true root cause in the B0 metrics-only baseline.
"""

import pandas as pd
from baseline_b0 import score_case

CASE = "re2ss_orders_disk_1"


def main():
    df = pd.read_parquet(f"data/processed/{CASE}/metrics_long.parquet")

    print("Metric types available for 'orders':")
    print(sorted(df[df["service"] == "orders"]["metric_type"].unique()))

    print("\nMetric types available for 'orders-db':")
    print(sorted(df[df["service"] == "orders-db"]["metric_type"].unique()))

    print("\nFull per-(service, metric) anomaly scores, showing orders/orders-db rows:")
    scores_df = score_case(CASE)
    print(scores_df[scores_df["service"].isin(["orders", "orders-db"])].to_string(index=False))

    print("\nTop 10 overall (for context):")
    print(scores_df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
