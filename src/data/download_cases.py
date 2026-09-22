"""
Phase 2, Step 6: Download only the selected case folders from RCAEval.
"""

import pandas as pd
from huggingface_hub import snapshot_download


def main():
    selected = pd.read_csv("data/processed/selected_cases_expanded.csv")
    case_names = selected["case"].tolist()
    print(f"Cases to download: {len(case_names)}")

    patterns = [f"{case}/**" for case in case_names]

    local_path = snapshot_download(
        repo_id="phamquiluan/RCAEval",
        repo_type="dataset",
        allow_patterns=patterns,
        local_dir="data/raw",
    )

    print(f"\nDownload complete. Files saved under: {local_path}")


if __name__ == "__main__":
    main()
