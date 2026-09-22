"""
Phase 10: FastAPI backend wrapping the existing pipeline.

Reuses the exact same functions already tested in Phases 4-8 -
this file only wires them into HTTP endpoints, it does not
reimplement any logic.
"""

import sys
import os
import pandas as pd

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "src", "root_cause")
)

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "src", "anomaly_detection")
)

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "src", "reasoning")
)

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "src", "decision")
)

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..")
)

from src.config import DATA_DIR

from combined_score import combined_rank_for_case
from evidence_package import build_evidence_package
from reasoning_agent import run_reasoning
from db import init_db, save_decision, save_feedback, get_all_decisions

app = FastAPI(
    title="AI Root Cause and Decision Agent API",
    description="Evidence-grounded root cause analysis for microservice incidents",
    version="0.1.0",
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for a demo project; would restrict in production
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


class FeedbackRequest(BaseModel):
    decision_id: int
    verdict: str  # "confirmed" or "corrected"
    corrected_service: str | None = None
    notes: str | None = None


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "AI Root Cause and Decision Agent API is running",
    }


@app.get("/cases")
def list_cases():
    """List all cases available in our current pilot subset."""
    selected = pd.read_csv(f"{DATA_DIR}/selected_cases.csv")
    return selected.to_dict(orient="records")


@app.post("/analyze/{case_id}")
def analyze_case(case_id: str):
    """Run the full pipeline for one case: metrics+log ranking,
    grounded LLM reasoning, and save the decision."""

    selected = pd.read_csv(f"{DATA_DIR}/selected_cases.csv")

    matching = selected[selected["case"] == case_id]

    if matching.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Case '{case_id}' not found in pilot subset",
        )

    row = matching.iloc[0]

    try:
        ranked = combined_rank_for_case(case_id)

        package, _ = build_evidence_package(
            case_id,
            row["root_cause_service"],
        )

        result = run_reasoning(package)

        decision_id = save_decision(
            case_id,
            result,
            top_combined_score=float(
                ranked.iloc[0]["combined_score"]
            ),
        )

        return {
            "decision_id": decision_id,
            "case_id": case_id,
            "ranked_candidates": ranked.head(5)[
                [
                    "service",
                    "anomaly_score",
                    "log_corroboration",
                    "combined_score",
                ]
            ].to_dict(orient="records"),
            "ai_decision": result,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline error: {str(e)}",
        )


@app.post("/feedback")
def submit_feedback(fb: FeedbackRequest):
    if fb.verdict not in ("confirmed", "corrected"):
        raise HTTPException(
            status_code=400,
            detail="verdict must be 'confirmed' or 'corrected'",
        )

    save_feedback(
        fb.decision_id,
        fb.verdict,
        fb.corrected_service,
        fb.notes,
    )

    return {
        "status": "saved",
        "decision_id": fb.decision_id,
        "verdict": fb.verdict,
    }


@app.get("/decisions")
def list_decisions():
    """List all past AI decisions and any human feedback on them."""

    decisions = get_all_decisions()

    return [
        {
            "id": d.id,
            "case_id": d.case_id,
            "root_cause_service": d.root_cause_service,
            "confidence": d.confidence,
            "created_at": d.created_at.isoformat(),
            "feedback": [
                {
                    "verdict": f.verdict,
                    "corrected_service": f.corrected_service,
                    "notes": f.notes,
                }
                for f in d.feedback
            ],
        }
        for d in decisions
    ]
