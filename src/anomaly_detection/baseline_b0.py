"""
Phase 4: Baseline B0 - metrics-only anomaly detection and
root-cause ranking using robust z-scores.

For each (service, metric_type), compare the faulty-phase values
against the normal-phase distribution. Rank services by their
strongest anomaly score.
"""

import pandas as pd
import numpy as np

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.config import DATA_DIR as PROCESSED_DIR


def robust_zscore(faulty_values: np.ndarray, normal_values: np.ndarray) -> float:
    """Median-based z-score: how many MADs is the faulty median
    away from the normal median. Returns 0 if normal data has no
    spread (avoids divide-by-zero)."""
    normal_median = np.median(normal_values)
    mad = np.median(np.abs(normal_values - normal_median))

    if mad == 0:
        return 0.0

    faulty_median = np.median(faulty_values)
    # 1.4826 makes MAD comparable to standard deviation for normal-ish data
    score = abs(faulty_median - normal_median) / (1.4826 * mad)
    return score


def score_case(case_name: str) -> pd.DataFrame:
    """Return a DataFrame of (service, metric_type, anomaly_score)
    for one case, sorted by score descending."""
    df = pd.read_parquet(f"{PROCESSED_DIR}/{case_name}/metrics_long.parquet")

    results = []
    for (service, metric_type), group in df.groupby(["service", "metric_type"]):
        normal_vals = group.loc[group["phase"] == "normal", "value"].to_numpy()
        faulty_vals = group.loc[group["phase"] == "faulty", "value"].to_numpy()

        if len(normal_vals) < 5 or len(faulty_vals) < 5:
            continue  # not enough data to trust a score

        score = robust_zscore(faulty_vals, normal_vals)
        results.append({"service": service, "metric_type": metric_type, "anomaly_score": score})

    scores_df = pd.DataFrame(results).sort_values("anomaly_score", ascending=False)
    return scores_df.reset_index(drop=True)


def rank_services(scores_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate per-metric scores into a per-service ranking by
    taking each service's MAX anomaly score across its metrics."""
    ranked = (
        scores_df.groupby("service")["anomaly_score"]
        .max()
        .reset_index()
        .sort_values("anomaly_score", ascending=False)
        .reset_index(drop=True)
    )
    ranked["rank"] = ranked.index + 1
    return ranked


def main():
    selected = pd.read_csv(f"{PROCESSED_DIR}/selected_cases.csv")

    for _, row in selected.iterrows():
        case_name = row["case"]
        true_root_cause = row["root_cause_service"]

        scores_df = score_case(case_name)
        ranked = rank_services(scores_df)

        top1 = ranked.iloc[0]["service"]
        top3 = ranked.head(3)["service"].tolist()

        hit1 = "HIT" if top1 == true_root_cause else "miss"
        hit3 = "HIT" if true_root_cause in top3 else "miss"

        print(f"\n{case_name}  (true root cause: {true_root_cause})")
        print(ranked.head(5).to_string(index=False))
        print(f"Top-1: {hit1}  |  Top-3: {hit3}")


if __name__ == "__main__":
    main()
