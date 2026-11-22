#!/usr/bin/env python3
"""Check that every {{placeholder}} in the cards binds to a real claim.

A placeholder only renders if some claim in the type metadata carries a
matching svg_id: the wallet builds svg_id -> claim path from the metadata and
substitutes {{svg_id}} textually (wallet-common/src/rendering.ts). A
placeholder with no matching svg_id renders nothing at all, silently.

The ids are not hand-maintained. registry-cli generates the WE BUILD type
metadata from the catalogue's JSON Schemas, and derives svg_id from each
claim's path: the leaf name, or the full path joined with underscores when two
claims share a leaf, and none at all for a container. This script reimplements
that derivation against the schemas and compares it with what the cards use,
so a card cannot drift from the metadata unnoticed.

Usage:

    ./check_placeholders.py            # fetches the schemas from the catalogue
    ./check_placeholders.py <dir>      # uses <slug>-sd-jwt.json from <dir>

Exits non-zero and names every unbound placeholder.
"""

import json
import os
import re
import sys
import urllib.request

# Slug as used in the card filenames -> schema basename in the catalogue.
SCHEMAS = {
    "ebwoid": "ds001-ebwoid",
    "eucc": "ds004-eucc",
    "vat-id": "vat-id",
    "einvoice": "eInvoice",
    "ereceipt": "e-receipt",
}

CATALOG = ("https://raw.githubusercontent.com/webuild-consortium/"
           "webuild-attestation-rulebooks-catalog/main/data-schemas/sd-jwt/")

# Standard JWT/SD-JWT claims are infrastructure, not credential content, and
# registry-cli leaves them out of the claims list.
INFRASTRUCTURE = {"vct", "iss", "sub", "iat", "exp", "nbf", "jti", "cnf", "status"}

PLACEHOLDER = re.compile(r"\{\{([A-Za-z_][A-Za-z0-9_]*)\}\}")


def claim_paths(schema):
    """The claim paths registry-cli emits for a schema.

    Only inline object properties produce children. A $ref is not resolved and
    an array's items are not descended into, which is why some fields a card
    wants are unreachable; see the README.
    """
    paths = []
    for name in sorted(schema.get("properties", {})):
        if name in INFRASTRUCTURE:
            continue
        prop = schema["properties"][name]
        if prop.get("type") == "object" and prop.get("properties"):
            for child in sorted(prop["properties"]):
                paths.append((name, child))
        paths.append((name,))
    return paths


def svg_ids(schema):
    """The svg_id set registry-cli derives for a schema."""
    paths = claim_paths(schema)
    containers = {path[:i] for path in paths for i in range(1, len(path))}

    leaves = {}
    for path in paths:
        if path in containers:
            continue
        leaves[path[-1]] = leaves.get(path[-1], 0) + 1

    ids = set()
    for path in paths:
        if path in containers:
            continue
        ids.add(path[-1] if leaves[path[-1]] == 1 else "_".join(path))
    return ids


def load(slug, directory):
    name = SCHEMAS[slug] + "-sd-jwt.json"
    if directory:
        with open(os.path.join(directory, name)) as handle:
            return json.load(handle)
    with urllib.request.urlopen(CATALOG + name, timeout=30) as response:
        return json.load(response)


def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else None
    here = os.path.dirname(os.path.abspath(__file__))

    failures = 0
    for slug in SCHEMAS:
        available = svg_ids(load(slug, directory))
        with open(os.path.join(here, f"{slug}_card_v1.svg")) as handle:
            used = set(PLACEHOLDER.findall(handle.read()))

        unbound = sorted(used - available)
        status = "ok" if not unbound else "UNBOUND: " + ", ".join(unbound)
        print(f"{slug:<10} {len(used):>2} placeholders, "
              f"{len(available):>2} claims available   {status}")
        failures += len(unbound)

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
