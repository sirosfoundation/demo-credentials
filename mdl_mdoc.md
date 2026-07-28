---
doctype: org.iso.18013.5.1.mDL
namespace: org.iso.18013.5.1
formats: mddl
background_color: "#1a365d"
text_color: "#ffffff"
---

# mDL (mdoc-only)

A Mobile Driving Licence (ISO/IEC 18013-5) test credential with **no
sd-jwt counterpart** — it declares `doctype`/`namespace` and no `vct` at
all. It exists to exercise the mdoc/MDDL pipeline end to end:

- Discovery of an mdoc-only credential (no `vct:` front matter).
- Every CDDL value type the MDDL generator maps: `tstr`, `full-date`,
  `tdate`, `bstr`, `uint`, `bool`, and `array`.
- A genuine two-level nested container claim (`driving_privileges` containing
  `codes`), authored via real markdown indentation, to exercise structured
  claims being emitted as a single element rather than flattened into dotted
  leaf claims.
- A leaf array claim with no children (`nationalities`), which should get a
  populated `value_type` of its own rather than being dropped.

## Claims

- `family_name` "Family Name" (string): Last name(s) or surname(s) of the mDL holder [mandatory]
- `given_name` "Given Name" (string): First name(s) of the mDL holder [mandatory]
- `birth_date` "Date of Birth" (date): Date of birth of the mDL holder [mandatory]
- `issue_date` "Issue Date" (date): Date when the mDL was issued [mandatory]
- `expiry_date` "Expiry Date" (date): Date when the mDL expires [mandatory]
- `issuing_country` "Issuing Country" (string): Alpha-2 country code of the issuing authority's country [mandatory]
- `issuing_authority` "Issuing Authority" (string): Name of the issuing authority [mandatory]
- `document_number` "Document Number" (string): Licence number assigned by the issuing authority [mandatory]
- `portrait` "Portrait" (image): Portrait image of the mDL holder [mandatory]
- `un_distinguishing_sign` "UN Distinguishing Sign" (string): Distinguishing sign per ISO/IEC 18013-1:2018, Annex F [mandatory]
- `driving_privileges` "Driving Privileges" (array): Driving privileges held by the mDL holder [mandatory]
  - `vehicle_category_code` "Vehicle Category" (string): Vehicle category code per ISO 18013-5 / Vienna Convention [mandatory]
  - `issue_date` "Privilege Issue Date" (date): Date when this privilege was issued
  - `expiry_date` "Privilege Expiry Date" (date): Date when this privilege expires
  - `codes` "Restriction Codes" (array): Restriction or condition codes for this privilege
    - `code` "Code" (string): Restriction or condition code [mandatory]
    - `sign` "Sign" (string): Sign of the code (e.g. "=", "<", ">")
    - `value` "Value" (string): Value associated with the code
- `administrative_number` "Administrative Number" (string): Audit control number assigned by the issuing authority
- `sex` "Sex" (integer): Sex per ISO/IEC 5218 (0=not known, 1=male, 2=female, 9=not applicable)
- `height` "Height" (integer): Height of the mDL holder in centimetres
- `weight` "Weight" (integer): Weight of the mDL holder in kilograms
- `eye_colour` "Eye Colour" (string): Eye colour of the mDL holder
- `hair_colour` "Hair Colour" (string): Hair colour of the mDL holder
- `birth_place` "Place of Birth" (string): Country and municipality/state/province where the mDL holder was born
- `resident_address` "Resident Address" (string): Place where the mDL holder resides
- `portrait_capture_date` "Portrait Capture Date" (datetime): Date and time when the portrait was taken
- `age_in_years` "Age in Years" (integer): Age of the mDL holder in years
- `age_birth_year` "Birth Year" (integer): Year when the mDL holder was born
- `age_over_18` "Age Over 18" (boolean): Whether the mDL holder is 18 years or older
- `issuing_jurisdiction` "Issuing Jurisdiction" (string): Country subdivision code (ISO 3166-2) of the issuing jurisdiction
- `nationalities` "Nationalities" (array<string>): Nationalities of the mDL holder (ISO 3166-1 alpha-2)
- `resident_city` "Resident City" (string): City where the mDL holder lives
- `resident_state` "Resident State" (string): State/province/district where the mDL holder lives
- `resident_postal_code` "Resident Postal Code" (string): Postal code of the mDL holder
- `resident_country` "Resident Country" (string): Country where the mDL holder lives (ISO 3166-1 alpha-2)
- `family_name_national_character` "Family Name (National Characters)" (string): Family name using full UTF-8 character set
- `given_name_national_character` "Given Name (National Characters)" (string): Given name using full UTF-8 character set
- `signature_usual_mark` "Signature / Usual Mark" (image): Image of the signature or usual mark of the mDL holder
