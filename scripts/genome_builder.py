import json
from pathlib import Path

FILES = {
    "assets": Path("genome/assets.json"),
    "identities": Path("genome/identities.json"),
    "crown_jewels": Path("genome/crown_jewels.json"),
    "attack_graph": Path("genome/attack_graph.json"),
    "risk_graph": Path("genome/risk_graph.json"),
    "future_library": Path("genome/future_library.json"),
    "remediation_library": Path("genome/remediation_library.json"),
}

OUTPUT_FILE = Path("genome/enterprise_genome.json")


def load_json(path):
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def count_items(data, key):
    value = data.get(key, [])
    return len(value) if isinstance(value, list) else 0


def calculate_genome_score(summary):
    score = 0
    score += min(summary["asset_count"] * 5, 25)
    score += min(summary["identity_count"] * 5, 20)
    score += min(summary["crown_jewel_count"] * 10, 30)
    score += min(summary["attack_edge_count"] * 3, 25)
    return min(score, 100)


def build_enterprise_genome():
    assets = load_json(FILES["assets"])
    identities = load_json(FILES["identities"])
    crown_jewels = load_json(FILES["crown_jewels"])
    attack_graph = load_json(FILES["attack_graph"])
    risk_graph = load_json(FILES["risk_graph"])
    future_library = load_json(FILES["future_library"])
    remediation_library = load_json(FILES["remediation_library"])

    summary = {
        "asset_count": count_items(assets, "assets"),
        "identity_count": count_items(identities, "identities"),
        "crown_jewel_count": count_items(crown_jewels, "systems"),
        "attack_node_count": count_items(attack_graph, "nodes"),
        "attack_edge_count": count_items(attack_graph, "edges"),
        "risk_rule_count": count_items(risk_graph, "risk_rules"),
        "future_count": count_items(future_library, "futures"),
        "remediation_count": count_items(remediation_library, "remediations"),
    }

    summary["genome_completeness_score"] = calculate_genome_score(summary)

    genome = {
        "name": "ARKSTRIDE Enterprise Genome",
        "version": "0.1",
        "summary": summary,
        "assets": assets.get("assets", []),
        "identities": identities.get("identities", []),
        "crown_jewels": crown_jewels.get("systems", []),
        "attack_graph": attack_graph,
        "risk_graph": risk_graph,
        "future_library": future_library,
        "remediation_library": remediation_library,
    }

    OUTPUT_FILE.write_text(json.dumps(genome, indent=2))
    return genome


def main():
    genome = build_enterprise_genome()
    summary = genome["summary"]

    print("\nARKSTRIDE ENTERPRISE GENOME BUILT\n")
    print(f"Assets: {summary['asset_count']}")
    print(f"Identities: {summary['identity_count']}")
    print(f"Crown Jewels: {summary['crown_jewel_count']}")
    print(f"Attack Nodes: {summary['attack_node_count']}")
    print(f"Attack Edges: {summary['attack_edge_count']}")
    print(f"Risk Rules: {summary['risk_rule_count']}")
    print(f"Futures: {summary['future_count']}")
    print(f"Remediations: {summary['remediation_count']}")
    print(f"Genome Completeness: {summary['genome_completeness_score']}/100")
    print(f"\nWritten to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()