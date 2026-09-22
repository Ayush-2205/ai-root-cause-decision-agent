"""
Phase 3, Step 2: Reshape metrics to long format, align logs, and
label both with time-since-injection and normal/faulty phase.
"""

import os
import pandas as pd

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"


def load_inject_time(case_dir: str) -> int:
    with open(f"{case_dir}/inject_time.txt") as f:
        return int(f.read().strip())


def reshape_metrics_long(metrics_wide: pd.DataFrame) -> pd.DataFrame:
    """Melt wide metrics (time, carts_cpu, carts_mem, ...) into
    long format: time, service, metric_type, value."""
    long_df = metrics_wide.melt(id_vars="time", var_name="column", value_name="value")

    # Split "carts-db_cpu" -> service="carts-db", metric_type="cpu"
    # rpartition splits on the LAST underscore, confirmed safe in Step 1
    split = long_df["column"].str.rpartition("_")
    long_df["service"] = split[0]
    long_df["metric_type"] = split[2]
    long_df = long_df.drop(columns=["column"])

    # Drop rows where this service/metric_type combo doesn't apply
    # (e.g. "diskio" doesn't exist for every service -> all-NaN column)
    long_df = long_df.dropna(subset=["value"]).reset_index(drop=True)

    return long_df[["time", "service", "metric_type", "value"]]


def add_phase_labels(df: pd.DataFrame, time_col: str, inject_time: int) -> pd.DataFrame:
    """Add seconds_from_injection and phase ('normal'/'faulty')."""
    df = df.copy()
    df["seconds_from_injection"] = df[time_col] - inject_time
    df["phase"] = df["seconds_from_injection"].apply(
        lambda s: "faulty" if s >= 0 else "normal"
    )
    return df


def process_case(case_name: str) -> None:
    case_dir = f"{RAW_DIR}/{case_name}"
    out_dir = f"{PROCESSED_DIR}/{case_name}"
    os.makedirs(out_dir, exist_ok=True)

    inject_time = load_inject_time(case_dir)

    # --- Metrics ---
    metrics_wide = pd.read_parquet(f"{case_dir}/metrics.parquet")
    metrics_long = reshape_metrics_long(metrics_wide)
    metrics_long = add_phase_labels(metrics_long, "time", inject_time)
    metrics_long.to_parquet(f"{out_dir}/metrics_long.parquet", index=False)

    # --- Logs ---
    logs = pd.read_parquet(f"{case_dir}/logs.parquet")
    logs = logs.rename(columns={"container_name": "service"})
    logs = add_phase_labels(logs, "timestamp", inject_time)
    logs.to_parquet(f"{out_dir}/logs_labeled.parquet", index=False)

    n_normal_m = (metrics_long["phase"] == "normal").sum()
    n_faulty_m = (metrics_long["phase"] == "faulty").sum()
    n_normal_l = (logs["phase"] == "normal").sum()
    n_faulty_l = (logs["phase"] == "faulty").sum()

    print(f"{case_name}: metrics rows={len(metrics_long)} "
          f"(normal={n_normal_m}, faulty={n_faulty_m}) | "
          f"logs rows={len(logs)} (normal={n_normal_l}, faulty={n_faulty_l})")


def main():
    selected = pd.read_csv("data/processed/selected_cases_expanded.csv")
    for case_name in selected["case"]:
        process_case(case_name)


if __name__ == "__main__":
    main()
