import json
import subprocess
import sys
from pathlib import Path

POLICY_FILE = "policies/arkstride.rego"
RISK_GRAPH_FILE = "genome/risk_graph.json"

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def evaluate_policy(scenario_file):
    result = subprocess.run(
        [
            "opa",
            "eval",
            "-f",
            "json",
            "-i",
            scenario_file,
            "-d",
            POLICY_FILE,
            "data.arkstride.deny",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("OPA execution failed")
        print(result.stderr)
        sys.exit(1)

    return json.loads(result.stdout)

def extract_denies(data):
    try:
        return data["result"][0]["expressions"][0]["value"]
    except Exception:
        return []

def calculate_future_risk(scenario):
    risk_graph = load_json(RISK_GRAPH_FILE)

    default_risk = 10
    matched_reason = "No high-risk future state matched."

    for rule in risk_graph.get("risk_rules", []):
        action_match = rule["action"] == scenario.get("action")
        target_match = rule["target"] == scenario.get("target") or rule["target"] == "*"

        if action_match and target_match:
            return rule["future_risk"], rule["reason"]

    return default_risk, matched_reason

def decision_from_risk(risk, denies):
    if denies:
        return "BLOCK"

    if risk >= 80:
        return "BLOCK"

    if risk >= 50:
        return "REVIEW"

    return "ALLOW"

def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("python scripts/arkstride.py <scenario.json>")
        sys.exit(1)

    scenario_file = sys.argv[1]

    if not Path(scenario_file).exists():
        print(f"Scenario not found: {scenario_file}")
        sys.exit(1)

    scenario = load_json(scenario_file)
    policy_data = evaluate_policy(scenario_file)
    denies = extract_denies(policy_data)

    future_risk, risk_reason = calculate_future_risk(scenario)
    decision = decision_from_risk(future_risk, denies)

    print("\nARKSTRIDE REALITY VERIFICATION\n")

    print(f"Actor: {scenario.get('actor')}")
    print(f"Action: {scenario.get('action')}")
    print(f"Target: {scenario.get('target')}")
    print(f"Environment: {scenario.get('environment')}")

    print(f"\nFuture Risk: {future_risk}/100")
    print(f"Risk Reason: {risk_reason}")

    print(f"\nDecision: {decision}")

    if denies:
        print("\nPolicy Violations:")
        for reason in denies:
            print(f"- {reason}")

    if decision == "BLOCK":
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
