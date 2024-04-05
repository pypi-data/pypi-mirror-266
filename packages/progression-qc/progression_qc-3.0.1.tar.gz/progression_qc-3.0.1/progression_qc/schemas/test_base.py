{
    "nom": {"required": False, "type": "string"},
    "sortie": {
        "required": False,
        "type": ["string", "integer"],
        "nullable": False,
    },
    "rétroactions": {
        "required": False,
        "type": "dict",
        "schema": "rétroactions",
    },
    "caché": {"required": False, "type": "boolean"},
}
