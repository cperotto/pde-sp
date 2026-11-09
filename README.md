# pde-sp

Replication code for **"Os movimentos da acessibilidade: interações entre regulação, uso do solo e mobilidade em São Paulo entre 2013 e 2022"** (*The movements of accessibility: interactions between regulation, land use and mobility in São Paulo between 2013 and 2022*), a master's thesis in Public Policy at Insper (2025).

The study evaluates how access to formal employment changed in São Paulo between 2013 and 2022 — before and after the city's Strategic Master Plan (PDE, Lei nº 16.050/2014) — and isolates the contribution of each component (transport network, job distribution, population distribution) through ceteris paribus scenarios.

---

## Repository structure

```
pde-sp/
├── 01_dataPrep/          # Data preparation pipeline
├── 02_access/            # Accessibility index computation and analysis
├── 03_plots/             # Visualization scripts and output figures
└── scenarios.json        # Scenario definitions for ceteris paribus analysis
```

### 01_dataPrep — Data preparation

Scripts run in numbered order. Each step produces inputs for the next.

| Script | Description |
|---|---|
| `01_iptuAddresses.py` | Filters residential properties from the IPTU cadastre (São Paulo city open data), extracting addresses for housing stock estimation |
| `02_iptuCoordinates.py` | Geocodes IPTU residential addresses to geographic coordinates |
| `03_travelTimes.py` | Computes door-to-door travel time matrices using [r5py](https://r5py.readthedocs.io/), combining GTFS feeds and OpenStreetMap road network. Covers multimodal trips (public transit + walking/cycling) with up to 3 transfers and a 60-minute threshold |
| `04_jobsCoordinatesNew.py` | Primary geocoding of RAIS employment microdata (2013 and 2021). Applies cascading heuristics: exact CEP + street number match → CEP match with spatial interpolation → approximate CEP with fuzzy street name matching |
| `05_jobsCoordinatesGeopy.ipynb` | Fallback geocoding for unmatched RAIS records via Nominatim (OpenStreetMap) |
| `06_jobsCoordinatesSchool.py` | Geocoding for additional destination types |
| `06_mergingDestinations.py` | Merges geocoded employment records into a unified destinations dataset |
| `07_eda.py` | Exploratory data analysis on input datasets |
| `08_gradeCenso.py` | Interpolates census population data (IBGE statistical grid, 200m resolution) to the H3 hexagonal grid using area-weighted interpolation via [tobler](https://pysal.org/tobler/) |

### 02_access — Accessibility computation

| Script | Description |
|---|---|
| `08_access___scenarios.py` | Computes cumulative accessibility indices for all scenarios defined in `scenarios.json`. The index counts reachable jobs within 60 minutes, weighted by hexagon population |
| `09_decomposingEffects.py` | Decomposes accessibility variation between 2013 and 2022 by component, producing spatial maps of absolute and percentage changes |
| `10_elasticities.py` | Estimates the elasticity of the accessibility index with respect to each component (jobs, housing, network) by geographic area (municipality, EETU, TGE) |
| `11_bvMoranClustering.py` | Bivariate Local Moran statistics to identify spatial clusters of accessibility change correlated with land use and network changes |
| `run.sh` | Runs the full analysis pipeline sequentially |

### 03_plots — Visualizations

Jupyter notebooks for figures used in the thesis, organized by theme:

| Notebook / folder | Content |
|---|---|
| `instrumentos.ipynb` | Maps of PDE instruments (EETU and TGE boundaries) |
| `moran.ipynb` | Global and local Moran index plots |
| `non_linearity.ipynb` | Analysis of non-additive component interactions |
| `scenario_comparison.ipynb` | Comparative visualizations across ceteris paribus scenarios |
| `rais_georref.ipynb` | Quality assessment of RAIS geocoding results |
| `maup/` | MAUP sensitivity analysis: Moran index stability across H3 resolutions for population and employment aggregation |
| `percents/` | Local Moran maps for percentage accessibility changes |
| `plots/` | Final figures exported for the thesis |

### scenarios.json

Defines the six scenarios computed in the analysis:

| Scenario ID | Origins | Destinations | Network | Purpose |
|---|---|---|---|---|
| `real___2013` | 2013 | 2013 | 2013 | Baseline |
| `real___2022` | 2022 | 2021 | 2022 | Observed end state |
| `jobs___solo` | 2013 | 2021 | 2013 | Isolated effect of job redistribution |
| `housing___solo` | 2022 | 2013 | 2013 | Isolated effect of population redistribution |
| `network___solo` | 2013 | 2013 | 2022 | Isolated effect of network changes |
| `jobs_housing___solo` | 2022 | 2021 | 2013 | Combined land use effect (no network change) |

---

## Data requirements

The scripts expect a `data/` directory (not versioned) at the repository root with the following inputs:

| Data | Source | Years |
|---|---|---|
| RAIS employment microdata | Ministério do Trabalho e Emprego | 2013, 2021 |
| IBGE statistical grid (population) | IBGE Censo Demográfico | 2010, 2022 |
| GTFS feeds (public transit) | SPTrans / EMTU / CPTM / Metrô | 2013, 2022 |
| IPTU cadastre | Prefeitura de São Paulo (open data) | 2013, 2022 |
| EETU boundaries | PDE / SMUL | — |
| TGE boundaries (economic zones) | PDE / SMUL | — |
| São Paulo municipality boundary (`sp.geojson`) | IBGE | — |
| IBGE street address reference | IBGE Endereços | — |

Travel time matrices are stored as Parquet files.

---

## Dependencies

The pipeline runs on Python 3.10+. Install all dependencies with:

```bash
pip install -r requirements.txt
```

Key libraries: `geopandas`, `h3pandas`, `tobler`, `libpysal`, `esda` (spatial); `r5py` (routing); `fuzzywuzzy`, `geopy` (geocoding); `matplotlib`, `mapclassify` (visualization).

---

## Spatial unit

All outputs use the [H3](https://h3geo.org/) hexagonal grid at **resolution 9** (~0.1 km² per hexagon), chosen for its isotropic distance properties and stability in spatial autocorrelation tests (Moran index) across aggregation resolutions.

---

## Citation

Perotto, C. C. (2025). *Os movimentos da acessibilidade: interações entre regulação, uso do solo e mobilidade em São Paulo entre 2013 e 2022.* Dissertação (Mestrado em Políticas Públicas) — Insper, São Paulo.
