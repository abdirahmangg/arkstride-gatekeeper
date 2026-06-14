import json
import sys
from pathlib import Path

def infer_environment(content):
    lowered = content.lower()

    if "prod" in lowered or "production" in lowered:
        return "prod"

    if "dev" in lowered:
        return "dev"

    return "unknown"

def detect_public_s3(content):
    lowered = content.lower()

    public_access_disabled = (
        "block_public_acls       = false" in lowered
        or "block_public_policy     = false" in lowered
        or "ignore_public_acls      = false" in lowered
        or "restrict_public_buckets = false" in lowered
    )

    has_s3_bucket = "aws_s3_bucket" in lowered

    return has_s3_bucket and public_access_disabled

def convert(terraform_file):
    path = Path(terraform_file)

    if not path.exists():
        print(f"Terraform file not found: {terraform_file}")
        sys.exit(1)

    content = path.read_text()

    environment = infer_environment(content)

    if detect_public_s3(content):
        return {
            "actor": "developer",
            "actor_type": "human",
            "action": "public_expose",
            "target": "s3",
            "environment": environment,
            "reason": f"Terraform file {terraform_file} appears to allow public S3 exposure."
        }

    return {
        "actor": "developer",
        "actor_type": "human",
        "action": "infrastructure_change",
        "target": "terraform",
        "environment": environment,
        "reason": f"No dangerous Terraform pattern detected in {terraform_file}."
    }

def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("python scripts/terraform_to_scenario.py <terraform-file>")
        sys.exit(1)

    scenario = convert(sys.argv[1])
    print(json.dumps(scenario, indent=2))

if __name__ == "__main__":
    main()