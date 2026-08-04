# Third-party and scientific-source notices

pyGeoHet is an independent Python implementation. It does not copy source code from the reviewed R, Python, C++, QGIS, MATLAB, or spreadsheet implementations and does not call those projects at runtime.

Reference implementations and papers may be used to define formulas, construct static numerical fixtures, and investigate disagreements. Every reference fixture records its source project or publication, input hash, expected output, tolerance, and known convention differences.

## Stage 2 reviewed sources

The classical-workflow audit reviewed the primary geographical-detector papers and source archives from `GD`, `gdverse`, `geodetector`, and `GeodetectorPy`. The reviewed software is GPL-family licensed. No source code was copied or translated line by line into the MIT-licensed package.

The NTD validation uses a GPL-associated CSV available in a reviewed archive. pyGeoHet does not redistribute that raw file. It stores only numerical outputs, provenance, the input SHA-256 hash, and a validator that the developer can run against a separately obtained copy.

The ecological detector has incompatible historical software conventions. pyGeoHet implements the primary-paper residual-dispersion F ratio, uses a two-sided test by default, and exposes a separately named upper-tail compatibility option. This is a documented statistical choice, not copied package behaviour.

## Scientific anchors

Initial anchors include Wang et al. (2010), Wang, Zhang, and Fu (2016), Wang and Xu (2017), and later method papers listed in `MODEL_INVENTORY.md`.

Licences of future source archives must be audited before any code-level adaptation. Lack of a clear licence means the source may be read for behavioural understanding but must not be copied or translated line by line.
