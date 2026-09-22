"""
Phase 5, Step 2: Check whether error/exception keywords in logs
are actually concentrated in the faulty phase (not just present
somewhere in the file).
"""

import pandas as pd

CASE = "re2ss_orders_disk_1"
SERVICE = "orders"
KEYWORDS = ["error", "exception", "timeout"]


def main():
    df = pd.read_parquet(f"data/processed/{CASE}/logs_labeled.parquet")
    sub = df[df["service"] == SERVICE].copy()

    # Extract the log level token (e.g. INFO, WARN, ERROR) if present
    sub["level"] = sub["message"].str.extract(r"\s+(INFO|WARN|ERROR|DEBUG)\s+")

    print("Log level counts by phase:")
    print(sub.groupby(["phase", "level"]).size().unstack(fill_value=0))

    # Phase durations in seconds, from the actual timestamp range per phase
    durations = sub.groupby("phase")["seconds_from_injection"].agg(lambda x: x.max() - x.min())
    print("\nPhase span (seconds), for rate normalization:")
    print(durations)

    print("\nKeyword counts AND rate-per-minute, by phase:")
    for kw in KEYWORDS:
        matches = sub[sub["message"].str.contains(kw, case=False, na=False)]
        counts = matches.groupby("phase").size()
        for phase in ["normal", "faulty"]:
            n = counts.get(phase, 0)
            span_sec = durations.get(phase, None)
            rate = (n / span_sec * 60) if span_sec else None
            print(f"  '{kw}' | phase={phase}: count={n}, rate/min={rate}")

    print("\nSample exception message (if any):")
    exc = sub[sub["message"].str.contains("exception", case=False, na=False)]
    if len(exc) > 0:
        print(exc.iloc[0]["message"][:400])
        print(f"...(phase of this line: {exc.iloc[0]['phase']})")


if __name__ == "__main__":
    main()
