import sys
from pathlib import Path
import subprocess

def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("python scripts/pr_comment.py <arkstride-report.json>")
        return 1

    report_file = Path(sys.argv[1])

    if not report_file.exists():
        print("Report file not found.")
        return 1

    result = subprocess.run(
        ["python", "scripts/narrative_engine.py", str(report_file)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(result.stderr)
        return 1

    comment = result.stdout

    Path("arkstride_pr_comment.md").write_text(comment)

    print(comment)

    return 0

if __name__ == "__main__":
    sys.exit(main())
