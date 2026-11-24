This is a set of demo credentials used with registry.siros.org

`vctm/` holds the published documents; `.github/workflows/publish.yml` pushes
them to the `vctm` branch that registry.siros.org serves.

The WE BUILD business credentials are generated rather than written:
`tools/make_webuild_vctms.py` derives their claims, `svg_id`s and labels from
the catalogue's JSON Schemas, the same way registry-cli does, and supplies
the three things a schema cannot carry - per-claim disclosure, display names
and a rendering colour. Re-run it after an upstream schema change:

    ./tools/make_webuild_vctms.py            # fetch the schemas from the catalogue
    ./tools/make_webuild_vctms.py <dir>      # read <name>-sd-jwt.json from <dir>

`ebwoid.vctm.json` is the exception, hand-written: every claim is `sd: never`
by an integrity rule its schema cannot express.
