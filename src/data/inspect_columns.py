"""
Phase 3, Step 1: Verify the service/metric-type naming pattern
holds across ALL metric columns before we write parsing logic.
"""

import pandas as pd

CASE_DIR = "data/raw/re2ss_catalogue_cpu_2"


def main():
    df = pd.read_parquet(f"{CASE_DIR}/metrics.parquet")
    metric_cols = [c for c in df.columns if c != "time"]

    print(f"Total metric columns: {len(metric_cols)}")

    parsed = []
    for col in metric_cols:
        service, _, metric_type = col.rpartition("_")
        parsed.append((col, service, metric_type))

    parsed_df = pd.DataFrame(parsed, columns=["column", "service", "metric_type"])

    print("\nUnique services found:")
    print(sorted(parsed_df["service"].unique()))

    print("\nUnique metric types found:")
    print(sorted(parsed_df["metric_type"].unique()))

    # Flag anything that looks wrong (empty service or metric_type)
    bad = parsed_df[(parsed_df["service"] == "") | (parsed_df["metric_type"] == "")]
    print(f"\nRows where parsing looks broken: {len(bad)}")
    if len(bad) > 0:
        print(bad)

    print("\nFull parsed table:")
    print(parsed_df.to_string(index=False))


if __name__ == "__main__":
    main()
