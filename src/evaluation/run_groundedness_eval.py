"""
Phase 9, Step 2: Run groundedness scoring across all 6 pilot cases
for both the grounded agent and the ungrounded baseline.
"""

import sys, os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "reasoning"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "anomaly_detection"))
from evidence_package import build_evidence_package
from reasoning_agent import run_reasoning
from ungrounded_baseline import run_ungrounded
from baseline_b0 import score_case, rank_services
from groundedness import score_grounded, score_ungrounded

ALL_SERVICES = ["front-end", "orders", "orders-db", "carts", "carts-db",
                "catalogue", "catalogue-db", "user", "user-db", "payment",
                "shipping", "queue-master", "rabbitmq", "rabbitmq-exporter",
                "session-db"]


def main():
    selected = pd.read_csv("data/processed/selected_cases.csv")
    records = []

    for _, row in selected.iterrows():
        case_name = row["case"]
        truth = row["root_cause_service"]

        # Grounded agent
        package, _ = build_evidence_package(case_name, truth)
        grounded_result = run_reasoning(package)
        grounded_score = score_grounded(grounded_result.get("explanation", ""), package)

        # Ungrounded agent
        b0_top1 = rank_services(score_case(case_name)).iloc[0]["service"]
        ungrounded_result = run_ungrounded(
            case_name, "Sock Shop", ALL_SERVICES, b0_top1,
            "elevated response times and abnormal resource usage reported by monitoring"
        )
        ungrounded_score = score_ungrounded(ungrounded_result.get("explanation", ""))

        records.append({
            "case": case_name,
            "grounded_claimed": grounded_score["claimed_count"],
            "grounded_traceable": grounded_score.get("grounded_count", 0),
            "grounded_groundedness_score": grounded_score["groundedness_score"],
            "ungrounded_claimed": ungrounded_score["claimed_count"],
            "ungrounded_fabricated": ungrounded_score["fabricated_count"],
            "ungrounded_groundedness_score": ungrounded_score["groundedness_score"],
        })

    df = pd.DataFrame(records)
    out_path = "data/processed/phase9_groundedness_results.csv"
    df.to_csv(out_path, index=False)

    print(df.to_string(index=False))
    print(f"\nSaved to {out_path}")

    valid_grounded = df["grounded_groundedness_score"].dropna()
    print(f"\nAvg grounded agent groundedness: {valid_grounded.mean():.2f} "
          f"(over {len(valid_grounded)}/{len(df)} cases that cited specific numbers)")
    print(f"Avg ungrounded agent groundedness: {df['ungrounded_groundedness_score'].mean():.2f}")
    print(f"Total fabricated numeric claims (ungrounded): {df['ungrounded_fabricated'].sum()}")


if __name__ == "__main__":
    main()
