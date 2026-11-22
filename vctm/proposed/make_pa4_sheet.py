#!/usr/bin/env python3
"""Compose the five proposed cards onto one sheet, filled with sample data.

Placeholder values come from the WE BUILD catalogue's own sample payloads
wherever they exist, so the sheet shows what the cards look like with real
field lengths rather than with {{placeholder}} text, which is the thing that
usually hides an overflow problem.
"""

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
CARDS = ["ebwoid", "eucc", "vat-id", "einvoice", "ereceipt"]

TITLES = {
    "ebwoid": "EBWOID — Business Wallet Owner ID",
    "eucc": "EUCC — EU Company Certificate",
    "vat-id": "VAT ID — VAT Identification",
    "einvoice": "eInvoice",
    "ereceipt": "eReceipt",
}

# Sample values. Those marked SIROS are the demo-tenant data added to
# helm-charts; the rest are from the catalogue's sample-data payloads.
SAMPLES = {
    # EBWOID — SIROS demo tenant (issuer_documents_ebwoid.json, user 100)
    "name": "Exempelbolaget Handel AB",
    "id": "SEBOLREG.556012-3456",
    "issuing_authority": "Bolagsverket",
    "issuing_country": "SE",
    "date_of_expiry": "2028-12-31",
    "attestation_legal_category": "PuB-EAA",
    # EUCC — ds004-eucc-sd-jwt-sample.json
    "legal_person_name": "Example Trading Company Ltd",
    "legal_person_id": "NLNHR.68750110",
    "legal_form_type": "Besloten Vennootschap",
    "legal_person_status": "Active",
    "registration_date": "2015-03-18",
    "registration_member_state": "NL",
    "authentic_source_name": "Kamer van Koophandel",
    # VAT ID — vat-id-sd-jwt-sample.json
    "name": "KLM Royal Dutch Airlines",
    "vat_id": "NL001234567B01",
    "organisation_type": "N.V.",
    "registered_eu_cross_border_transactions": "Yes",
    "authentic_source_country": "NL",
    "vat_id_authentic_source": "Belastingdienst",
    # eInvoice — eInvoice-sd-jwt-sample.json
    "seller_name": "Exempelbolaget Handel AB",
    "invoiceNumber": "INV-2026-000123",
    "amountDueForPayment": "14 250.00",
    "InvoiceCurrencyCode": "EUR",
    "issueDate": "2026-11-02",
    "invoiceTotalVatAmount": "2 850.00",
    "invoiceLifecycleStatus": "active",
    "buyer_name": "Exempelbolaget Inköp AB",
    # eReceipt — e-receipt-sd-jwt-sample.json
    "receipt_number": "RCP-2026-889102",
    "original_receipt_number": "RCP-2026-889044",
    "total_price_inc_vat": "14 250.00",
    "currency_iso_code": "EUR",
    "receipt_timestamp": "2026-11-04 09:41",
    "total_vat_amount": "2 850.00",
    "total_price_exc_vat": "11 400.00",
    "type": "B2B payment",
}


def fill(svg):
    """Replace {{placeholder}} with its sample value, flagging any we lack."""
    missing = set()

    def swap(match):
        key = match.group(1)
        if key not in SAMPLES:
            missing.add(key)
            return match.group(0)
        return SAMPLES[key]

    return re.sub(r"\{\{([a-zA-Z_0-9]+)\}\}", swap, svg), missing


def inner(svg):
    """Strip the outer <svg> wrapper so the card can be nested in a group."""
    body = re.sub(r"^<svg[^>]*>", "", svg.strip())
    return re.sub(r"</svg>\s*$", "", body)


def unique_ids(svg, suffix):
    """Namespace defs ids, since five cards share one document."""
    for name in ("bg", "card"):
        svg = svg.replace(f'id="{name}"', f'id="{name}_{suffix}"')
        svg = svg.replace(f"url(#{name})", f"url(#{name}_{suffix})")
    return svg


def main():
    cols, gap, pad = 2, 46, 44
    cw, ch = 365, 243
    caption = 30
    rows = (len(CARDS) + cols - 1) // cols
    width = pad * 2 + cols * cw + (cols - 1) * gap
    height = pad * 2 + 46 + rows * (ch + caption + gap)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" fill="none">',
        f'<rect width="{width}" height="{height}" fill="#FFFFFF"/>',
        f'<text x="{pad}" y="{pad + 10}" font-family="Arial" font-size="17" font-weight="bold" '
        f'fill="#0C0E11">WE BUILD PA4 credentials — proposed card designs</text>',
        f'<text x="{pad}" y="{pad + 30}" font-family="Arial" font-size="11" fill="#718096">'
        f'One layout, five accents. Shown with sample data at real field lengths. '
        f'365×243, Arial, text-only placeholders.</text>',
    ]

    all_missing = set()
    for index, slug in enumerate(CARDS):
        with open(os.path.join(HERE, f"{slug}_card_v1.svg")) as handle:
            svg = handle.read()

        svg, missing = fill(svg)
        all_missing |= missing

        x = pad + (index % cols) * (cw + gap)
        y = pad + 46 + (index // cols) * (ch + caption + gap)

        out.append(
            f'<text x="{x}" y="{y + 14}" font-family="Arial" font-size="12" '
            f'font-weight="bold" fill="#4A5568">{TITLES[slug]}</text>'
        )
        out.append(f'<g transform="translate({x} {y + caption - 6})">')
        out.append(unique_ids(inner(svg), slug.replace("-", "_")))
        out.append("</g>")

    out.append("</svg>")

    sheet = os.path.join(HERE, "pa4-cards-proposal.svg")
    with open(sheet, "w") as handle:
        handle.write("\n".join(out) + "\n")

    print(f"wrote {sheet}  ({width}x{height})")
    if all_missing:
        print("placeholders with no sample value:", sorted(all_missing))
    else:
        print("every placeholder has a sample value")


if __name__ == "__main__":
    main()
