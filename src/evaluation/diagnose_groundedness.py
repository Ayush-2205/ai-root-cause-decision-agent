"""
Phase 9, Step 3: Show exactly which numbers in the grounded agent's
explanation for re2ss_user_loss_1 could NOT be traced to the
evidence package, and what they actually were.
"""

import sys, os, json
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "reasoning"))
from evidence_package import build_evidence_package
from reasoning_agent import run_reasoning
from groundedness import extract_numbers, numbers_in_package

CASE = "re2ss_user_loss_1"
TRUTH = "user"

package, _ = build_evidence_package(CASE, TRUTH)
result = run_reasoning(package)
explanation = result.get("explanation", "")

print("Full explanation text:")
print(explanation)

claimed = [n for n in extract_numbers(explanation) if n != int(n)]
evidence = numbers_in_package(package)

print(f"\nNumbers claimed (decimals only): {claimed}")
print(f"Numbers actually in evidence package: {sorted(evidence)}")

untraceable = [n for n in claimed if not any(abs(n - e) <= 0.05 for e in evidence)]
print(f"\nUNTRACEABLE claims: {untraceable}")