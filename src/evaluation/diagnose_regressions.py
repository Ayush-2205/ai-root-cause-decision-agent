"""
Phase 11, Step 5: Diagnose the 3 cases where B0 was correct but
Combined (metrics+logs) flipped to a wrong answer, at n=30.
"""

import sys, os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "root_cause"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "anomaly_detection"))
from combined_score import combined_rank_for_case

REGRESSED_CASES = ["re2ss_catalogue_cpu_1", "re2ss_user_socket_2", "re2ss_carts_socket_3"]

selected = pd.read_csv("data/processed/selected_cases_expanded.csv")

for case_name in REGRESSED_CASES:
    truth = selected[selected["case"] == case_name]["root_cause_service"].values[0]
    print(f"\n{'=' * 60}\n{case_name}  (true root cause: {truth})\n{'=' * 60}")
    ranked = combined_rank_for_case(case_name)
    print(ranked[["service", "anomaly_score", "log_corroboration", "combined_score"]].to_string(index=False))
