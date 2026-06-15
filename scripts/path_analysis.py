import json
import sys
from collections import deque
from pathlib import Path

ATTACK_GRAPH_FILE = Path("genome/attack_graph.json")

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def build_adjacency(edges):
    graph = {}

    for edge in edges:
        source = edge["from"]
        target = edge["to"]
        relationship = edge.get("relationship", "connected_to")

        graph.setdefault(source, []).append({
            "to": target,
            "relationship": relationship
        })

    return graph

def find_paths_to_crown_jewels(start, adjacency, crown_jewels):
    queue = deque()
    queue.append((start, [start], []))

    found_paths = []

    while queue:
        current, path, relationships = queue.popleft()

        if current in crown_jewels and current != start:
            found_paths.append({
                "path": path,
                "relationships": relationships,
                "impact": current
            })
            continue

        for neighbor in adjacency.get(current, []):
            next_node = neighbor["to"]

            if next_node in path:
                continue

            queue.append((
                next_node,
                path + [next_node],
                relationships + [neighbor["relationship"]]
            ))

    return found_paths

def risk_from_paths(paths):
    if not paths:
        return 0

    max_path_score = 0

    for path in paths:
        path_length = len(path["path"])

        if path["impact"] == "customer_pii":
            impact_score = 100
        elif path["impact"] == "payment_system":
            impact_score = 95
        elif path["impact"] == "production_database":
            impact_score = 90
        else:
            impact_score = 70

        distance_penalty = max(0, (path_length - 2) * 10)
        score = max(50, impact_score - distance_penalty)

        max_path_score = max(max_path_score, score)

    return max_path_score

def analyze_start_node(start):
    attack_graph = load_json(ATTACK_GRAPH_FILE)

    adjacency = build_adjacency(attack_graph["edges"])
    crown_jewels = set(attack_graph["crown_jewels"])

    paths = find_paths_to_crown_jewels(start, adjacency, crown_jewels)
    graph_risk = risk_from_paths(paths)

    return {
        "start": start,
        "paths": paths,
        "graph_risk": graph_risk
    }

def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("python scripts/path_analysis.py <start-node>")
        sys.exit(1)

    start = sys.argv[1]
    result = analyze_start_node(start)

    print(json.dumps(result, indent=2))

    if result["graph_risk"] >= 80:
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()