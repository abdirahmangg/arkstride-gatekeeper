import subprocess
import sys
from pathlib import Path

SCENARIOS_DIR = Path("scenarios/safe")

def main():
    scenario_files = sorted(SCENARIOS_DIR.glob("*.json"))
    failed = []

    print("\nARKSTRIDE GRAPH-NATIVE SAFE SCENARIO VERIFICATION\n")

    for scenario in scenario_files:
        print("=" * 60)
        print(f"Evaluating: {scenario}")

        result = subprocess.run(
            ["python", "scripts/arkstride.py", str(scenario)],
            text=True
        )

        if result.returncode != 0:
            failed.append(str(scenario))

    print("=" * 60)

    if failed:
        print("\nARKSTRIDE BLOCKED ONE OR MORE SAFE SCENARIOS\n")
        for item in failed:
            print(f"- {item}")
        return 1

    print("\nARKSTRIDE ALLOWED ALL SAFE SCENARIOS\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
