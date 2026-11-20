"""Output shapes for the local model's constrained JSON decoder."""


def object_fields(**fields):
    return {"type": "object", "properties": fields, "required": list(fields),
            "additionalProperties": False}


def items(schema, maximum):
    return {"type": "array", "items": schema, "maxItems": maximum}


TEXT = {"type": "string"}
BOOLEAN = {"type": "boolean"}
EDIT = object_fields(path=TEXT, old=TEXT, new=TEXT)
CRITERION = object_fields(
    id=TEXT, requirement=TEXT, evidence=TEXT,
    provenance={"enum": ["confirmed", "inferred"]}, given=TEXT, when=TEXT, then=TEXT,
)
SCHEMAS = {
    "requirements": object_fields(
        status={"enum": ["ready", "blocked"]}, summary=TEXT, actors=items(TEXT, 4),
        constraints=items(TEXT, 6), assumptions=items(TEXT, 6), questions=items(TEXT, 4),
        criteria=items(CRITERION, 6),
        checks=object_fields(completeness=BOOLEAN, consistency=BOOLEAN,
                             traceability=BOOLEAN, feasibility=BOOLEAN, testability=BOOLEAN),
    ),
    "design": object_fields(
        approach=TEXT, architecture_fit=TEXT, tests=TEXT,
        targets=items(object_fields(path=TEXT, symbol=TEXT, action={"enum": ["edit", "add"]},
                                    change=TEXT), 6),
        context=items(TEXT, 4),
    ),
    "implementation": object_fields(edits=items(EDIT, 8)),
    "testing": object_fields(edits=items(EDIT, 6)),
    "inspect": object_fields(paths=items(TEXT, 6), run_tests=BOOLEAN),
    "review": object_fields(
        verdict={"enum": ["approve", "request_changes"]}, summary=TEXT,
        findings=items(object_fields(path=TEXT, line={"type": "integer", "minimum": 1},
                                     problem=TEXT, return_to={"enum": ["design", "implementation"]}), 6),
    ),
}
