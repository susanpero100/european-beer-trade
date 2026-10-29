
# European Beer Trade Dynamics

## Research Question

How have beer trade flows among EU countries evolved from 2019 to 2025, and which countries have gained or lost export market share?

## Project Overview

This project analyzes beer made from malt (HS 2203) across the 27 European Union member states from 2019 to 2025.

It integrates trade statistics from Eurostat with population and GDP per capita indicators from the World Bank to support descriptive comparisons of export performance, trade geography and market-share changes.

## Data Sources

- **Eurostat:** International trade of EU and non-EU countries since 2002 by HS2-4-6 (DS-059341).
- **World Bank:** World Development Indicators, accessed through the public API.

Detailed collection procedures, filters and limitations are documented in [Data Sources](docs/data_sources.md).

## Installation

Requires Python 3.13 and uv.

```bash
uv sync
```

## Rebuild the Analysis

The project can be rebuilt offline from the stored raw data:

```bash
uv run python run_pipeline.py
```

This command generates cleaned datasets, integrated data, KPIs and Python figures.

## Refresh World Bank Data

To collect fresh World Bank observations using the API:

```bash
uv run python src/beer_trade/collect_worldbank.py
```

Then rerun the main pipeline.

The Eurostat raw CSV is currently a saved manual download. See `docs/data_sources.md` for its extraction method.

## Quality Checks

Run the automated tests:

```bash
uv run pytest -q
```

Check coding standards and formatting:

```bash
uv run ruff check src/beer_trade tests
uv run ruff format --check src/beer_trade tests
```

Run static type checking:

```bash
uv run mypy src/beer_trade
```

## Key Findings

1. Ireland, Czechia and Spain increased their shares of combined EU-27 worldwide beer exports between 2019 and 2025.
2. Spain and Ireland experienced growth in extra-EU exports, whereas Czechia's growth was driven by intra-EU exports.
3. Total reported export volume across EU-27 countries declined by approximately 14.87% between 2019 and 2025, while aggregate export unit value increased by approximately 15.41%.

These findings are descriptive rather than causal.

## Outputs

- `data/processed/beer_trade_integrated.csv` — integrated trade and economic indicators.
- `data/processed/beer_trade_kpis.csv` — country-year KPIs.
- `reports/figures/` — three Python-generated EDA charts.
- `docs/quality_note.md` — data quality assessment.

## Tableau

The Tableau dashboard will use `data/processed/beer_trade_kpis.csv` and, where needed, `data/processed/beer_trade_integrated.csv`.

After rebuilding the pipeline, refresh the corresponding CSV data sources in Tableau. The packaged workbook will be added to the `tableau/` directory.

## Limitations

Export shares are calculated relative to combined worldwide beer exports reported by EU-27 countries, not the full global market. The selected Eurostat data does not contain bilateral country-level partner flows.

See [Quality Note](docs/quality_note.md) for further limitations and sensitivity analysis.

