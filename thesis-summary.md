# Thesis summary

**Title:** The movements of accessibility: interactions between regulation, land use and mobility in São Paulo between 2013 and 2022 (*Os movimentos da acessibilidade: interações entre regulação, uso do solo e mobilidade em São Paulo entre 2013 e 2022*)
**Institution:** Insper — Master's in Public Policy
**Advisor:** Prof. Dr. Adriano Borges Ferreira da Costa
**Year:** 2025
**Full text:** [Insper Institutional Repository](https://repositorio.insper.edu.br/entities/publication/82768a2c-ad09-4d51-8e21-bd904c3135fa)

---

## Research questions

The thesis addresses two central questions:

(i) How did access to jobs change in São Paulo between 2013 and 2022?

(ii) To what extent can these changes be attributed to the regulatory changes introduced by the 2014 Strategic Master Plan (*Plano Diretor Estratégico*, PDE)?

As a methodological extension, the research proposes *ceteris paribus* scenarios to isolate the contribution of each component (transport network, job distribution, housing/population distribution) to the cumulative accessibility index.

---

## Introduction

The motivation starts from the premise that cities exist because of the physical proximity between people, activities and infrastructure (Glaeser, 2012). The study takes the municipality of São Paulo as its object and examines the urban changes that took place before (2013) and after (2022) the approval of the PDE. The period is intentionally asymmetric: the PDE came into force in 2014, but its effects on the built environment and the transport network materialize gradually.

Accessibility is the organizing concept. Understood as the potential to reach destinations (jobs, in this case) from an origin location, it captures the interaction between land use and the transport network, the two axes on which the PDE intervenes.

The stated contribution is twofold. On the theoretical side, it deepens the debate on how land use and transport shape access to opportunities across time and space. On the practical side, it informs the review and planning of integrated urban policies and highlights heterogeneous effects across different groups and territories.

---

## Theoretical framework

### Urban public policy and legislation

The chapter draws on the *policy mix* approach to frame the PDE: a master plan is not a single instrument but an articulated set of regulations, incentives and restrictions that operate simultaneously on housing, employment and mobility. The coherence and consistency among these instruments condition the effectiveness of the mix (Howlett and Rayner, 2013).

Empirical evidence indicates that regulations more permissive about building potential lead to more compact urban forms and to larger increases in property prices in areas where more construction is allowed (Anagol, Ferreira and Rexer, 2021, for the case of São Paulo).

### Access to job opportunities

Following Hansen (1959), accessibility is defined as the potential to reach destinations. The literature recognizes that the accessibility index is sensitive both to the transport network and to the spatial distribution of origins and destinations, and that changes in the magnitude and location of these variables have non-linear effects on the indicator.

Existing work predominantly evaluates the introduction of large, high-capacity infrastructure (metros, BRTs). This thesis differs in two ways: it includes lower-frequency public transport (municipal buses, which dominate mobility in the peripheries), and it incorporates land use, a variable comparatively neglected in the literature.

---

## Methodology

### Unit of analysis

H3 hexagonal polygons at resolution 9 (average area of ~0.1 km²), covering the municipality of São Paulo. The hexagonal grid is justified by the isotropy of distances (lower aggregation bias than rectangular grids) and by statistical stability, assessed through Moran indices.

### Modeled components

**Transport network:** multimodal modeling based on GTFS and OpenStreetMap, using the r5py router. Trips are simulated for a representative weekday, with a 60-minute travel time limit. Up to 3 transfers are allowed on public transport; walking and cycling are also included as active modes.

**Population distribution:** 2010 and 2022 Demographic Censuses, interpolated to the H3 grid.

**Job distribution:** RAIS (2013 and 2021), excluding the public sector, duplicated establishments and outliers above the 99th percentile. Custom geocoding with a match rate of 95.5–95.9%, applying cascading heuristics (CEP and street number match → interpolation → Nominatim/OSM).

### Cumulative accessibility index

The index counts the total number of jobs reachable within 60 minutes from each hexagon (Equation I), weighted by the resident population of the origin hexagon (Equation II). The weighting turns a measure of place into a measure of people.

### *Ceteris paribus* scenarios

Four scenarios isolate the contribution of each component to the 2022 index relative to 2013:
- **Scenario I:** changes only the job distribution (2021), keeping the 2013 network and population
- **Scenario II:** changes only the population distribution (2022), keeping the 2013 network and jobs
- **Scenario III:** changes only the transport network (2022), keeping the 2013 land use
- **Scenario IV:** changes jobs and network, keeping the 2013 population

The polarity and magnitude of each scenario's deviations from the baseline scenario (2013) and from the observed outcome (2022) make it possible to decompose the actual change in accessibility among its components.

---

## The São Paulo case

### 2014 Strategic Master Plan (PDE)

The PDE (Law No. 16,050/2014) sets guidelines for urban development through 2029. Two instruments are central to this study:

**Urban Transformation Structuring Axes (*Eixos de Estruturação da Transformação Urbana*, EETU):** these delimit blocks within the areas of influence around high- and medium-capacity corridors (150 to 600 meters from the axes), with high building potential. The goal is housing densification near transport. The delimited area is ~5.5 km².

**Job Generation Territories (*Territórios de Geração de Emprego*, TGE):** areas with urban planning incentives and potentially fiscal ones to attract firms, aiming to decentralize jobs. In practice, only 2 areas received effective fiscal incentives: implementing the economic instruments depends on later regulation that was not consolidated during the period.

### Land use changes (2013–2022)

**Population:** an increase of 405,123 inhabitants (+3.6% relative to 2013), of whom 22.3% live in TGE. The central region lost residents (a cluster of lower values confirmed by spatial autocorrelation). The peripheries concentrated the population growth.

**Jobs:** a reduction of 218,548 formal jobs (−9.27%). In EETU: −62,472 (−9.51%); in TGE: −128,846 (−12.73%). The COVID-19 pandemic accounts for part of this decline.

### Changes in the transport network

Rail and metro expansion: Metro Lines 4 and 5 and a new monorail line (Line 15), increasing supply along specific corridors. In the municipal bus system, three new corridors were implemented (Ponte Baixa, Berrini, Itaquera/Líder), but the system also accumulated operational cuts that particularly affected the peripheries.

### Observed accessibility

The average municipal index fell by **17.6%** between 2013 and 2022. By PDE-delimited area:
- EETU: −12.9% (smaller than the municipal average, suggesting that the network expansion partially cushioned the decline)
- TGE: −15.9%

Regions near the municipal boundaries recorded **percentage gains** in access to jobs. This behavior runs against the general trend and is associated with the rail and metro expansion in those areas.

---

## Scenario simulation and decomposition of accessibility

The *ceteris paribus* scenarios show that the change observed in 2022 is **smaller** than the change estimated by the isolated scenarios. This indicates that the components do not operate additively: interactions among them amplify the total decline beyond the sum of the parts.

**Hierarchy of components:**

1. **Transport network (Scenario III):** the largest negative contribution to the decline in accessibility. The reduction in municipal bus services, especially in peripheries with no rail or metro alternative, is the main driver.

2. **Job distribution (Scenario I):** also contributed negatively; the contraction of the formal labor market and the absence of effective decentralization widen the decline.

3. **Population/housing distribution (Scenario II):** the only component with a **positive** contribution to the index, particularly in EETU areas, where housing densification near transport improved per capita accessibility.

Spatially, territories with a decline in all scenarios simultaneously are zones where vulnerabilities overlap: reduced transport supply, unfavorable job redistribution and a low housing stock.

---

## Discussion

### Assessment by component and elasticities

The elasticity of the accessibility index with respect to each component varies by territory. In general, increasing the number of jobs has a stronger effect on the percentage change in accessibility. This suggests that policies to attract firms (such as the TGE) would have a greater potential impact than equivalent housing densification policies, if effectively implemented.

The elasticity analysis identifies areas where interventions would yield more than proportional gains, guiding the spatial prioritization of policy instruments.

### Institutional challenges

The PDE incorporates principles aligned with accessibility-oriented development but defines no operational targets or indicators to monitor progress toward its objectives. Two specific institutional problems are identified:

(i) **Mismatch between urban planning and mobility:** the PDE directs densification to the EETU, but the transport network that justifies delimiting these areas does not depend exclusively on the municipality (metro and rail are a state responsibility). During the period, municipal bus services were cut in ways that contradict the PDE's objectives.

(ii) **Fragility of the economic instruments (TGE):** the planned tax incentives depend on later regulation that was not consolidated. Only 2 areas were covered. The literature suggests that even when implemented, these effects tend to be short-lived and concentrated in the first years (Rathelot and Sillard, 2008).

---

## Conclusion

The thesis concludes that the widespread decline in accessibility in São Paulo between 2013 and 2022 is geographically heterogeneous and multi-determined. The transport network is the component with the greatest explanatory weight, but its deterioration in the peripheries cannot be separated from the lack of coordination between urban planning (PDE/municipal) and mobility planning (partly state-level).

The PDE instruments aimed at housing densification (EETU) show partially positive results: the smaller decline in accessibility in these areas relative to the municipal average suggests that densification near transport worked in the right direction. The instruments aimed at job decentralization (TGE) did not produce the expected effects, owing to the incomplete implementation of the incentives.

**Acknowledged limitations:** RAIS does not capture informal jobs, potentially underestimating or distorting spatial patterns in the peripheries. The study also does not assess the sensitivity of the index to different travel time thresholds or to variations in the modeled departure times.

**Future agenda:** incorporate informality in the labor and housing markets; investigate the gap between potential and effective (behavioral) accessibility; assess equity of access across income, gender and race groups.
