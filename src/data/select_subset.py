"""
Phase 2, Step 5: Pick a small, diverse subset of RE2-SS cases
before downloading any telemetry.
"""

import pandas as pd
from explore_dataset import load_case_index


def main():
    index = load_case_index()

    re2_ss = index[index["dataset"] == "RE2-SS"].copy()
    print(f"Total RE2-SS cases available: {len(re2_ss)}")

    # Take up to 5 cases per fault type, preferring smaller log volumes
    re2_ss_sorted = re2_ss.sort_values(["fault", "n_logs", "n_traces"])
    selected = re2_ss_sorted.groupby("fault").head(5).reset_index(drop=True)

    cols = ["case", "fault", "root_cause_service", "n_metrics",
            "n_logs", "n_traces", "duration_minutes", "has_root_cause_file"]
    print(f"\nSelected subset ({len(selected)} cases, up to 5 per fault type):")
    print(selected[cols].to_string(index=False))

    total_logs = selected["n_logs"].sum()
    print(f"\nTotal logs across selected cases: {total_logs:,}")

    out_path = "data/processed/selected_cases_expanded.csv"
    selected[cols].to_csv(out_path, index=False)
    print(f"\nSaved expanded selection to {out_path}")


if __name__ == "__main__":
    main()
