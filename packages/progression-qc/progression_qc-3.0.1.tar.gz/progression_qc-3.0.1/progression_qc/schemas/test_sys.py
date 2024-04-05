{
    **schema_registry.get("test_base"),
    "validation": {
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
}
