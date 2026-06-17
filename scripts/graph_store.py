import json
from pathlib import Path

GRAPH_FILE = Path("graph/enterprise_graph.json")

def load_graph():
    if not GRAPH_FILE.exists():
        return {"nodes": [], "edges": []}
    return json.loads(GRAPH_FILE.read_text())

def save_graph(graph):
    GRAPH_FILE.parent.mkdir(parents=True, exist_ok=True)
    GRAPH_FILE.write_text(json.dumps(graph, indent=2))

def node_exists(graph, node_id):
    return any(node["id"] == node_id for node in graph["nodes"])

def edge_exists(graph, source, target, relationship):
    return any(
        edge["from"] == source and edge["to"] == target and edge["relationship"] == relationship
        for edge in graph["edges"]
    )

def add_node(graph, node_id, node_type, metadata=None):
    if metadata is None:
        metadata = {}
    if not node_exists(graph, node_id):
        graph["nodes"].append({
            "id": node_id,
            "type": node_type,
            "metadata": metadata
        })

def add_edge(graph, source, target, relationship, evidence=None):
    if evidence is None:
        evidence = {}
    if not edge_exists(graph, source, target, relationship):
        graph["edges"].append({
            "from": source,
            "to": target,
            "relationship": relationship,
            "evidence": evidence
        })

def main():
    graph = load_graph()
    print("\nARKSTRIDE ENTERPRISE KNOWLEDGE GRAPH\n")
    print(f"Nodes: {len(graph['nodes'])}")
    print(f"Edges: {len(graph['edges'])}")

if __name__ == "__main__":
    main()
