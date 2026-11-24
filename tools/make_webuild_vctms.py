#!/usr/bin/env python3
"""Generate the WE BUILD type metadata this repository publishes.

The catalogue's JSON Schemas are the source of truth for these credentials.
registry-cli generates the published type metadata from them, and this script
generates what we publish the same way, so a consumer gets what the registry
would give it rather than a copy that drifts.

Output goes to ../vctm/<slug>.vctm.json. Consumers take that, generated once
here rather than transcribed per repository: copying by hand is what went
wrong before, when two of these types were pasted out of registry output and
arrived with no `sd`, no rendering and a name taken straight off the schema
title.

Three things the schemas cannot tell us are supplied here:

  * `sd`, because each rulebook states disclosure in a prose table, not in the
    schema. The DISCLOSURE maps below transcribe that table; every entry cites
    its row. registry-cli reads disclosure out of property descriptions and
    these schemas carry none, so without this every claim would default to
    "allowed" - which for several of them is the opposite of the rule.
  * `display`, since a schema title is not a card name and a property name is
    not a label.
  * `rendering`, which the schema has no place for.

`svg_id` is not supplied: it is derived from the claim path by exactly the rule
in sirosfoundation/registry-cli#62, so the chart and the registry agree on what
a template may address.

Not covered: EBWOID, whose every claim is `sd: never` by an integrity rule
the schema cannot express and whose claim set comes from the rulebook's own
encoding table (vctm/ebwoid.vctm.json, hand-written); and EUCC, still
hand-maintained in sirosfoundation/siros-id-stack#28.

Usage:  ./make_webuild_vctms.py            # fetch the schemas from the catalogue
        ./make_webuild_vctms.py <dir>      # read <name>-sd-jwt.json from <dir>
"""

import collections
import json
import os
import re
import sys
import urllib.request

CATALOG = ("https://raw.githubusercontent.com/webuild-consortium/"
           "webuild-attestation-rulebooks-catalog/main/data-schemas/sd-jwt/")

# Standard JWT/SD-JWT claims are infrastructure, not credential content.
INFRASTRUCTURE = {"vct", "iss", "sub", "iat", "exp", "nbf", "jti", "cnf", "status"}

SVG_ID_SHAPE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
SVG_ID_ILLEGAL = re.compile(r"[^A-Za-z0-9_]")


# --------------------------------------------------------------------------
# Claim derivation - mirrors registry-cli's rulebook-catalog plugin.
# --------------------------------------------------------------------------

def claim_paths(schema):
    """The claim paths registry-cli emits for a schema.

    It descends one level into an inline object and no further, does not
    resolve $ref, and does not descend into array items. Those limits are
    why some attributes a rulebook defines have no claim at all; see
    "Attributes with no claim" in README-webuild.md.
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


def svg_ids(paths):
    """path -> svg_id, by the rule in registry-cli#62."""
    containers = {path[:i] for path in paths for i in range(1, len(path))}

    leaves = collections.Counter(
        path[-1] for path in paths if path not in containers)

    ids, used = {}, set()
    for path in paths:
        if path in containers:
            continue
        candidate = path[-1] if leaves[path[-1]] == 1 else "_".join(path)

        identifier = SVG_ID_ILLEGAL.sub("_", candidate)
        if identifier and not SVG_ID_SHAPE.match(identifier):
            identifier = "_" + identifier
        if not identifier or not SVG_ID_SHAPE.match(identifier) or identifier in used:
            continue

        ids[path] = identifier
        used.add(identifier)
    return ids


def describe(schema, path):
    """The schema's description for a claim path, if it has one."""
    prop = schema["properties"][path[0]]
    for segment in path[1:]:
        prop = prop.get("properties", {}).get(segment, {})
    return prop.get("description", "")


def label_for(path, labels):
    """A human label: the override, else the leaf name made readable."""
    dotted = ".".join(path)
    if dotted in labels:
        return labels[dotted]
    return path[-1].replace("_", " ").strip().capitalize()


def build(schema, spec, ids):
    paths = claim_paths(schema)
    required = set(schema.get("required", []))

    claims = []
    for path in paths:
        display = collections.OrderedDict([
            ("locale", "en-US"),
            ("label", label_for(path, spec["labels"])),
        ])
        description = describe(schema, path)
        if description:
            display["description"] = description

        claim = collections.OrderedDict([
            ("path", list(path)),
            ("display", [display]),
        ])
        if len(path) == 1 and path[0] in required:
            claim["mandatory"] = True

        disclosure = spec["disclosure"].get(".".join(path))
        if disclosure:
            claim["sd"] = disclosure
        if path in ids:
            claim["svg_id"] = ids[path]

        claims.append(claim)

    return collections.OrderedDict([
        ("vct", schema["properties"]["vct"]["const"]),
        ("name", schema["title"]),
        ("description", schema.get("description", "")),
        ("display", [collections.OrderedDict([
            ("locale", "en-US"),
            ("name", spec["display_name"]),
            ("description", spec["display_description"]),
            ("rendering", collections.OrderedDict([
                ("simple", collections.OrderedDict([
                    ("background_color", spec["background"]),
                    ("text_color", "#FFFFFF"),
                ])),
            ])),
        ])]),
        ("claims", claims),
    ])


# --------------------------------------------------------------------------
# Per-credential facts the schemas do not carry.
# --------------------------------------------------------------------------

CREDENTIALS = {
    # ----------------------------------------------------------- VAT ID
    "vat_id": dict(
        schema="vat-id",
        display_name="VAT Identification",
        display_description=(
            "Confirms a VAT identification number and the organisation it "
            "belongs to, as held by the tax administration."),
        background="#4C1D95",
        labels={
            "administrative_unit.vat_id": "VAT identification number",
            "administrative_unit.name": "Registered name",
            "administrative_unit.organisation_type": "Organisation type",
            "administrative_unit.address": "Registered address",
            "administrative_unit.economic_operator": "Economic operator",
            "administrative_unit.economic_activity": "Economic activity",
            "administrative_unit.validity_period": "Validity period",
            "administrative_unit.registered_eu_cross_border_transactions":
                "Registered for EU cross-border transactions",
            "issuer.vat_id_authentic_source": "Authentic source",
            "issuer.authentic_source_country": "Authentic source country",
            "issuer.location_status": "Location status",
            "attestation_legal_category": "Attestation category",
            "trust_anchor": "Trust anchor",
        },
        # rb-vat-id section 5.1, the Disclosable column. Its legend reads
        # MUST = "SHALL be selectively disclosable", MUST NOT = "SHALL NOT be
        # selectively disclosable, always present in plain text".
        disclosure={
            "administrative_unit.vat_id": "never",
            "administrative_unit.name": "never",
            "administrative_unit.validity_period": "never",
            "administrative_unit.economic_operator": "never",
            "administrative_unit.registered_eu_cross_border_transactions": "never",
            "administrative_unit.organisation_type": "always",
            "administrative_unit.address": "always",
            "administrative_unit.economic_activity": "always",
            "issuer.vat_id_authentic_source": "never",
            "issuer.authentic_source_country": "never",
            "issuer.location_status": "never",
            "attestation_legal_category": "never",
            "trust_anchor": "never",
        },
    ),
    # --------------------------------------------------------- eInvoice
    "einvoice": dict(
        schema="eInvoice",
        display_name="eInvoice",
        display_description=(
            "An invoice from a seller to a buyer, carried in the wallet and "
            "presentable without contacting the seller."),
        background="#7C2D12",
        labels={
            "invoiceNumber": "Invoice number",
            "issueDate": "Issued",
            "amountDueForPayment": "Amount due",
            "InvoiceCurrencyCode": "Currency",
            "invoiceTotalVatAmount": "VAT total",
            "invoiceLifecycleStatus": "Status",
            "invoiceFormat": "Invoice format",
            "invoicePayloadHash": "Payload hash",
            "precedingInvoiceReference": "Preceding invoice",
            "paymentInstructions": "Payment instructions",
            "evidenceReferences": "Evidence references",
            "taxSubtotal": "Tax subtotal",
            "BuyerElectronicAddress": "Buyer electronic address",
            "seller.name": "Seller",
            "seller.vat": "Seller VAT number",
            "seller.identifier": "Seller identifier",
            "seller.country": "Seller country",
            "buyer.name": "Buyer",
            "buyer.vat": "Buyer VAT number",
            "buyer.identifier": "Buyer identifier",
            "buyer.country": "Buyer country",
            "attestation_legal_category": "Attestation category",
            "cryptographically_bound_to": "Cryptographically bound to",
        },
        # rb-eInvoice section 5, the Disclosable column.
        disclosure={
            "attestation_legal_category": "never",
            "invoicePayloadHash": "never",
            "precedingInvoiceReference": "never",
            "invoiceLifecycleStatus": "never",
            "cryptographically_bound_to": "never",
            # "MUST, issuer SHALL make selectively disclosable so payment
            # details can be withheld where not required".
            "paymentInstructions": "always",
            "invoiceFormat": "allowed",
            "invoiceNumber": "allowed",
            "issueDate": "allowed",
            "seller": "allowed",
            "buyer": "allowed",
            "BuyerElectronicAddress": "allowed",
            "amountDueForPayment": "allowed",
            "invoiceTotalVatAmount": "allowed",
            "InvoiceCurrencyCode": "allowed",
            "taxSubtotal": "allowed",
            "evidenceReferences": "allowed",
        },
    ),
    # --------------------------------------------------------- eReceipt
    "ereceipt": dict(
        schema="e-receipt",
        display_name="eReceipt",
        display_description=(
            "A till receipt issued by a merchant after a payment, "
            "presentable to an expense system, accounting tool or tax "
            "authority."),
        background="#0C4A6E",
        labels={
            "receipt_number": "Receipt number",
            "original_receipt_number": "Original receipt number",
            "receipt_timestamp": "Date and time",
            "type": "Receipt type",
            "currency_iso_code": "Currency",
            "total_price_inc_vat": "Total including VAT",
            "total_price_exc_vat": "Total excluding VAT",
            "total_vat_amount": "VAT amount",
            "merchant": "Merchant",
            "products": "Line items",
            "vats": "VAT breakdown",
            "payments": "Payments",
            "verifications": "Technical proof",
            "journey": "Journey",
            "attachments": "Attachments",
            "free_text": "Note",
            "custom_attributes": "Custom attributes",
            "attestation_legal_category": "Attestation category",
            "cryptographically_bound_to": "Cryptographically bound to",
        },
        # rb-e-receipt section 3, the Disclosable column.
        disclosure={
            "attestation_legal_category": "never",
            "verifications": "never",
            "type": "always",
            "receipt_number": "always",
            "receipt_timestamp": "always",
            "currency_iso_code": "always",
            "total_price_exc_vat": "always",
            "total_vat_amount": "always",
            "total_price_inc_vat": "always",
            "products": "always",
            "vats": "always",
            "payments": "always",
            "merchant": "allowed",
            "journey": "allowed",
            "free_text": "allowed",
            "custom_attributes": "allowed",
            "original_receipt_number": "allowed",
        },
    ),
}


def load(name, directory):
    filename = name + "-sd-jwt.json"
    if directory:
        with open(os.path.join(directory, filename)) as handle:
            return json.load(handle)
    with urllib.request.urlopen(CATALOG + filename, timeout=30) as response:
        return json.load(response)


def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else None
    here = os.path.dirname(os.path.abspath(__file__))

    for slug, spec in CREDENTIALS.items():
        schema = load(spec["schema"], directory)
        paths = claim_paths(schema)
        ids = svg_ids(paths)

        unknown = set(spec["disclosure"]) - {".".join(p) for p in paths}
        if unknown:
            raise SystemExit(
                f"{slug}: disclosure set for claims the schema does not have: "
                f"{sorted(unknown)}")

        document = build(schema, spec, ids)
        name = f"{slug}.vctm.json"
        path = os.path.join(here, os.pardir, "vctm", name)
        with open(path, "w") as handle:
            json.dump(document, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        print(f"wrote vctm/{name}  "
              f"({len(document['claims'])} claims, {len(ids)} with svg_id)")


if __name__ == "__main__":
    main()
