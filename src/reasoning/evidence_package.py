"""
Phase 7, Step 2: Build a structured evidence package for one case,
combining Phase 6's ranked candidates with the REAL supporting log
lines behind any corroboration score - not just the numeric score.
"""

import sys
import os
import json
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "root_cause"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "anomaly_detection"))
from combined_score import combined_rank_for_case
from dependencies import get_downstream_dependencies

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.config import DATA_DIR as PROCESSED_DIR

FAILURE_KEYWORDS = ["error", "exception", "timeout", "fail", "refused", "unavailable"]


def get_supporting_log_lines(case_name: str, service: str, max_lines: int = 3) -> list:
    """Pull the REAL faulty-phase log lines (WARN/ERROR/keyword-matched)
    for a service and its downstream dependencies - the actual text
    the LLM will be grounded in, not just a score."""
    logs = pd.read_parquet(f"{PROCESSED_DIR}/{case_name}/logs_labeled.parquet")

    related = get_downstream_dependencies(service)
    subset = logs[logs["service"].isin(related) & (logs["phase"] == "faulty")]

    level = subset["message"].str.extract(r"\s+(INFO|WARN|ERROR|DEBUG)\s+")[0]
    is_bad_level = level.isin(["WARN", "ERROR"])
    is_bad_keyword = subset["message"].str.contains("|".join(FAILURE_KEYWORDS), case=False, na=False)
    bad_lines = subset[is_bad_level | is_bad_keyword]

    samples = bad_lines.head(max_lines)
    return [
        {"service": row["service"], "message": row["message"][:300]}
        for _, row in samples.iterrows()
    ]


def build_evidence_package(case_name: str, true_root_cause_for_metadata_only: str = None) -> dict:
    """Build the full evidence package. true_root_cause_for_metadata_only
    is stored SEPARATELY and never included in what we hand to the LLM -
    it's only for our own later scoring of the LLM's answer."""
    ranked = combined_rank_for_case(case_name)

    candidates = []
    for _, row in ranked.head(5).iterrows():
        candidates.append({
            "service": row["service"],
            "metric_anomaly_score": round(float(row["anomaly_score"]), 2),
            "log_corroboration_score": round(float(row["log_corroboration"]), 2),
            "combined_score": round(float(row["combined_score"]), 4),
                        "supporting_log_lines": (
                get_supporting_log_lines(case_name, row["service"])
                if row["log_corroboration"] > 0 else []
            ),
        })

    package = {
        "case_id": case_name,
        "ranked_candidates": candidates,
        "top_candidate": candidates[0]["service"] if candidates else None,
    }

    # Kept separate, NOT part of what's sent to the LLM
    ground_truth = {"true_root_cause": true_root_cause_for_metadata_only}

    return package, ground_truth


def main():
    selected = pd.read_csv(f"{PROCESSED_DIR}/selected_cases.csv")
    row = selected.iloc[0]  # start with just one case: re2ss_catalogue_cpu_2

    package, ground_truth = build_evidence_package(row["case"], row["root_cause_service"])

    print(json.dumps(package, indent=2))
    print(f"\n(Ground truth, kept separate, NOT sent to LLM: {ground_truth})")


if __name__ == "__main__":
    main()
