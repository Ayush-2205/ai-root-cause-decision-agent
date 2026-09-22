"""
Phase 5, Step 3: Generic log-based anomaly score per service.

For each service, compute the rate (per minute) of WARN/ERROR level
lines plus generic failure keywords, separately for normal and
faulty phases, and score the increase.
"""

import pandas as pd
import numpy as np

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.config import DATA_DIR as PROCESSED_DIR

FAILURE_KEYWORDS = ["error", "exception", "timeout", "fail", "refused", "unavailable"]


def score_logs_for_case(case_name: str) -> pd.DataFrame:
    df = pd.read_parquet(f"{PROCESSED_DIR}/{case_name}/logs_labeled.parquet")

    # A line counts as "bad" if it's WARN/ERROR level OR contains a failure keyword
    level = df["message"].str.extract(r"\s+(INFO|WARN|ERROR|DEBUG)\s+")[0]
    is_bad_level = level.isin(["WARN", "ERROR"])
    is_bad_keyword = df["message"].str.contains("|".join(FAILURE_KEYWORDS), case=False, na=False)
    df["is_bad"] = is_bad_level | is_bad_keyword

    results = []
    for service, group in df.groupby("service"):
        durations = group.groupby("phase")["seconds_from_injection"].agg(lambda x: x.max() - x.min())
        bad_counts = group[group["is_bad"]].groupby("phase").size()

        normal_span = durations.get("normal", 0)
        faulty_span = durations.get("faulty", 0)
        if normal_span <= 0 or faulty_span <= 0:
            continue

        normal_rate = bad_counts.get("normal", 0) / normal_span * 60
        faulty_rate = bad_counts.get("faulty", 0) / faulty_span * 60

        # Simple, explainable score: how much did the bad-line rate increase.
        # +0.01 avoids div-by-zero while barely affecting real signals.
        log_score = (faulty_rate - normal_rate) / (normal_rate + 0.01)
        log_score = max(log_score, 0)  # a decrease isn't "anomalous" for our purposes

        results.append({
            "service": service,
            "normal_rate_per_min": round(normal_rate, 3),
            "faulty_rate_per_min": round(faulty_rate, 3),
            "log_score": round(log_score, 3),
        })

    return pd.DataFrame(results).sort_values("log_score", ascending=False).reset_index(drop=True)


def main():
    selected = pd.read_csv(f"{PROCESSED_DIR}/selected_cases.csv")

    for _, row in selected.iterrows():
        case_name = row["case"]
        true_root_cause = row["root_cause_service"]

        log_scores = score_logs_for_case(case_name)
        top1 = log_scores.iloc[0]["service"] if len(log_scores) else None
        top3 = log_scores.head(3)["service"].tolist()

        hit1 = "HIT" if top1 == true_root_cause else "miss"
        hit3 = "HIT" if true_root_cause in top3 else "miss"

        print(f"\n{case_name}  (true root cause: {true_root_cause})")
        print(log_scores.head(5).to_string(index=False))
        print(f"Top-1: {hit1}  |  Top-3: {hit3}")


if __name__ == "__main__":
    main()
