"""
Phase 7, Step 6: Consolidate B0, Combined, Grounded-LLM, and
Ungrounded-LLM results into one saved comparison table.
"""

import sys, os, json
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "root_cause"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "anomaly_detection"))
from baseline_b0 import score_case, rank_services
from combined_score import combined_rank_for_case
from evidence_package import build_evidence_package
from reasoning_agent import run_reasoning
from ungrounded_baseline import run_ungrounded

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

        b0_top1 = rank_services(score_case(case_name)).iloc[0]["service"]
        combined_top1 = combined_rank_for_case(case_name).iloc[0]["service"]

        package, _ = build_evidence_package(case_name, truth)
        grounded_result = run_reasoning(package)
        grounded_top1 = grounded_result.get("root_cause_service")

        ungrounded_result = run_ungrounded(
            case_name, "Sock Shop", ALL_SERVICES, b0_top1,
            "elevated response times and abnormal resource usage reported by monitoring"
        )
        ungrounded_top1 = ungrounded_result.get("root_cause_service")

        records.append({
            "case": case_name,
            "true_root_cause": truth,
            "alert_fired_on": b0_top1,
            "b0_top1": b0_top1,
            "b0_hit": b0_top1 == truth,
            "combined_top1": combined_top1,
            "combined_hit": combined_top1 == truth,
            "grounded_llm_top1": grounded_top1,
            "grounded_llm_hit": grounded_top1 == truth,
            "grounded_confidence": grounded_result.get("confidence"),
            "ungrounded_llm_top1": ungrounded_top1,
            "ungrounded_llm_hit": ungrounded_top1 == truth,
        })

    df = pd.DataFrame(records)
    out_path = "data/processed/phase7_results.csv"
    df.to_csv(out_path, index=False)

    print(df.to_string(index=False))
    print(f"\nSaved to {out_path}")
    print(f"\nn = {len(df)} cases (small pilot set - not statistically conclusive)")
    print(f"B0 hits: {df['b0_hit'].sum()}/{len(df)}")
    print(f"Combined hits: {df['combined_hit'].sum()}/{len(df)}")
    print(f"Grounded LLM hits: {df['grounded_llm_hit'].sum()}/{len(df)}")
    print(f"Ungrounded LLM hits: {df['ungrounded_llm_hit'].sum()}/{len(df)}")


if __name__ == "__main__":
    main()
