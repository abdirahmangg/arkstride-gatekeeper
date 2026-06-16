import json
import subprocess
import sys
from pathlib import Path

POLICY_FILE = "policies/arkstride.rego"
RISK_GRAPH_FILE = "genome/risk_graph.json"
ATTACK_GRAPH_FILE = "genome/attack_graph.json"
FUTURE_LIBRARY_FILE = "genome/future_library.json"
REMEDIATION_FILE = "genome/remediation_library.json"
REPORT_FILE = "reports/latest_report.json"


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


def build_adjacency(edges):
    graph = {}

    for edge in edges:
        source = edge["from"]
        target = edge["to"]
        relationship = edge.get("relationship", "connected_to")

        graph.setdefault(source, []).append(
            {
                "to": target,
                "relationship": relationship,
            }
        )

    return graph


def find_paths_to_crown_jewels(start, adjacency, crown_jewels):
    queue = [(start, [start], [])]
    found_paths = []

    while queue:
        current, path, relationships = queue.pop(0)

        if current in crown_jewels and current != start:
            found_paths.append(
                {
                    "path": path,
                    "relationships": relationships,
                    "impact": current,
                }
            )
            continue

        for neighbor in adjacency.get(current, []):
            next_node = neighbor["to"]

            if next_node in path:
                continue

            queue.append(
                (
                    next_node,
                    path + [next_node],
                    relationships + [neighbor["relationship"]],
                )
            )

    return found_paths


def risk_from_attack_paths(paths):
    if not paths:
        return 0

    max_score = 0

    for item in paths:
        path_length = len(item["path"])

        if item["impact"] == "customer_pii":
            impact_score = 100
        elif item["impact"] == "payment_system":
            impact_score = 95
        elif item["impact"] == "production_database":
            impact_score = 90
        else:
            impact_score = 70

        distance_penalty = max(0, (path_length - 2) * 10)
        score = max(50, impact_score - distance_penalty)

        max_score = max(max_score, score)

    return max_score


def analyze_attack_graph(target):
    if not Path(ATTACK_GRAPH_FILE).exists():
        return [], 0

    attack_graph = load_json(ATTACK_GRAPH_FILE)
    adjacency = build_adjacency(attack_graph.get("edges", []))
    crown_jewels = set(attack_graph.get("crown_jewels", []))

    paths = find_paths_to_crown_jewels(target, adjacency, crown_jewels)
    graph_risk = risk_from_attack_paths(paths)

    return paths, graph_risk


def simulate_possible_futures(scenario):
    if not Path(FUTURE_LIBRARY_FILE).exists():
        return []

    library = load_json(FUTURE_LIBRARY_FILE)
    futures = []

    for future in library.get("futures", []):
        action_match = future["trigger_action"] == scenario.get("action")
        target_match = (
            future["trigger_target"] == scenario.get("target")
            or future["trigger_target"] == "*"
        )

        if action_match and target_match:
            futures.append(future)

    return sorted(futures, key=lambda item: item["risk"], reverse=True)


def risk_from_futures(futures):
    if not futures:
        return 0

    return max(future["risk"] for future in futures)


def find_remediation(action, target):
    if not Path(REMEDIATION_FILE).exists():
        return None

    library = load_json(REMEDIATION_FILE)

    for item in library.get("remediations", []):
        action_match = item["action"] == action
        target_match = item["target"] == target or item["target"] == "*"

        if action_match and target_match:
            return item

    return None


def decision_from_risk(future_risk, graph_risk, denies):
    total_risk = max(future_risk, graph_risk)

    if denies:
        return "BLOCK", total_risk

    if total_risk >= 80:
        return "BLOCK", total_risk

    if total_risk >= 50:
        return "REVIEW", total_risk

    return "ALLOW", total_risk


def print_attack_paths(paths):
    if not paths:
        print("\nAttack Paths: none found")
        return

    print("\nAttack Paths:")

    for item in paths:
        readable_path = " -> ".join(item["path"])
        print(f"- {readable_path}")
        print(f"  Impact: {item['impact']}")


def print_possible_futures(futures):
    if not futures:
        print("\nPossible Futures: none simulated")
        return

    print("\nPossible Futures:")

    for future in futures:
        readable_path = " -> ".join(future["future_path"])
        print(f"- {future['name']}")
        print(f"  Path: {readable_path}")
        print(f"  Impact: {future['impact']}")
        print(f"  Risk: {future['risk']}/100")
        print(f"  Description: {future['description']}")


def print_remediation(remediation):
    if not remediation:
        print("\nSuggested Remediation: none found")
        return

    print("\nSuggested Remediation:")
    print(remediation["title"])

    print("\nSuggested Patch:")

    for patch in remediation.get("patch", []):
        print(f"- {patch}")


def write_report(
    scenario,
    decision,
    total_risk,
    future_risk,
    graph_risk,
    future_simulation_risk,
    risk_reason,
    attack_paths,
    possible_futures,
    remediation,
    denies,
):
    report = {
        "scenario": scenario,
        "decision": decision,
        "total_risk": total_risk,
        "future_risk": future_risk,
        "attack_graph_risk": graph_risk,
        "future_simulation_risk": future_simulation_risk,
        "risk_reason": risk_reason,
        "attack_paths": attack_paths,
        "possible_futures": possible_futures,
        "remediation": remediation,
        "policy_violations": denies,
    }

    reports_path = Path("reports")
    if reports_path.exists() and not reports_path.is_dir():
        reports_path.unlink()

    reports_path.mkdir(exist_ok=True)
    Path(REPORT_FILE).write_text(json.dumps(report, indent=2))

    return report


def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("python scripts/arkstride.py <scenario.json>")
        return 1

    scenario_file = sys.argv[1]

    if not Path(scenario_file).exists():
        print(f"Scenario not found: {scenario_file}")
        return 1

    scenario = load_json(scenario_file)
    policy_data = evaluate_policy(scenario_file)
    denies = extract_denies(policy_data)

    future_risk, risk_reason = calculate_future_risk(scenario)
    attack_paths, graph_risk = analyze_attack_graph(scenario.get("target"))

    possible_futures = simulate_possible_futures(scenario)
    future_simulation_risk = risk_from_futures(possible_futures)

    combined_future_risk = max(future_risk, future_simulation_risk)

    decision, total_risk = decision_from_risk(
        combined_future_risk,
        graph_risk,
        denies,
    )

    remediation = find_remediation(
        scenario.get("action"),
        scenario.get("target"),
    )

    write_report(
        scenario=scenario,
        decision=decision,
        total_risk=total_risk,
        future_risk=future_risk,
        graph_risk=graph_risk,
        future_simulation_risk=future_simulation_risk,
        risk_reason=risk_reason,
        attack_paths=attack_paths,
        possible_futures=possible_futures,
        remediation=remediation,
        denies=denies,
    )

    print("\nARKSTRIDE REALITY VERIFICATION\n")

    print(f"Actor: {scenario.get('actor')}")
    print(f"Action: {scenario.get('action')}")
    print(f"Target: {scenario.get('target')}")
    print(f"Environment: {scenario.get('environment')}")

    print(f"\nFuture Risk: {future_risk}/100")
    print(f"Attack Graph Risk: {graph_risk}/100")
    print(f"Future Simulation Risk: {future_simulation_risk}/100")
    print(f"Total Risk: {total_risk}/100")
    print(f"Risk Reason: {risk_reason}")

    print_attack_paths(attack_paths)
    print_possible_futures(possible_futures)

    print(f"\nDecision: {decision}")

    if denies:
        print("\nPolicy Violations:")
        for reason in denies:
            print(f"- {reason}")

    if decision == "BLOCK":
        print_remediation(remediation)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
