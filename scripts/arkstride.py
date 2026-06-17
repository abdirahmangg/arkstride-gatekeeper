import json
import sys
from pathlib import Path
from reachability_engine import find_reachable_paths

REPORT_FILE = Path("reports/latest_report.json")

def load_json(path):
    return json.loads(Path(path).read_text())

def scenario_to_start_node(scenario):
    actor = scenario.get("actor")
    target = scenario.get("target")

    if actor == "ai_coding_agent":
        return "identity:ai_coding_agent"
    if target == "github":
        return "github_repo:arkstride-gatekeeper"
    if target == "s3":
        return "s3:prod_customer_data"
    if target == "service_account":
        return "iam_role:deployment_role"
    if target == "dev_logs":
        return "dev_logs"
    return target

def decision_from_reachability(paths):
    return "BLOCK" if paths else "ALLOW"

def write_report(scenario, start_node, paths, decision):
    report = {
        "scenario": scenario,
        "start_node": start_node,
        "decision": decision,
        "reachable_crown_jewels": paths,
        "reachable_count": len(paths)
    }
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(json.dumps(report, indent=2))
    return report

def print_paths(paths):
    if not paths:
        print("\nReachable Crown Jewels: none")
        return

    print("\nReachable Crown Jewels:")
    for item in paths:
        print(f"- {' -> '.join(item['path'])}")
        print(f"  Impact: {item['impact']}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/arkstride.py <scenario.json>")
        return 1

    scenario_file = Path(sys.argv[1])
    if not scenario_file.exists():
        print(f"Scenario not found: {scenario_file}")
        return 1

    scenario = load_json(scenario_file)
    start_node = scenario_to_start_node(scenario)
    paths = find_reachable_paths(start_node)
    decision = decision_from_reachability(paths)

    write_report(scenario, start_node, paths, decision)

    print("\nARKSTRIDE GRAPH-NATIVE VERIFICATION\n")
    print(f"Actor: {scenario.get('actor')}")
    print(f"Action: {scenario.get('action')}")
    print(f"Target: {scenario.get('target')}")
    print(f"Start Node: {start_node}")

    print_paths(paths)
    print(f"\nDecision: {decision}")

    return 1 if decision == "BLOCK" else 0

if __name__ == "__main__":
    sys.exit(main())
