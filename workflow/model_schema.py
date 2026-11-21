"""Output shapes for the local model's constrained JSON decoder."""


def object_fields(**fields):
    return {"type": "object", "properties": fields, "required": list(fields),
            "additionalProperties": False}


def items(schema, maximum):
    return {"type": "array", "items": schema, "maxItems": maximum}


TEXT = {"type": "string"}
BOOLEAN = {"type": "boolean"}
SCHEMAS = {
    "cli-testing": object_fields(scenarios=items(object_fields(
        id=TEXT, args=items(TEXT, 12), markdown=TEXT, filename=TEXT,
        mode={"enum": ["stdout", "output_file", "preserve_file"]},
    ), 8)),
    "inspect": object_fields(paths=items(TEXT, 6), run_tests=BOOLEAN),
    "review": object_fields(
        verdict={"enum": ["approve", "request_changes"]}, summary=TEXT,
        findings=items(object_fields(path=TEXT, line={"type": "integer", "minimum": 1},
                                     problem=TEXT, return_to={"enum": ["design", "implementation"]}), 6),
    ),
}
