from __future__ import annotations

import re

MUTATION_TERMS = frozenset(
    {
        "admin",
        "create",
        "delete",
        "drop",
        "edit",
        "mutate",
        "patch",
        "post",
        "purge",
        "put",
        "reload",
        "remove",
        "restart",
        "save",
        "update",
        "write",
    }
)

READ_ONLY_SAFETY_PROMPT = (
    "GeoServer MCP v1 is read-only. Create, update, delete, reload, purge, and other "
    "GeoServer mutation or admin-write actions are unsupported in v1. Use only read-only "
    "inspection tools, and tell the user when a requested mutation is unsupported in v1."
)


def is_mutation_name(name: str) -> bool:
    normalized_parts = {part for part in re.split(r"[^A-Za-z0-9]+|_", name.lower()) if part}
    return any(part in MUTATION_TERMS for part in normalized_parts)
