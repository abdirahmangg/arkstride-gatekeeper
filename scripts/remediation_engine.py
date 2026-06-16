import json
import sys
from pathlib import Path

REMEDIATION_FILE = Path("genome/remediation_library.json")

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def find_remediation(action, target):
    library = load_json(REMEDIATION_FILE)

    for item in library["remediations"]:
        action_match = item["action"] == action
        target_match = item["target"] == target

        if action_match and target_match:
            return item

    return None

def main():

    if len(sys.argv) != 3:
        print("Usage:")
        print("python remediation_engine.py <action> <target>")
        return 1

    action = sys.argv[1]
    target = sys.argv[2]

    remediation = find_remediation(action, target)

    if remediation is None:
        print("No remediation found.")
        return 0

    print("\nARKSTRIDE REMEDIATION\n")

    print(f"Title: {remediation['title']}")
    print(f"Risk Reduction: {remediation['risk_reduction']}%")

    print("\nSuggested Patch:")

    for patch in remediation["patch"]:
        print(f"- {patch}")

    return 0

if __name__ == "__main__":
    sys.exit(main())