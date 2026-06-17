from graph_store import load_graph, save_graph, add_node, add_edge

def main():
    graph = load_graph()

    add_node(graph, "aws_account:prod", "aws_account", {"environment": "prod"})
    add_node(graph, "iam_role:deployment_role", "iam_role", {"environment": "prod"})
    add_node(graph, "s3:prod_customer_data", "s3_bucket", {"environment": "prod"})
    add_node(graph, "database:production", "database", {"criticality": "crown_jewel"})
    add_node(graph, "data:customer_pii", "data_asset", {"criticality": "crown_jewel"})

    add_edge(graph, "github_secret:AWS_DEPLOY_ROLE", "iam_role:deployment_role", "authenticates_as", {
        "source": "simulated_secret_mapping"
    })
    add_edge(graph, "iam_role:deployment_role", "aws_account:prod", "can_administer", {
        "source": "simulated_iam_policy"
    })
    add_edge(graph, "aws_account:prod", "database:production", "can_access", {
        "source": "simulated_network_path"
    })
    add_edge(graph, "database:production", "data:customer_pii", "contains", {
        "source": "crown_jewel_mapping"
    })
    add_edge(graph, "s3:prod_customer_data", "aws_account:prod", "can_expose_credentials_to", {
        "source": "public_bucket_exposure"
    })

    save_graph(graph)
    print("Ingested AWS relationships.")

if __name__ == "__main__":
    main()
