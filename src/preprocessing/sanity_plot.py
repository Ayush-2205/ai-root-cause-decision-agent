"""
Phase 3, Step 3: Visual sanity check - does the fault show up
in the CPU metric of the actual root-cause service?
"""

import pandas as pd
import matplotlib.pyplot as plt

CASE = "re2ss_catalogue_cpu_2"
ROOT_CAUSE_SERVICE = "catalogue"
HEALTHY_SERVICE = "front-end"
METRIC = "cpu"


def main():
    df = pd.read_parquet(f"data/processed/{CASE}/metrics_long.parquet")

    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    for ax, service in zip(axes, [ROOT_CAUSE_SERVICE, HEALTHY_SERVICE]):
        sub = df[(df["service"] == service) & (df["metric_type"] == METRIC)]
        sub = sub.sort_values("seconds_from_injection")

        normal = sub[sub["phase"] == "normal"]
        faulty = sub[sub["phase"] == "faulty"]

        ax.plot(normal["seconds_from_injection"], normal["value"],
                color="steelblue", label="normal")
        ax.plot(faulty["seconds_from_injection"], faulty["value"],
                color="crimson", label="faulty")
        ax.axvline(0, color="black", linestyle="--", linewidth=1, label="injection point")
        ax.set_title(f"{service} — {METRIC}")
        ax.set_ylabel(METRIC)
        ax.legend(loc="upper left", fontsize=8)

    axes[-1].set_xlabel("Seconds from injection")
    plt.tight_layout()

    out_path = "data/processed/sanity_check_plot.png"
    plt.savefig(out_path, dpi=120)
    print(f"Saved plot to {out_path}")


if __name__ == "__main__":
    main()
