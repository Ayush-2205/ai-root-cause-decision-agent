"""
Phase 9, Step 1: Automated groundedness scoring.

Grounded agent: every number in its explanation should trace back
to a number literally present in the evidence package it was given.

Ungrounded agent: it was given NO numbers at all, so any number it
states is necessarily invented.
"""

import re
import json


def extract_numbers(text: str) -> list:
    """Pull out decimal/integer numbers from free text."""
    matches = re.findall(r"-?\d+\.?\d*", text)
    return [float(m) for m in matches if m not in ("", "-", ".")]


def numbers_in_package(package: dict) -> set:
    """Collect every numeric value actually present in the evidence
    package (rounded to 2dp, matching how we formatted it)."""
    nums = set()

    for c in package.get("ranked_candidates", []):
        for key in ["metric_anomaly_score", "log_corroboration_score", "combined_score"]:
            if key in c:
                nums.add(round(float(c[key]), 2))

    return nums


def score_grounded(explanation: str, package: dict, tolerance: float = 0.05) -> dict:
    claimed_numbers = extract_numbers(explanation)
    evidence_numbers = numbers_in_package(package)

    # Ignore tiny/common numbers (like "2" or "4" service counts) that
    # aren't really "evidence claims" - focus on decimal scores, which
    # are the actual evidence values in our system.
    decimal_claims = [n for n in claimed_numbers if n != int(n)]

    if not decimal_claims:
        return {
            "claimed_count": 0,
            "grounded_count": 0,
            "groundedness_score": None,
            "note": "No specific decimal evidence values cited.",
        }

    grounded = 0

    for n in decimal_claims:
        if any(abs(n - e) <= tolerance for e in evidence_numbers):
            grounded += 1

    return {
        "claimed_count": len(decimal_claims),
        "grounded_count": grounded,
        "groundedness_score": round(grounded / len(decimal_claims), 2),
        "note": "OK" if grounded == len(decimal_claims) else "Some claims not traceable to evidence",
    }


def strip_quoted_log_text(text: str) -> str:
    """Remove anything inside double quotes - this is where raw log
    line content gets quoted, and can legitimately contain IPs/ports/
    numbers that have nothing to do with our evidence scores."""
    return re.sub(r'"[^"]*"', "", text)


def score_grounded(explanation: str, package: dict, tolerance: float = 0.05) -> dict:
    cleaned_text = strip_quoted_log_text(explanation)

    claimed_numbers = extract_numbers(cleaned_text)
    evidence_numbers = numbers_in_package(package)

    decimal_claims = [n for n in claimed_numbers if n != int(n)]

    if not decimal_claims:
        return {
            "claimed_count": 0,
            "grounded_count": 0,
            "groundedness_score": None,
            "note": "No specific decimal evidence values cited.",
        }

    grounded = 0

    for n in decimal_claims:
        if any(abs(n - e) <= tolerance for e in evidence_numbers):
            grounded += 1

    return {
        "claimed_count": len(decimal_claims),
        "grounded_count": grounded,
        "groundedness_score": round(grounded / len(decimal_claims), 2),
        "note": "OK" if grounded == len(decimal_claims) else "Some claims not traceable to evidence",
    }


if __name__ == "__main__":
    # Quick manual test using a real example from Phase 7
    sample_package = {
        "ranked_candidates": [
            {
                "service": "catalogue",
                "metric_anomaly_score": 4516.08,
                "log_corroboration_score": 0.0,
                "combined_score": 0.5,
            },
        ]
    }

    sample_explanation = (
        "The catalogue service has the highest combined_score (0.5) and an "
        "extremely high metric_anomaly_score (4516.08), far exceeding rabbitmq."
    )

    print("Grounded test:", score_grounded(sample_explanation, sample_package))

    fabricated_explanation = (
        "The catalogue-db likely has 87.3% CPU usage and response times over 450ms."
    )

    print("Ungrounded test:", score_grounded(fabricated_explanation, {}))
