{
    **schema_registry.get("question_base"),
    "image": {
        "required": True,
        "type": "string",
        "empty": False,
        "nullable": True,
    },
    "tests": {
        "excludes": "réponse",
        "required": True,
        "type": "list",
        "empty": False,
        "schema": {
            "required": True,
            "type": "dict",
            "schema": "test_sys",
        },
    },
    "réponse": {
        "excludes": "tests",
        "required": True,
        "type": "string",
        "empty": False,
        "nullable": False,
    },
    "utilisateur": {
        "required": False,
        "type": "string",
        "regex": "^[a-z][-a-z0-9_]*$",
        "nullable": False,
    },
    "init": {
        "required": False,
        "type": "string",
        "empty": False,
        "nullable": False,
    },
    "commande": {
        "required": False,
        "type": "string",
        "empty": False,
        "nullable": False,
    },
}
