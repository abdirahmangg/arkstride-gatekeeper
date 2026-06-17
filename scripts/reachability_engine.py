import json
import sys
from collections import deque
from pathlib import Path

GRAPH_FILE = Path("graph/enterprise_graph.json")
CROWN_JEWEL_IDS = {"database:production", "data:customer_pii"}

def load_graph():
    return json.loads(GRAPH_FILE.read_text())

def build_adjacency(graph):
    adjacency = {}
    for edge in graph["edges"]:
        adjacency.setdefault(edge["from"], []).append(edge)
    return adjacency

def find_reachable_paths(start_node):
    graph = load_graph()
    adjacency = build_adjacency(graph)

    queue = deque([(start_node, [start_node], [])])
    reachable = []

    while queue:
        current, path, edges = queue.popleft()

        if current in CROWN_JEWEL_IDS and current != start_node:
            reachable.append({
                "path": path,
                "relationships": [edge["relationship"] for edge in edges],
                "impact": current,
                "evidence": [edge.get("evidence", {}) for edge in edges]
            })
            continue

        for edge in adjacency.get(current, []):
            next_node = edge["to"]
            if next_node in path:
                continue
            queue.append((next_node, path + [next_node], edges + [edge]))

    return reachable

def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/reachability_engine.py <node_id>")
        return 1

    start_node = sys.argv[1]
    paths = find_reachable_paths(start_node)

    print(json.dumps({
        "start_node": start_node,
        "reachable_crown_jewels": paths,
        "reachable_count": len(paths)
    }, indent=2))

    return 1 if paths else 0

if __name__ == "__main__":
    sys.exit(main())
