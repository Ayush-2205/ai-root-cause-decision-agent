"""
Phase 6, Step 4: Save the B0 vs Combined comparison as a permanent
record - this is real evaluation data for our paper, not to be
regenerated differently later without noting the change.
"""

import pandas as pd
from combined_score import combined_rank_for_case
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "anomaly_detection"))
from baseline_b0 import score_case, rank_services


def main():
    selected = pd.read_csv("data/processed/selected_cases.csv")
    records = []

    for _, row in selected.iterrows():
        case_name = row["case"]
        true_root_cause = row["root_cause_service"]

        b0_full = rank_services(score_case(case_name))
        combined = combined_rank_for_case(case_name)

        records.append({
            "case": case_name,
            "fault": row["fault"],
            "true_root_cause": true_root_cause,
            "b0_top1": b0_full.iloc[0]["service"],
            "b0_top1_hit": b0_full.iloc[0]["service"] == true_root_cause,
            "b0_top3_hit": true_root_cause in b0_full.head(3)["service"].tolist(),
            "combined_top1": combined.iloc[0]["service"],
            "combined_top1_hit": combined.iloc[0]["service"] == true_root_cause,
            "combined_top3_hit": true_root_cause in combined.head(3)["service"].tolist(),
        })

    results_df = pd.DataFrame(records)
    out_path = "data/processed/phase6_results.csv"
    results_df.to_csv(out_path, index=False)
    print(results_df.to_string(index=False))
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
