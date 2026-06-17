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
        graph.setdefault(edge["from"], []).append({
            "to": edge["to"],
            "relationship": edge.get("relationship", "connected_to")
        })

    return graph


def find_paths(start, adjacency, crown_jewels, max_depth=8):
    queue = deque()
    queue.append((start, [start], []))

    paths = []

    while queue:
        current, path, relationships = queue.popleft()

        if len(path) > max_depth:
            continue

        if current in crown_jewels and current != start:
            paths.append({
                "start": start,
                "impact": current,
                "path": path,
                "relationships": relationships,
                "path_length": len(path)
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

    return paths


def score_path(path_item):
    impact = path_item["impact"]
    length = path_item["path_length"]

    if impact == "customer_pii":
        base = 100
    elif impact == "payment_system":
        base = 95
    elif impact == "production_database":
        base = 90
    else:
        base = 70

    distance_penalty = max(0, (length - 2) * 5)
    return max(40, base - distance_penalty)


def analyze_all_starts():
    graph_data = load_json(ATTACK_GRAPH_FILE)

    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])
    crown_jewels = set(graph_data.get("crown_jewels", []))

    adjacency = build_adjacency(edges)

    all_paths = []

    for node in nodes:
        if node in crown_jewels:
            continue

        paths = find_paths(node, adjacency, crown_jewels)

        for path in paths:
            path["risk"] = score_path(path)
            all_paths.append(path)

    return sorted(all_paths, key=lambda item: item["risk"], reverse=True)


def main():
    paths = analyze_all_starts()

    print("\nARKSTRIDE MULTI-ASSET ATTACK PATHS\n")

    if not paths:
        print("No attack paths found.")
        return 0

    for item in paths[:20]:
        readable_path = " -> ".join(item["path"])
        readable_relationships = " -> ".join(item["relationships"])

        print("=" * 60)
        print(f"Start: {item['start']}")
        print(f"Impact: {item['impact']}")
        print(f"Risk: {item['risk']}/100")
        print(f"Path: {readable_path}")
        print(f"Relationships: {readable_relationships}")

    Path("reports").mkdir(exist_ok=True)
    Path("reports/multi_asset_paths.json").write_text(
        json.dumps(paths, indent=2)
    )

    print("\nWritten to: reports/multi_asset_paths.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())