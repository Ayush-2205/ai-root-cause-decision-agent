"""
Phase 2, Step 7: Preview one downloaded case's metrics, logs, and
injection time before we write any preprocessing logic.
"""

import pandas as pd

CASE_DIR = "data/raw/re2ss_catalogue_cpu_2"


def preview_metrics():
    print("=" * 60)
    print("METRICS")
    print("=" * 60)
    df = pd.read_parquet(f"{CASE_DIR}/metrics.parquet")
    print(f"Shape: {df.shape}")
    print(f"\nColumns ({len(df.columns)} total, showing first 15):")
    print(list(df.columns)[:15])
    print("\nDtypes (first 10 columns):")
    print(df.dtypes.head(10))
    print("\nHead:")
    print(df.head())


def preview_logs():
    print("\n" + "=" * 60)
    print("LOGS")
    print("=" * 60)
    df = pd.read_parquet(f"{CASE_DIR}/logs.parquet")
    print(f"Shape: {df.shape}")
    print(f"\nColumns:")
    print(list(df.columns))
    print("\nDtypes:")
    print(df.dtypes)
    print("\nHead:")
    print(df.head())


def preview_inject_time():
    print("\n" + "=" * 60)
    print("INJECT TIME")
    print("=" * 60)
    with open(f"{CASE_DIR}/inject_time.txt") as f:
        content = f.read().strip()
    print(f"Raw content: {content}")


if __name__ == "__main__":
    preview_metrics()
    preview_logs()
    preview_inject_time()
