import json
import sys
from pathlib import Path

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def main():

    if len(sys.argv) != 2:
        print("Usage:")
        print("python scripts/pr_comment.py <arkstride-report.json>")
        return 1

    report_file = Path(sys.argv[1])

    if not report_file.exists():
        print("Report file not found.")
        return 1

    report = load_json(report_file)

    markdown = []

    markdown.append("# ❌ ARKSTRIDE BLOCKED THIS CHANGE")
    markdown.append("")

    markdown.append(f"**Decision:** {report['decision']}")
    markdown.append(f"**Total Risk:** {report['total_risk']}/100")
    markdown.append("")

    markdown.append("## Attack Paths")

    for path in report.get("attack_paths", []):
        markdown.append(
            f"- {' → '.join(path['path'])}"
        )

    markdown.append("")

    markdown.append("## Possible Futures")

    for future in report.get("possible_futures", []):
        markdown.append(
            f"- {future['name']} ({future['risk']}/100)"
        )

    markdown.append("")

    remediation = report.get("remediation")

    if remediation:

        markdown.append("## Suggested Remediation")
        markdown.append(remediation["title"])
        markdown.append("")

        for patch in remediation["patch"]:
            markdown.append(f"- {patch}")

    output = "\n".join(markdown)

    print(output)

    Path("arkstride_pr_comment.md").write_text(output)

    return 0

if __name__ == "__main__":
    sys.exit(main())