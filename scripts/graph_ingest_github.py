from graph_store import load_graph, save_graph, add_node, add_edge

def main():
    graph = load_graph()

    add_node(graph, "identity:ai_coding_agent", "ai_agent", {"trust_level": "low"})
    add_node(graph, "github_repo:arkstride-gatekeeper", "github_repository", {"criticality": "high"})
    add_node(graph, "github_actions:arkstride-gatekeeper", "ci_pipeline", {})
    add_node(graph, "github_secret:AWS_DEPLOY_ROLE", "secret", {})

    add_edge(graph, "identity:ai_coding_agent", "github_repo:arkstride-gatekeeper", "can_write_to", {
        "source": "simulated_github_ingestion"
    })
    add_edge(graph, "github_repo:arkstride-gatekeeper", "github_actions:arkstride-gatekeeper", "triggers", {
        "source": "workflow_detection"
    })
    add_edge(graph, "github_actions:arkstride-gatekeeper", "github_secret:AWS_DEPLOY_ROLE", "can_access", {
        "source": "github_actions_secret_mapping"
    })

    save_graph(graph)
    print("Ingested GitHub relationships.")

if __name__ == "__main__":
    main()
