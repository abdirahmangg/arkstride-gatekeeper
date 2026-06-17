import subprocess
import sys
from pathlib import Path

GRAPH_FILE = Path("graph/enterprise_graph.json")

def run(command):
    result = subprocess.run(command, text=True)
    return result.returncode

def main():
    GRAPH_FILE.parent.mkdir(parents=True, exist_ok=True)
    GRAPH_FILE.write_text('{"nodes": [], "edges": []}')

    commands = [
        ["python", "scripts/graph_ingest_github.py"],
        ["python", "scripts/graph_ingest_aws.py"],
    ]

    for command in commands:
        code = run(command)
        if code != 0:
            return code

    print("\nEnterprise Knowledge Graph rebuilt.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
