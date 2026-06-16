import subprocess
import sys
from pathlib import Path

GENERATED_DIR = Path("scenarios/generated")

EXCLUDED_PATH_PARTS = {
    ".git",
    "scenarios",
    "examples/iam/attack"
}

def is_excluded(path):
    normalized = str(path)
    return any(part in normalized for part in EXCLUDED_PATH_PARTS)

def iam_files():
    return [
        path for path in Path(".").rglob("*.json")
        if "iam" in str(path).lower()
        and not is_excluded(path)
    ]

def main():
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    files = iam_files()

    if not files:
        print("No IAM policy files found.")
        return 0

    failed = []

    print("\nARKSTRIDE IAM SCAN\n")

    for iam_file in files:
        scenario_file = GENERATED_DIR / f"{iam_file.stem}_iam_scenario.json"

        print("=" * 60)
        print(f"IAM policy file: {iam_file}")
        print(f"Generated scenario: {scenario_file}")

        with open(scenario_file, "w") as out:
            convert = subprocess.run(
                ["python", "scripts/iam_to_scenario.py", str(iam_file)],
                stdout=out,
                text=True
            )

        if convert.returncode != 0:
            print(f"Failed to convert IAM file: {iam_file}")
            failed.append(str(iam_file))
            continue

        verify = subprocess.run(
            ["python", "scripts/arkstride.py", str(scenario_file)],
            text=True
        )

        if verify.returncode != 0:
            failed.append(str(iam_file))

    print("=" * 60)

    if failed:
        print("\nARKSTRIDE BLOCKED IAM CHANGES\n")
        for item in failed:
            print(f"- {item}")
        return 1

    print("\nARKSTRIDE ALLOWED ALL IAM CHANGES\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())