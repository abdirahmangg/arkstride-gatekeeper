import json
import sys
from pathlib import Path

FUTURE_LIBRARY_FILE = Path("genome/future_library.json")

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def scenario_matches_future(scenario, future):
    action_match = future["trigger_action"] == scenario.get("action")
    target_match = (
        future["trigger_target"] == scenario.get("target")
        or future["trigger_target"] == "*"
    )

    return action_match and target_match

def simulate_futures(scenario):
    library = load_json(FUTURE_LIBRARY_FILE)
    possible_futures = []

    for future in library.get("futures", []):
        if scenario_matches_future(scenario, future):
            possible_futures.append(future)

    possible_futures = sorted(
        possible_futures,
        key=lambda item: item["risk"],
        reverse=True
    )

    return possible_futures

def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("python scripts/simulate_futures.py <scenario.json>")
        return 1

    scenario_file = Path(sys.argv[1])

    if not scenario_file.exists():
        print(f"Scenario not found: {scenario_file}")
        return 1

    scenario = load_json(scenario_file)
    futures = simulate_futures(scenario)

    result = {
        "scenario": scenario_file.as_posix(),
        "possible_futures": futures,
        "future_count": len(futures),
        "highest_risk": futures[0]["risk"] if futures else 0
    }

    print(json.dumps(result, indent=2))

    return 1 if result["highest_risk"] >= 80 else 0

if __name__ == "__main__":
    sys.exit(main())