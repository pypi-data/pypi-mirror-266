{
    "type": {"required": True, "type": "string", "regex": "(?i)^(prog|sys)$"},
    "niveau": {"required": False, "type": "string"},
    "titre": {"required": False, "type": "string"},
    "objectif": {"required": False, "type": "string"},
    "description": {"required": False, "type": "string"},
    "énoncé": {
        "required": False,
        "type": ["string", "list"],
        "schema": {
            "required": True,
            "empty": False,
            "type": "dict",
            "schema": {
                "titre": {"required": False, "type": "string"},
                "texte": {"required": True, "type": "string"},
            },
        },
    },
    "auteur": {"required": False, "type": "string"},
    "licence": {"required": False, "type": "string"},
    "rétroactions": {"required": False, "type": "dict", "schema": "rétroactions"},
    "ttl": {"required": False, "type": "integer"},
}
