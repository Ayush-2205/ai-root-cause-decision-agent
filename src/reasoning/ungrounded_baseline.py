"""
Phase 7, Step 5: Ungrounded LLM baseline (B2) - given only a plain
text incident description, no structured evidence - for direct
comparison against the grounded reasoning agent.
"""

import os
import json
import pandas as pd
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])

UNGROUNDED_SYSTEM_PROMPT = """You are an SRE assistant diagnosing a microservice incident.
You will be given only a brief text description of the incident - no metrics,
logs, or scores. Based on your general knowledge of microservice systems,
give your best guess at the root cause.

Output ONLY valid JSON matching this schema:
{
  "root_cause_service": "<your best-guess service name>",
  "confidence": "<low|medium|high>",
  "explanation": "<your reasoning>"
}"""


def run_ungrounded(case_name: str, system_name: str, all_services: list,
                    alerting_service: str, fault_description: str) -> dict:
    incident_text = (
        f"An incident was detected in the '{system_name}' microservices system. "
        f"The services running in this system are: {', '.join(all_services)}. "
        f"Monitoring first raised an alert on the '{alerting_service}' service. "
        f"Reported symptom: {fault_description}. "
        f"Which service is most likely the root cause?"
    )
    

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": UNGROUNDED_SYSTEM_PROMPT},
            {"role": "user", "content": incident_text},
        ],
        temperature=0,
    )
    raw = response.choices[0].message.content
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"error": "invalid_json", "raw": raw}


import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "anomaly_detection"))
from baseline_b0 import score_case, rank_services

def main():
    selected = pd.read_csv("data/processed/selected_cases.csv")
    all_services = ["front-end", "orders", "orders-db", "carts", "carts-db",
                     "catalogue", "catalogue-db", "user", "user-db", "payment",
                     "shipping", "queue-master", "rabbitmq", "rabbitmq-exporter",
                     "session-db"]

    for _, row in selected.iterrows():
        b0_ranked = rank_services(score_case(row["case"]))
        alerting_service = b0_ranked.iloc[0]["service"]  # what monitoring would flag first

        fault_description = "elevated response times and abnormal resource usage reported by monitoring"
        result = run_ungrounded(row["case"], "Sock Shop", all_services, alerting_service, fault_description)

        print(f"{row['case']}  (true: {row['root_cause_service']}, alert fired on: {alerting_service})")
        print(json.dumps(result, indent=2))
        hit = result.get("root_cause_service") == row["root_cause_service"]
        print(f"HIT: {hit}\n")


if __name__ == "__main__":
    main()
