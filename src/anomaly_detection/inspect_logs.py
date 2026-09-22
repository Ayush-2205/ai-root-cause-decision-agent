"""
Phase 5, Step 1: Inspect raw log message content before designing
a log-based anomaly signal.
"""

import pandas as pd

CASE = "re2ss_orders_disk_1"
SERVICE = "orders"


def main():
    df = pd.read_parquet(f"data/processed/{CASE}/logs_labeled.parquet")
    sub = df[df["service"] == SERVICE].sort_values("timestamp")

    print(f"Total log lines for '{SERVICE}': {len(sub)}")

    print("\n--- 5 sample NORMAL-phase messages ---")
    for msg in sub[sub["phase"] == "normal"]["message"].head(5):
        print(msg)

    print("\n--- 5 sample FAULTY-phase messages ---")
    for msg in sub[sub["phase"] == "faulty"]["message"].head(5):
        print(msg)

    # Look for common keywords that might indicate severity/status
    print("\n--- Keyword presence check (case-insensitive) ---")
    for keyword in ["error", "level=", "exception", "status=5", "status=4", "timeout", "fail"]:
        count = sub["message"].str.contains(keyword, case=False, na=False).sum()
        print(f"'{keyword}': {count} lines")

    print("\n--- Log line counts: normal vs faulty (raw, not yet rate-normalized) ---")
    print(sub["phase"].value_counts())


if __name__ == "__main__":
    main()
