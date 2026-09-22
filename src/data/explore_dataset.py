"""
Phase 2, Step 1: Download and inspect the RCAEval case index.

This does NOT download any telemetry data yet — just the small
index file that lists all 735 cases and their ground-truth labels.
"""

import pandas as pd

def load_case_index() -> pd.DataFrame:
    """Load the RCAEval case index directly from Hugging Face."""
    url = "hf://datasets/phamquiluan/RCAEval/cases.parquet"
    df = pd.read_parquet(url)
    return df


if __name__ == "__main__":
    index = load_case_index()

    print(f"Total cases in RCAEval: {len(index)}")
    print("\nColumns available:")
    print(list(index.columns))

    print("\nDatasets (suites) available:")
    print(index["dataset"].unique())

    print("\nSample rows:")
    print(index.head(10))