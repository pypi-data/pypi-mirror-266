[![PyPI](https://img.shields.io/badge/python-3.11-blue.svg)]()

# PyBAYWATCH
This package incorporates a set of Bayesian hierarchical Proxy System Models (PSMs, i.e., forward data models) for sedimentary paleoclimate records in Python, including:
- [BAYSPAR](https://github.com/jesstierney/BAYSPAR): for TEX$_{86}$ in paleotemperature proxy (Tierney and Tingley, 2014, 2015).
- [BAYSPLINE](https://github.com/jesstierney/BAYSPLINE): for U$^{K'}_{37}$ in alkenone paleothermometer (Tierney and Tingley, 2018).
- [BAYMAG](https://github.com/jesstierney/BAYMAG): for Mg/Ca in planktic foraminifera (Tierney et al., 2019).
- [BAYFOX](https://github.com/jesstierney/bayfoxm): for global plankit foraminifera $\delta^{18}$O(Malevich et al., 2019).
- [BAYMBT](https://github.com/jesstierney/BayMBT): for the branched GDGT MBT5Me proxy in soils, peats, and lakes (Dearing Crampton-Flood et al., 2020; Martínez-Sosa et al., 2021).

It include two modes: (i) Python wrappers for the original Matlab codebase, and (ii) pure Python versions.
The detailed supporting information is provided below:

| Model     | Python wrapper      | Pure Python       |
|-----------|---------------------|-------------------|
| BAYSPAR   | ✅         | ✅       |
| BAYSPINE  | ❌ (due to a non-open Matlab toolbox)  | ✅          |
| BAYMAG    | ✅         | ✅       |
| BAYFOX    | ✅         | ✅       |
| BAYMBT    | ✅         | ✅       |

## References
- Tierney, J. E. & Tingley, M. P. A Bayesian, spatially-varying calibration model for the TEX86 proxy. Geochimica et Cosmochimica Acta 127, 83–106 (2014).
- Tierney, J. E. & Tingley, M. P. A TEX86 surface sediment database and extended Bayesian calibration. Sci Data 2, 150029 (2015).
- Tierney, J. E. & Tingley, M. P. BAYSPLINE: A New Calibration for the Alkenone Paleothermometer. Paleoceanography and Paleoclimatology 33, 281–301 (2018).
- Tierney, J. E., Malevich, S. B., Gray, W., Vetter, L. & Thirumalai, K. Bayesian Calibration of the Mg/Ca Paleothermometer in Planktic Foraminifera. Paleoceanography and Paleoclimatology 34, 2005–2030 (2019).
- Malevich, S. B., Vetter, L. & Tierney, J. E. Global Core Top Calibration of δ18O in Planktic Foraminifera to Sea Surface Temperature. Paleoceanography and Paleoclimatology 34, 1292–1315 (2019).
- Dearing Crampton-Flood, E., Tierney, J. E., Peterse, F., Kirkels, F. M. S. A. & Sinninghe Damsté, J. S. BayMBT: A Bayesian calibration model for branched glycerol dialkyl glycerol tetraethers in soils and peats. Geochimica et Cosmochimica Acta 268, 142–159 (2020).
- Martínez-Sosa, P. et al. A global Bayesian temperature calibration for lacustrine brGDGTs. Geochimica et Cosmochimica Acta 305, 87–105 (2021).
