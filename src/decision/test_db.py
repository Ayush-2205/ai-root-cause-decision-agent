"""
Phase 8, Step 1: Quick test - create the DB, save one decision,
save feedback on it, and read both back.
"""

from db import init_db, save_decision, save_feedback, get_all_decisions

init_db()

fake_llm_result = {
    "root_cause_service": "catalogue",
    "confidence": "high",
    "explanation": "Test explanation for DB check.",
    "recommended_action": "Test recommended action.",
    "evidence_gaps": "none",
}

decision_id = save_decision("re2ss_catalogue_cpu_2", fake_llm_result, top_combined_score=0.5)
print(f"Saved decision with id={decision_id}")

save_feedback(decision_id, verdict="confirmed", notes="Looks correct, matches ground truth.")
print("Saved feedback.")

print("\nAll decisions in DB:")
for d in get_all_decisions():
    print(f"  id={d.id} case={d.case_id} root_cause={d.root_cause_service} confidence={d.confidence}")
    for f in d.feedback:
        print(f"    -> feedback: {f.verdict} ({f.notes})")
    