import json
import subprocess
from graph_store import load_graph, save_graph, add_node, add_edge

REPO = "abdirahmangg/arkstride-gatekeeper"

def gh_json(args):
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(result.stderr)
        return None
    return json.loads(result.stdout)

def main():
    graph = load_graph()

    repo = gh_json(["repo", "view", REPO, "--json", "nameWithOwner,visibility,defaultBranchRef"])
    if not repo:
        return 1

    repo_id = f"github_repo:{repo['nameWithOwner']}"
    add_node(graph, repo_id, "github_repository", {
        "visibility": repo["visibility"],
        "default_branch": repo["defaultBranchRef"]["name"]
    })

    workflows = gh_json(["api", f"repos/{REPO}/actions/workflows"])
    if workflows:
        for wf in workflows.get("workflows", []):
            workflow_id = f"github_workflow:{REPO}:{wf['name']}"
            add_node(graph, workflow_id, "github_workflow", {
                "path": wf.get("path"),
                "state": wf.get("state")
            })
            add_edge(graph, repo_id, workflow_id, "defines_workflow", {
                "source": "github_api"
            })

    save_graph(graph)
    print("Ingested real GitHub metadata into Enterprise Knowledge Graph.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
