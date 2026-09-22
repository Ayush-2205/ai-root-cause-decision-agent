"""
Phase 7, Step 3: Grounded LLM reasoning agent.

Takes an evidence package (and ONLY the evidence package) and
produces an explanation + confidence + recommendation, strictly
grounded in what's provided - required to say so explicitly when
evidence is weak or absent, rather than inventing detail.
"""

import os
import json
import sys
from dotenv import load_dotenv
from groq import Groq

sys.path.append(os.path.dirname(__file__))
from evidence_package import build_evidence_package

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])

SYSTEM_PROMPT = """You are a root-cause analysis assistant for microservice incidents.

You will be given a JSON evidence package containing ranked candidate services,
their anomaly scores, log corroboration scores, and any real supporting log lines.

STRICT RULES:
1. Only reference services, scores, and log lines that literally appear in the
   provided JSON. Never mention a service, metric, or log line not present in it.
2. If a candidate has an empty "supporting_log_lines" list, you MUST explicitly
   state that no corroborating log evidence was found for it - do not invent any.
3. Base your root cause choice primarily on "combined_score" (higher = more likely).
4. Your confidence must reflect the evidence strength: if the top candidate's
   combined_score is far higher than the second-place candidate, confidence can
   be higher; if scores are close together, say confidence is low/medium.
5. Output ONLY valid JSON matching this exact schema, nothing else:

{
  "root_cause_service": "<service name from the JSON>",
  "confidence": "<low|medium|high>",
  "explanation": "<2-4 sentences citing specific scores/log lines from the JSON>",
  "recommended_action": "<one concrete, specific action for an engineer>",
  "evidence_gaps": "<state explicitly if log evidence was missing/weak, or 'none' if evidence was strong>"
}"""


def run_reasoning(evidence_package: dict) -> dict:
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(evidence_package, indent=2)},
        ],
        temperature=0,
    )
    raw = response.choices[0].message.content

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("WARNING: response was not valid JSON. Raw output:")
        print(raw)
        return {"error": "invalid_json", "raw": raw}


def main():
    import pandas as pd
    selected = pd.read_csv("data/processed/selected_cases.csv")

    for _, row in selected.iterrows():
        print("=" * 70)
        print(f"CASE: {row['case']}  (true root cause: {row['root_cause_service']})")
        print("=" * 70)

        package, ground_truth = build_evidence_package(row["case"], row["root_cause_service"])
        result = run_reasoning(package)

        print(json.dumps(result, indent=2))
        print()


if __name__ == "__main__":
    main()
