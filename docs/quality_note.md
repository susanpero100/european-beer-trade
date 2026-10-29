# Data Quality Note — European Beer Trade Dynamics

**Scope:** EU-27, 2019–2025, beer made from malt (HS 2203).  
**Sources:** Eurostat DS-059341 and World Bank World Development Indicators.

## 1. Data Quality Checks

| Check | Result |
|---|---|
| Eurostat raw observations | 2,268 |
| Missing Eurostat observation values | 0 |
| Duplicate Eurostat business keys | 0 |
| Prepared Eurostat observations | 1,134 |
| World Bank country-year observations | 189 |
| Missing population / GDP per capita | 0 / 0 |
| Integrated observations | 1,134 |
| Join match rate | 100% |
| Unmatched or multiplied rows | 0 |
| WORLD = INTRA-EU + EXTRA-EU, by quantity | 378/378 exact matches |
| Duplicate country-year KPI rows | 0 |
| Negative values in checked source measures | 0 |
| Annual export share totals | 100% for every year |

## 2. Cleaning and Integration Decisions

- Retained Eurostat's original raw CSV and World Bank API JSON snapshots.
- Converted the Eurostat long format into separate `quantity_kg` and `value_eur` columns without aggregating away trade-flow information.
- Standardized World Bank ISO3 country identifiers to Eurostat ISO2 identifiers.
- Joined on country and year with `many_to_one` validation.
- Used only `WORLD` partner observations for country-level export shares and aggregate trends, avoiding double counting.
- Kept the 27 missing export-growth values for 2019 as undefined because 2018 is outside the analysis period.
- Retained quantities in kilograms and monetary values in their original currencies; no currency or volume conversions were invented.
- Excluded partial UN Comtrade preview downloads from the analytical pipeline following API rate-limit errors.

## 3. Sensitivity Analysis

Using 2024 rather than 2025 as the final year confirms positive export-share changes for Czechia, Ireland and Spain.

Aggregate export volume changes by **−8.48% from 2019 to 2024**, compared with **−14.87% from 2019 to 2025**.

However, some country conclusions are endpoint-sensitive: Poland's share change is +0.42 percentage points through 2024 but −0.65 through 2025.

## 4. What cannot be trusted

- **Causality:** Observed trade changes cannot establish the effects of company strategy, consumer behavior or government policy.
- **Bilateral trade claims:** The selected Eurostat data contains only WORLD, intra-EU and extra-EU partner categories, not individual trading partners.
- **Global market shares:** Export shares are relative to the 27 EU reporting countries, not all countries worldwide.
- **Unit values as prices:** EUR/kg ratios can reflect product composition and destination changes, not just selling-price changes.
- **2025 stability:** The most recent observations may be revised; endpoint-sensitive findings require caution.
- **Source completeness beyond checks:** Passing coverage, duplicate and reconciliation checks does not independently verify the correctness of underlying official statistics.

**Overall assessment:** The dataset is suitable for descriptive comparisons of EU-27 beer export volumes, relative export shares and intra-/extra-EU patterns over 2019–2025, subject to the limitations above.

