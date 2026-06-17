import json
import sys
from pathlib import Path

def load_json(path):
    return json.loads(Path(path).read_text())

def build_narrative(report):
    scenario = report.get("scenario", {})
    decision = report.get("decision")
    paths = report.get("reachable_crown_jewels", [])

    lines = [
        "# ARKSTRIDE Graph-Native Security Narrative",
        "",
        f"**Decision:** {decision}",
        f"**Reachable Crown Jewels:** {len(paths)}",
        "",
        "## Proposed Change",
        "",
        f"- Actor: `{scenario.get('actor')}`",
        f"- Action: `{scenario.get('action')}`",
        f"- Target: `{scenario.get('target')}`",
        f"- Environment: `{scenario.get('environment')}`",
        "",
    ]

    if decision == "BLOCK":
        lines += [
            "## Why ARKSTRIDE Blocked This",
            "",
            "This change was blocked because one or more crown-jewel systems became reachable through the Enterprise Knowledge Graph.",
            "",
        ]

    if paths:
        lines += ["## Reachable Consequence Paths", ""]
        for index, path in enumerate(paths, start=1):
            lines += [
                f"### Path {index}",
                "",
                f"`{' → '.join(path['path'])}`",
                "",
                f"**Impact:** `{path['impact']}`",
                "",
            ]

    return "\n".join(lines)

def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/narrative_engine.py <report.json>")
        return 1

    report = load_json(sys.argv[1])
    narrative = build_narrative(report)

    Path("reports").mkdir(exist_ok=True)
    Path("reports/security_narrative.md").write_text(narrative)

    print(narrative)
    return 0

if __name__ == "__main__":
    sys.exit(main())
