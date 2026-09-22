"""
Phase 9, Step 4: Re-score the user_loss_1 explanation with the
fixed rubric (ignoring quoted log text), no new API call needed.
"""

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "reasoning"))
from evidence_package import build_evidence_package
from groundedness import score_grounded

CASE = "re2ss_user_loss_1"
TRUTH = "user"

EXPLANATION = (
    'The user service has the highest combined_score (0.7051) driven by an extreme '
    'metric_anomaly_score of 11414.49 and a log_corroboration_score of 16.69. Supporting '
    'log lines show repeated i/o timeout errors when reading from MongoDB (10.108.9.83:27017), '
    'e.g., "read tcp 10.104.0.16:32922->10.108.9.83:27017: i/o timeout". The next candidate, '
    'front-end, has a combined_score of only 0.3007, indicating a much lower likelihood.'
)

package, _ = build_evidence_package(CASE, TRUTH)
print(score_grounded(EXPLANATION, package))