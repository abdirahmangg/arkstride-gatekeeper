import json
import sys
from pathlib import Path

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def sentence_from_edge(source, target):
    return f"{source} can lead to {target}."

def build_attack_path_narrative(path):
    steps = []

    nodes = path.get("path", [])

    for index in range(len(nodes) - 1):
        source = nodes[index]
        target = nodes[index + 1]
        steps.append(sentence_from_edge(source, target))

    return steps

def build_future_narrative(future):
    path = future.get("future_path", [])
    impact = future.get("impact", "unknown impact")
    description = future.get("description", "")

    steps = []

    for index in range(len(path) - 1):
        source = path[index]
        target = path[index + 1]
        steps.append(sentence_from_edge(source, target))

    return {
        "name": future.get("name"),
        "risk": future.get("risk"),
        "impact": impact,
        "description": description,
        "steps": steps
    }

def build_narrative(report):
    scenario = report.get("scenario", {})
    decision = report.get("decision", "UNKNOWN")
    total_risk = report.get("total_risk", 0)

    lines = []

    lines.append("# ARKSTRIDE Security Narrative")
    lines.append("")
    lines.append(f"**Decision:** {decision}")
    lines.append(f"**Total Risk:** {total_risk}/100")
    lines.append("")

    lines.append("## Proposed Change")
    lines.append("")
    lines.append(f"- Actor: `{scenario.get('actor')}`")
    lines.append(f"- Action: `{scenario.get('action')}`")
    lines.append(f"- Target: `{scenario.get('target')}`")
    lines.append(f"- Environment: `{scenario.get('environment')}`")
    lines.append(f"- Reason: {scenario.get('reason')}")
    lines.append("")

    lines.append("## Executive Summary")
    lines.append("")

    if decision == "BLOCK":
        lines.append(
            "ARKSTRIDE blocked this change because it creates one or more dangerous future states."
        )
    elif decision == "REVIEW":
        lines.append(
            "ARKSTRIDE recommends human review because this change creates moderate future-state risk."
        )
    else:
        lines.append(
            "ARKSTRIDE allowed this change because no dangerous future state was identified."
        )

    lines.append("")

    attack_paths = report.get("attack_paths", [])

    if attack_paths:
        lines.append("## Attack Path Explanation")
        lines.append("")

        for path_index, path in enumerate(attack_paths, start=1):
            readable_path = " → ".join(path.get("path", []))
            lines.append(f"### Path {path_index}: `{readable_path}`")
            lines.append("")

            for step_index, step in enumerate(build_attack_path_narrative(path), start=1):
                lines.append(f"{step_index}. {step}")

            lines.append("")
            lines.append(f"**Business Impact:** `{path.get('impact')}`")
            lines.append("")

    futures = report.get("possible_futures", [])

    if futures:
        lines.append("## Simulated Futures")
        lines.append("")

        for future in futures:
            narrative = build_future_narrative(future)

            lines.append(f"### {narrative['name']} — Risk {narrative['risk']}/100")
            lines.append("")
            lines.append(narrative["description"])
            lines.append("")

            for step_index, step in enumerate(narrative["steps"], start=1):
                lines.append(f"{step_index}. {step}")

            lines.append("")
            lines.append(f"**Impact:** `{narrative['impact']}`")
            lines.append("")

    remediation = report.get("remediation")

    if remediation:
        lines.append("## Suggested Remediation")
        lines.append("")
        lines.append(f"**{remediation.get('title')}**")
        lines.append("")

        for patch in remediation.get("patch", []):
            lines.append(f"- `{patch}`")

        lines.append("")

    violations = report.get("policy_violations", [])

    if violations:
        lines.append("## Policy Violations")
        lines.append("")

        for violation in violations:
            lines.append(f"- {violation}")

        lines.append("")

    return "\n".join(lines)

def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("python scripts/narrative_engine.py <report.json>")
        return 1

    report_file = Path(sys.argv[1])

    if not report_file.exists():
        print(f"Report file not found: {report_file}")
        return 1

    report = load_json(report_file)
    narrative = build_narrative(report)

    Path("reports").mkdir(exist_ok=True)
    Path("reports/security_narrative.md").write_text(narrative)

    print(narrative)

    return 0

if __name__ == "__main__":
    sys.exit(main())
