#!/usr/bin/env python3
"""Generate the proposed PA4 business-credential card templates.

One layout grammar, five accents. The cards are SD-JWT VC svg_templates, so
every placeholder is text — draft-ietf-oauth-sd-jwt-vc section 4.5.1.2.2 does
not permit non-text placeholders, which is what ruled out {{portrait}} on the
scanned passport in sirosfoundation/ops-tasks#18.

House conventions, taken from vctm/siros_id_v1.svg: 365x243, Arial, rx 14.5,
1px #BDBDBD stroke, 9px labels, 11px values, 14px headline.
"""

W, H = 365, 243

INK = "#0C0E11"
MUTED = "#718096"
VALUE = "#1A202C"
SUBTLE = "#4A5568"
RULE = "#E2E8F0"
STROKE = "#BDBDBD"


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def label(x, y, text, fill=MUTED):
    return (
        f'<text x="{x}" y="{y}" font-family="Arial" font-size="9" fill="{fill}" '
        f'letter-spacing="0.8" xml:space="preserve">{esc(text)}</text>'
    )


def value(x, y, text, size=11, fill=VALUE, weight=None):
    w = f' font-weight="{weight}"' if weight else ""
    return (
        f'<text x="{x}" y="{y}" font-family="Arial" font-size="{size}" fill="{fill}"'
        f'{w} xml:space="preserve">{esc(text)}</text>'
    )


def glyph(kind, accent):
    """A 24x24 mark at the top right, drawn at x=316 y=20."""
    g = f'<g transform="translate(316 20)" fill="none" stroke="{accent}" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round">'
    if kind == "owner":
        # A wallet: a card tucked behind a rounded pocket.
        g += '<rect x="1.5" y="6" width="21" height="14" rx="3"/><path d="M5 6V3.5h11V6"/><circle cx="17" cy="13" r="1.8"/>'
    elif kind == "certificate":
        # A seal with a ribbon.
        g += '<circle cx="12" cy="9.5" r="7"/><circle cx="12" cy="9.5" r="3"/><path d="M8.5 16l-1.5 6 5-2.5 5 2.5-1.5-6"/>'
    elif kind == "tax":
        # A percent mark, for a VAT registration.
        g += '<circle cx="7" cy="7" r="3"/><circle cx="17" cy="17" r="3"/><path d="M19 4L5 20"/>'
    elif kind == "invoice":
        # A document with ruled lines and a folded corner.
        g += '<path d="M4 2h11l5 5v15H4z"/><path d="M15 2v5h5"/><path d="M7.5 12h9M7.5 16h9M7.5 8h4"/>'
    elif kind == "receipt":
        # A receipt with a torn edge.
        g += '<path d="M4.5 2h15v18l-2.5-1.6-2.5 1.6-2.5-1.6-2.5 1.6L7 20l-2.5 1.6z"/><path d="M8 7h8M8 11h8M8 15h5"/>'
    return g + "</g>"


def card(accent, tint, kind, type_label, headline, identifier,
         fields, footer, amount=None):
    """fields: four (label, placeholder) pairs laid out two by two."""
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" fill="none">',
        "<defs>",
        f'  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="{H}" gradientUnits="userSpaceOnUse">',
        '    <stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#F7F9FC"/>',
        "  </linearGradient>",
        f'  <clipPath id="card"><rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14.5"/></clipPath>',
        "</defs>",
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14.5" fill="url(#bg)" stroke="{STROKE}"/>',
        # The accent spine identifies the credential family at a glance.
        f'<g clip-path="url(#card)"><rect x="0" y="0" width="6" height="{H}" fill="{accent}"/></g>',
        glyph(kind, accent),
        label(26, 32, type_label.upper(), accent),
        value(26, 66, headline, size=14, fill=INK, weight="bold"),
        value(26, 85, identifier, size=11, fill=SUBTLE),
    ]

    # The footer band starts at y=194, so the last value baseline has to stay
    # above roughly y=186 to clear it. That leaves room for two field rows on a
    # plain card, but only one once an amount block is in front of them, which
    # is why the amount cards carry their remaining two fields in the footer.
    cols = (26, 190)
    top = 112
    if amount:
        out.append(value(26, 116, amount, size=19, fill=accent, weight="bold"))
        top = 140

    rows = 1 if amount else 2
    if len(fields) > rows * 2:
        raise ValueError(
            f"{type_label}: {len(fields)} fields do not fit in {rows} row(s); "
            "move the remainder into the footer"
        )

    out.append(f'<line x1="26" y1="{top}" x2="339" y2="{top}" stroke="{RULE}"/>')

    for index, (lab, placeholder) in enumerate(fields):
        x = cols[index % 2]
        y = top + 24 + (index // 2) * 34
        out.append(label(x, y, lab.upper()))
        out.append(value(x, y + 14, placeholder))

    # Footer strip, echoing the band on siros_id_v1.svg. It takes one or two
    # label/value pairs, in the same two columns as the grid above.
    out.append(f'<rect x="12" y="194" width="342" height="38" rx="8" fill="{tint}"/>')
    for index, (lab, placeholder) in enumerate(footer[:2]):
        x = cols[index % 2]
        out.append(label(x, 211, lab.upper()))
        out.append(value(x, 225, placeholder, size=11, fill=VALUE))
    out.append("</svg>")

    return "\n".join(out) + "\n"


CARDS = {
    "ebwoid": dict(
        accent="#1A365D", tint="#EEF2F8", kind="owner",
        type_label="Business Wallet Owner ID",
        headline="{{name}}",
        identifier="{{id}}",
        fields=[
            ("Issuing authority", "{{issuing_authority}}"),
            ("Country", "{{issuing_country}}"),
            ("Expires", "{{date_of_expiry}}"),
            ("Attestation category", "{{attestation_legal_category}}"),
        ],
        footer=[("Issued by", "{{issuing_authority}}")],
    ),
    "eucc": dict(
        accent="#14532D", tint="#EDF4EF", kind="certificate",
        type_label="EU Company Certificate",
        headline="{{legal_person_name}}",
        identifier="{{legal_person_id}}",
        fields=[
            ("Legal form", "{{legal_form_type}}"),
            ("Status", "{{legal_person_status}}"),
            ("Registered", "{{registration_date}}"),
            ("Member State", "{{registration_member_state}}"),
        ],
        footer=[("Authentic source", "{{authentic_source_name}}")],
    ),
    "vat-id": dict(
        accent="#4C1D95", tint="#F2EEFA", kind="tax",
        type_label="VAT Identification",
        headline="{{name}}",
        identifier="{{vat_id}}",
        fields=[
            ("Organisation type", "{{organisation_type}}"),
            ("EU cross-border", "{{registered_eu_cross_border_transactions}}"),
            ("Source country", "{{authentic_source_country}}"),
            ("Attestation category", "{{attestation_legal_category}}"),
        ],
        # The validity dates this row would rather show are unreachable; see
        # "Fields that cannot be bound yet" in the README.
        footer=[("Issued by", "{{vat_id_authentic_source}}")],
    ),
    "einvoice": dict(
        accent="#7C2D12", tint="#F8EFEA", kind="invoice",
        type_label="eInvoice",
        headline="{{seller_name}}",
        identifier="Invoice {{invoiceNumber}}",
        amount="{{amountDueForPayment}} {{InvoiceCurrencyCode}}",
        fields=[
            ("Issued", "{{issueDate}}"),
            ("VAT total", "{{invoiceTotalVatAmount}}"),
        ],
        footer=[
            ("Status", "{{invoiceLifecycleStatus}}"),
            ("Buyer", "{{buyer_name}}"),
        ],
    ),
    "ereceipt": dict(
        accent="#0C4A6E", tint="#EBF3F8", kind="receipt",
        type_label="eReceipt",
        # The merchant name belongs here and is unreachable; see "Fields that
        # cannot be bound yet" in the README. The receipt number is the only
        # identifying field that does bind, so it carries the headline until
        # that is fixed.
        headline="Receipt {{receipt_number}}",
        identifier="{{original_receipt_number}}",
        amount="{{total_price_inc_vat}} {{currency_iso_code}}",
        fields=[
            ("Date", "{{receipt_timestamp}}"),
            ("Excluding VAT", "{{total_price_exc_vat}}"),
        ],  # noqa: E262 - merchant name goes here once it is addressable
        footer=[
            ("VAT", "{{total_vat_amount}}"),
            ("Receipt type", "{{type}}"),
        ],
    ),
}


def main():
    import os

    # The cards sit next to this script, wherever it is checked out.
    out_dir = os.path.dirname(os.path.abspath(__file__))

    for slug, spec in CARDS.items():
        path = os.path.join(out_dir, f"{slug}_card_v1.svg")
        with open(path, "w") as handle:
            handle.write(card(**spec))
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
