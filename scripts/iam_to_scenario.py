import json
import sys
from pathlib import Path

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def normalize_list(value):
    if isinstance(value, list):
        return value
    return [value]

def is_admin_policy(statement):
    if statement.get("Effect") != "Allow":
        return False

    actions = normalize_list(statement.get("Action", []))
    resources = normalize_list(statement.get("Resource", []))

    wildcard_action = "*" in actions or "*:*" in actions
    wildcard_resource = "*" in resources

    return wildcard_action and wildcard_resource

def is_privilege_escalation(statement):
    if statement.get("Effect") != "Allow":
        return False

    actions = normalize_list(statement.get("Action", []))

    dangerous_actions = {
        "iam:AttachRolePolicy",
        "iam:PutRolePolicy",
        "iam:CreateAccessKey",
        "iam:PassRole",
        "sts:AssumeRole"
    }

    return any(action in dangerous_actions for action in actions)

def convert(policy_file):
    path = Path(policy_file)

    if not path.exists():
        print(f"IAM policy file not found: {policy_file}", file=sys.stderr)
        sys.exit(1)

    policy = load_json(path)
    statements = normalize_list(policy.get("Statement", []))

    for statement in statements:
        if is_admin_policy(statement):
            return {
                "actor": "developer",
                "actor_type": "human",
                "action": "grant_admin",
                "target": "service_account",
                "environment": "prod",
                "reason": f"IAM policy {policy_file} grants wildcard admin privileges."
            }

        if is_privilege_escalation(statement):
            return {
                "actor": "developer",
                "actor_type": "human",
                "action": "grant_admin",
                "target": "service_account",
                "environment": "prod",
                "reason": f"IAM policy {policy_file} enables privilege escalation."
            }

    return {
        "actor": "developer",
        "actor_type": "human",
        "action": "read",
        "target": "dev_logs",
        "environment": "dev",
        "reason": f"No dangerous IAM privilege pattern detected in {policy_file}."
    }

def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("python scripts/iam_to_scenario.py <iam-policy.json>", file=sys.stderr)
        sys.exit(1)

    scenario = convert(sys.argv[1])
    print(json.dumps(scenario, indent=2))

if __name__ == "__main__":
    main()