import subprocess
import sys
from pathlib import Path

UNSAFE_FILE = Path("examples/attack/unsafe_terraform.tf")
FIXED_FILE = Path("examples/attack/unsafe_terraform.fixed.tf")

REPLACEMENTS = {
    "block_public_acls       = false": "block_public_acls       = true",
    "block_public_policy     = false": "block_public_policy     = true",
    "ignore_public_acls      = false": "ignore_public_acls      = true",
    "restrict_public_buckets = false": "restrict_public_buckets = true",
}

def apply_simulated_fix():
    if not UNSAFE_FILE.exists():
        print(f"Unsafe file not found: {UNSAFE_FILE}")
        return False

    content = UNSAFE_FILE.read_text()

    for old, new in REPLACEMENTS.items():
        content = content.replace(old, new)

    FIXED_FILE.write_text(content)
    return True

def run_command(command):
    return subprocess.run(
        command,
        text=True,
        capture_output=True
    )

def main():
    print("\nARKSTRIDE REMEDIATION VALIDATION\n")

    print("Step 1: Applying simulated remediation...")

    if not apply_simulated_fix():
        return 1

    print(f"Created fixed file: {FIXED_FILE}")

    print("\nStep 2: Converting fixed Terraform to scenario...")

    scenario_file = Path("scenarios/generated/remediation_validation.json")
    scenario_file.parent.mkdir(parents=True, exist_ok=True)

    convert = run_command([
        "python",
        "scripts/terraform_to_scenario.py",
        str(FIXED_FILE)
    ])

    if convert.returncode != 0:
        print(convert.stderr)
        return 1

    scenario_file.write_text(convert.stdout)

    print("\nStep 3: Re-running ARKSTRIDE on fixed scenario...")

    verify = subprocess.run([
        "python",
        "scripts/arkstride.py",
        str(scenario_file)
    ])

    if verify.returncode == 0:
        print("\nREMEDIATION VERIFIED")
        print("Risk successfully reduced. Fixed Terraform is allowed.")
        return 0

    print("\nREMEDIATION FAILED")
    print("Fixed Terraform is still blocked.")
    return 1

if __name__ == "__main__":
    sys.exit(main())