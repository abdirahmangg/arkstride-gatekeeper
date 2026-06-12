import json
import subprocess
import sys
from pathlib import Path

POLICY_FILE = "policies/arkstride.rego"

def evaluate_scenario(scenario_file):
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

def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("python scripts/arkstride.py <scenario.json>")
        sys.exit(1)

    scenario = sys.argv[1]

    if not Path(scenario).exists():
        print(f"Scenario not found: {scenario}")
        sys.exit(1)

    data = evaluate_scenario(scenario)
    denies = extract_denies(data)

    if denies:
        print("\nARKSTRIDE BLOCKED EXECUTION\n")
        print("Reasons:")
        for reason in denies:
            print(f"- {reason}")
        sys.exit(1)

    print("\nARKSTRIDE ALLOWED EXECUTION\n")
    sys.exit(0)

if __name__ == "__main__":
    main()
