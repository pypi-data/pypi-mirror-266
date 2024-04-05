{
    **schema_registry.get("question_base"),
    "ébauches": {
        "required": True,
        "type": "dict",
        "empty": False,
        "valuesrules": {"type": "string", "nullable": True},
    },
    "tests": {
        "required": True,
        "type": "list",
        "empty": False,
        "schema": {
            "required": True,
            "type": "dict",
            "schema": "test_prog",
        },
    },
}
