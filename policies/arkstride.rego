package arkstride

default allow := false

deny contains msg {
    input.actor_type == "ai_agent"
    input.environment == "prod"

    msg := "AI agents cannot directly execute production actions."
}

deny contains msg {
    input.action == "delete"
    input.target == "production_database"

    msg := "Delete action against production database is forbidden."
}

deny contains msg {
    input.action == "public_expose"

    msg := "Public exposure action is forbidden."
}

allow if {
    count(deny) == 0
}
