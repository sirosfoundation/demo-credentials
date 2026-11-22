# Proposed card designs — WE BUILD PA4 credentials

**These are a starting point for a designer, not finished assets.** They exist so
that the conversation about how business credentials should look starts from
something concrete rather than from a blank page, and so the engineering
constraints are visible before any time is spent in Penpot.

Nothing here is referenced by a `*.vctm.json`. Adopting a card means exporting
the real design, embedding it as a `svg_templates` entry, and adding the
matching `svg_id` to each claim.

See sirosfoundation/ops-tasks#47 for the PA4 work these belong to.

## What is here

| File | |
| --- | --- |
| `pa4-cards-proposal.svg` | All five cards on one sheet, filled with sample data. Start here. |
| `<slug>_card_v1.svg` | The individual templates, with `{{placeholder}}` text. |
| `make_pa4_cards.py` | Generates the five cards. |
| `make_pa4_sheet.py` | Composes the sheet and substitutes the sample data. |
| `check_placeholders.py` | Checks every placeholder against the catalogue's schemas. Run it after any edit. |

The generators are scaffolding. If the design is taken into Penpot, as the
Student ID and mDL were, they can be deleted — they exist to keep five cards
consistent while the layout is still moving, not to replace a designer.

## The idea

Business credentials have no portrait. That frees the space a personal
credential spends on a photograph, and it removes the single strongest visual
cue that tells a holder which card they are looking at. So the proposal leans
on three things instead:

- **One layout for all five**, so the family reads as a set: type label, the
  organisation or counterparty, the identifier, a field grid, and a footer band
  naming who vouches for it.
- **An accent spine and mark** down the left edge, a different hue per
  credential, carrying the only per-credential colour on an otherwise neutral
  card. Navy for EBWOID, forest for EUCC, violet for VAT ID, sienna for
  eInvoice, deep cyan for eReceipt.
- **The amount as the headline** on eInvoice and eReceipt, because for those
  two the number is what a person is actually looking for.

## Constraints a design has to respect

- **365×243**, matching every existing card here.
- **Placeholders must be text.** `draft-ietf-oauth-sd-jwt-vc` section 4.5.1.2.2
  does not allow non-text placeholders. This is what ruled out `{{portrait}}` on
  the scanned passport in sirosfoundation/ops-tasks#18, and it is why these
  cards carry no logo slot per issuer.
- **Every placeholder needs a matching `svg_id`** on a claim in the type
  metadata, and `svg_id` must match `^[A-Za-z_][A-Za-z0-9_]*$`.
- **Field values vary in length.** The sheet is filled with real sample values
  for this reason: `Besloten Vennootschap` and `Exempelbolaget Inköp AB` are
  the kind of strings that overflow a column sized against `Active`.
- **The footer band starts at y=194**, so the last value baseline has to stay
  above roughly y=186. The generator raises an error rather than let a field
  row slide under the band, which is a mistake the first draft of these cards
  actually made.

## Placeholders

These are the complete sets. They are not invented here: `registry-cli`
generates the WE BUILD type metadata from the catalogue's JSON Schemas and
derives each `svg_id` from the claim's path - the leaf name, or the whole path
joined with underscores when two claims share a leaf
(sirosfoundation/registry-cli#62). `check_placeholders.py` reimplements that
derivation and fails if a card uses anything else, so run it after any edit.

| Credential | `svg_id` |
| --- | --- |
| EBWOID | `name` `id` `issuing_authority` `issuing_country` `date_of_expiry` `attestation_legal_category` `trust_anchor` |
| EUCC | `legal_person_name` `legal_person_id` `legal_form_type` `legal_person_status` `registration_date` `registration_member_state` `authentic_source_name` `authentic_source_id` `issuance_date` `issuing_authority` `issuing_country` `issuing_jurisdiction` `legal_person_duration` `legal_representative` plus the `registered_address_*`, `share_capital` and `legal_person_activity` leaves |
| VAT ID | `vat_id` `name` `organisation_type` `registered_eu_cross_border_transactions` `vat_id_authentic_source` `authentic_source_country` `location_status` `attestation_legal_category` `trust_anchor` |
| eInvoice | `invoiceNumber` `issueDate` `amountDueForPayment` `InvoiceCurrencyCode` `invoiceTotalVatAmount` `invoiceLifecycleStatus` `seller_name` `buyer_name` `seller_vat` `buyer_vat` `seller_country` `buyer_country` and the rest of the top-level invoice fields |
| eReceipt | `receipt_number` `original_receipt_number` `receipt_timestamp` `type` `total_price_inc_vat` `total_price_exc_vat` `total_vat_amount` `currency_iso_code` `free_text` |

`buyer_name` and `seller_name` show the collision rule: `name` appears under
both parents, so neither may use the short form.

## Fields that cannot be bound yet

Two fields these cards should show are unreachable, both because of how
`registry-cli` reads the schema rather than anything about the design. Each
has a hole in the layout where it belongs.

- **The merchant name on eReceipt.** `merchant` is `{"$ref":
  "#/$defs/merchant"}` and the generator does not resolve `$ref`, so it emits a
  single `merchant` claim with no children and `merchant.name` does not exist.
  This is the field a person uses to recognise a receipt, so the card falls back
  to the receipt number as its headline until it is fixed.
- **The validity dates on VAT ID.** `administrative_unit.validity_period` is an
  array of objects, and the generator does not descend into array items, so
  `start_date` and `end_date` do not exist. The correct claim path would be
  `["administrative_unit", "validity_period", null, "start_date"]`.

Filed as sirosfoundation/registry-cli#63 and sirosfoundation/registry-cli#64. Until they are fixed, a placeholder for
either would render nothing, so neither appears on a card.

## Known gaps

- Light mode only. Dark variants were optional on previous credentials
  (ops-tasks#18) and are left out here.
- No list or thumbnail view, which previous credentials treated as a separate
  deliverable.
