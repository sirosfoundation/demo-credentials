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

## Known gaps

- Light mode only. Dark variants were optional on previous credentials
  (ops-tasks#18) and are left out here.
- No list or thumbnail view, which previous credentials treated as a separate
  deliverable.
- `vat-id` nests its real content under `administrative_unit`, so those
  placeholders map to claim paths such as
  `["administrative_unit", "vat_id"]` rather than to a top-level claim. The
  `validity_period` entries are an array, so the dates are
  `["administrative_unit", "validity_period", 0, "start_date"]`.
