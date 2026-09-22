"""
Phase 11, Step 4: Full evaluation across all 30 expanded cases -
B0, Combined, and Grounded LLM agent top-1/top-3 accuracy.
"""

import sys, os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "root_cause"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "anomaly_detection"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "reasoning"))
from baseline_b0 import score_case, rank_services
from combined_score import combined_rank_for_case
from evidence_package import build_evidence_package
from reasoning_agent import run_reasoning


def main():
    selected = pd.read_csv("data/processed/selected_cases_expanded.csv")
    records = []

    for i, row in selected.iterrows():
        case_name = row["case"]
        truth = row["root_cause_service"]
        print(f"[{i+1}/{len(selected)}] Processing {case_name}...")

        try:
            b0_ranked = rank_services(score_case(case_name))
            b0_top1 = b0_ranked.iloc[0]["service"]
            b0_top3 = b0_ranked.head(3)["service"].tolist()

            combined = combined_rank_for_case(case_name)
            combined_top1 = combined.iloc[0]["service"]
            combined_top3 = combined.head(3)["service"].tolist()

            package, _ = build_evidence_package(case_name, truth)
            llm_result = run_reasoning(package)
            llm_top1 = llm_result.get("root_cause_service")
            llm_confidence = llm_result.get("confidence")

            records.append({
                "case": case_name,
                "fault": row["fault"],
                "true_root_cause": truth,
                "b0_top1": b0_top1,
                "b0_top1_hit": b0_top1 == truth,
                "b0_top3_hit": truth in b0_top3,
                "combined_top1": combined_top1,
                "combined_top1_hit": combined_top1 == truth,
                "combined_top3_hit": truth in combined_top3,
                "llm_top1": llm_top1,
                "llm_top1_hit": llm_top1 == truth,
                "llm_confidence": llm_confidence,
            })
        except Exception as e:
            print(f"  ERROR on {case_name}: {e}")
            records.append({"case": case_name, "fault": row["fault"],
                             "true_root_cause": truth, "error": str(e)})

    df = pd.DataFrame(records)
    out_path = "data/processed/phase11_full_results.csv"
    df.to_csv(out_path, index=False)

    print("\n" + "=" * 70)
    print(df.to_string(index=False))

    n = len(df[df["error"].isna()]) if "error" in df.columns else len(df)
    print(f"\n=== SUMMARY over {n} successfully-processed cases ===")
    print(f"B0 (metrics only):        Top-1 {df['b0_top1_hit'].sum()}/{n}   Top-3 {df['b0_top3_hit'].sum()}/{n}")
    print(f"Combined (metrics+logs):  Top-1 {df['combined_top1_hit'].sum()}/{n}   Top-3 {df['combined_top3_hit'].sum()}/{n}")
    print(f"Grounded LLM:             Top-1 {df['llm_top1_hit'].sum()}/{n}")

    print("\n--- Breakdown by fault type ---")
    print(df.groupby("fault")[["b0_top1_hit", "combined_top1_hit", "llm_top1_hit"]].mean().round(2))

    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
