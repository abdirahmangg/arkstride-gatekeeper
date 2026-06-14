import subprocess
import sys
from pathlib import Path

GENERATED_DIR = Path("scenarios/generated")

EXCLUDED_PATH_PARTS = {
    ".git",
    "scenarios",
    "examples/attack"
}

def is_excluded(path):
    normalized = str(path)
    return any(part in normalized for part in EXCLUDED_PATH_PARTS)

def terraform_files():
    return [
        path for path in Path(".").rglob("*.tf")
        if not is_excluded(path)
    ]

def main():
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    files = terraform_files()

    if not files:
        print("No Terraform files found.")
        return 0

    failed = []

    print("\nARKSTRIDE TERRAFORM SCAN\n")

    for tf_file in files:
        scenario_file = GENERATED_DIR / f"{tf_file.stem}_scenario.json"

        print("=" * 60)
        print(f"Terraform file: {tf_file}")
        print(f"Generated scenario: {scenario_file}")

        with open(scenario_file, "w") as out:
            convert = subprocess.run(
                ["python", "scripts/terraform_to_scenario.py", str(tf_file)],
                stdout=out,
                text=True
            )

        if convert.returncode != 0:
            print(f"Failed to convert Terraform file: {tf_file}")
            failed.append(str(tf_file))
            continue

        verify = subprocess.run(
            ["python", "scripts/arkstride.py", str(scenario_file)],
            text=True
        )

        if verify.returncode != 0:
            failed.append(str(tf_file))

    print("=" * 60)

    if failed:
        print("\nARKSTRIDE BLOCKED TERRAFORM CHANGES\n")
        for item in failed:
            print(f"- {item}")
        return 1

    print("\nARKSTRIDE ALLOWED ALL TERRAFORM CHANGES\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())