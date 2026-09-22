"""
Phase 6, Step 2: Combine metrics-based candidates (B0) with
corroborating log evidence from related services, restricted to
the metrics top-5 shortlist.
"""

import sys
import os
import pandas as pd

from dependencies import get_downstream_dependencies  # instead of get_related_services

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "anomaly_detection"))

from baseline_b0 import score_case, rank_services
from log_signal import score_logs_for_case

from dependencies import get_related_services

METRICS_WEIGHT = 0.7
LOG_WEIGHT = 0.3
SHORTLIST_SIZE = 8


def combined_rank_for_case(case_name: str) -> pd.DataFrame:
    metrics_scores = score_case(case_name)
    metrics_ranked = rank_services(metrics_scores).head(SHORTLIST_SIZE).copy()

    log_scores = score_logs_for_case(case_name)
    log_lookup = dict(zip(log_scores["service"], log_scores["log_score"]))

    corroboration = []

    for svc in metrics_ranked["service"]:
        related = get_downstream_dependencies(svc)
        related_log_scores = [log_lookup.get(r, 0.0) for r in related]
        corroboration.append(
            max(related_log_scores) if related_log_scores else 0.0
        )

    metrics_ranked["log_corroboration"] = corroboration

    def normalize(col):
        rng = col.max() - col.min()
        return (col - col.min()) / rng if rng > 0 else col * 0

    metrics_ranked["norm_metrics"] = normalize(metrics_ranked["anomaly_score"])
    metrics_ranked["norm_log"] = normalize(metrics_ranked["log_corroboration"])

    # PENALTY-BASED combination instead of pure addition:
    # a metric anomaly with NO meaningful corroborating log evidence
    # gets discounted, not just left un-boosted.
    NO_CORROBORATION_PENALTY = 0.5
    MIN_MEANINGFUL_CORROBORATION = 5.0

    def combine(row):
        if row["log_corroboration"] < MIN_MEANINGFUL_CORROBORATION:
            return row["norm_metrics"] * NO_CORROBORATION_PENALTY
        return 0.7 * row["norm_metrics"] + 0.3 * row["norm_log"]

    metrics_ranked["combined_score"] = metrics_ranked.apply(combine, axis=1)

    return metrics_ranked.sort_values(
        "combined_score",
        ascending=False
    ).reset_index(drop=True)


def main():
    selected = pd.read_csv("data/processed/selected_cases.csv")

    b0_hits1, combined_hits1 = 0, 0
    b0_hits3, combined_hits3 = 0, 0

    for _, row in selected.iterrows():
        case_name = row["case"]
        true_root_cause = row["root_cause_service"]

        combined = combined_rank_for_case(case_name)

        top1 = combined.iloc[0]["service"]
        top3 = combined.head(3)["service"].tolist()

        # Recompute plain B0 top1/top3 for side-by-side comparison
        b0_full = rank_services(score_case(case_name))

        true_rank_row = b0_full[
            b0_full["service"] == true_root_cause
        ]

        true_rank = (
            true_rank_row["rank"].values[0]
            if len(true_rank_row)
            else "not found"
        )

        print(
            f"  (true root cause '{true_root_cause}' "
            f"full metrics rank: {true_rank})"
        )

        b0_top1 = b0_full.iloc[0]["service"]
        b0_top3 = b0_full.head(3)["service"].tolist()

        b0_hits1 += (b0_top1 == true_root_cause)
        combined_hits1 += (top1 == true_root_cause)

        b0_hits3 += (true_root_cause in b0_top3)
        combined_hits3 += (true_root_cause in top3)

        print(
            f"\n{case_name}  (true root cause: {true_root_cause})"
        )

        print(
            combined[
                [
                    "service",
                    "anomaly_score",
                    "log_corroboration",
                    "combined_score",
                ]
            ].to_string(index=False)
        )

        print(
            f"B0 top-1: {b0_top1} "
            f"({'HIT' if b0_top1 == true_root_cause else 'miss'})  |  "
            f"Combined top-1: {top1} "
            f"({'HIT' if top1 == true_root_cause else 'miss'})"
        )

    n = len(selected)

    print(f"\n=== SUMMARY over {n} cases ===")
    print(
        f"B0 (metrics only):        "
        f"Top-1 {b0_hits1}/{n}   Top-3 {b0_hits3}/{n}"
    )
    print(
        f"Combined (metrics+logs):  "
        f"Top-1 {combined_hits1}/{n}   Top-3 {combined_hits3}/{n}"
    )


if __name__ == "__main__":
    main()
