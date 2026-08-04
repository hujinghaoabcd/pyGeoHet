# Static reference fixtures

Reference files in this directory are data outputs, not runtime calls to external software.

`ntd_classic_reference.json` records:

- the SHA-256 hash and column mapping of the 185-row NTD disease dataset;
- published `gdverse`/`GD` factor-detector values;
- published interaction labels and risk significance counts;
- the `gdverse` upper-tail ecological convention;
- pyGeoHet's primary two-sided ecological results;
- tolerances used for comparison.

The GPL-associated raw CSV is intentionally not redistributed. A developer who has the source archive can run:

```bash
python tools/validate_ntd_reference.py \
  "path/to/GeoDetector_2018_Example(Disease Dataset).csv"
```

The validator checks the input hash before comparing results.
