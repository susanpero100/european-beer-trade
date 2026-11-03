# Data Quality Note — European Beer Trade Dynamics

**Scope:** EU-27, 2019–2025, beer made from malt (HS 2203).  
**Sources:** Eurostat DS-059341 and World Bank WDI.

## Coverage and Quality Checks

| Validation | Result |
|---|---|
| Eurostat raw → cleaned observations | 2,268 → 1,134 |
| World Bank country-year observations | 189 (27 countries × 7 years) |
| Missing source values / duplicate business keys | 0 |
| Integrated observations / join match rate | 1,134 / 100% |
| Unmatched or multiplied rows | 0 |
| WORLD = intra-EU + extra-EU (quantity) | 378/378 exact matches |
| Negative checked values / duplicate KPI keys | 0 |
| Annual EU-27 export-share total | 100% each year |

## Key Decisions

- Preserved frozen raw CSV and JSON snapshots; standardized World Bank ISO3 identifiers to Eurostat ISO2 codes.
- Reshaped Eurostat data into separate quantity (kg) and value (EUR) columns; joined sources on country and year with `many_to_one` validation.
- Used `WORLD` observations for aggregate export KPIs to avoid double counting intra-/extra-EU components.
- Retained 27 undefined export-growth observations for 2019, because the preceding year is outside the scope.
- Excluded incomplete UN Comtrade API responses from the final analysis.

## Sensitivity Check

Using 2024 instead of 2025 preserves the positive export-share changes for Ireland, Czechia and Spain. Aggregate export volume declined **8.48%** from 2019 to 2024 versus **14.87%** from 2019 to 2025. Poland's export-share change switches from **+0.42 percentage points** (2019–2024) to **−0.65** (2019–2025), indicating endpoint sensitivity.

## What cannot be trusted

- **Causal explanations:** Trade patterns do not establish the effects of strategy, prices or policy.
- **Bilateral or global-share claims:** Partner categories are aggregated; market shares use EU-27 reporting countries only.
- **Unit values as product prices:** EUR/kg may change with product composition and destination mix.
- **Finality of 2025 data:** Recent observations may be revised.
- **Underlying source accuracy:** Passing validation checks does not independently verify official statistics.

**Assessment:** Suitable for descriptive EU-27 beer trade comparisons, but not for causal inference or destination-level investment decisions.

