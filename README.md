# European Beer Trade Dynamics (2019–2025)

## Project Overview

This project investigates how beer trade flows involving the 27 European Union countries evolved between 2019 and 2025, focusing on export volumes, changes in export market shares, and intra-EU versus extra-EU trade patterns.

**Research Question:** How have EU-27 beer export volumes, reported export shares, and intra-/extra-EU trade patterns evolved between 2019 and 2025?

**Decision Maker:** Export strategy managers at European beer producers.

**Business Objective:** Identify changes in competitive export positions and geographical trade patterns to inform further market research and export strategy decisions.

**Scope:**
- Geography: 27 EU member states.
- Period: 2019–2025.
- Product: Beer made from malt (HS 2203).
- Main indicators: export and import volumes (kg), trade values (EUR), export shares (%), annual export growth (%), and exports per capita (kg/person).

## Data Sources

The project integrates two complementary public datasets.

### 1. Eurostat — International Trade in Goods

- Source: Eurostat, dataset DS-059341.
- Product: HS 2203 — Beer made from malt.
- Coverage: EU-27 countries, 2019–2025.
- Trade flows: Imports and exports.
- Partner groups: WORLD, INT_EU27_2020, EXT_EU27_2020.
- Indicators: Trade quantity (kg) and value (EUR).
- Collection method: Manual download of a public SDMX-CSV file.
- Raw file: `data/raw/eurostat/beer_trade_raw.csv`.

### 2. World Bank — World Development Indicators

- Source: World Bank API.
- Indicators:
  - `SP.POP.TOTL`: Total population.
  - `NY.GDP.PCAP.CD`: GDP per capita (current US$).
- Coverage: 27 EU countries, 2019–2025.
- Collection method: Automated API requests with pagination.
- Raw files:
  - `data/raw/worldbank/population.json`
  - `data/raw/worldbank/gdp_per_capita_usd.json`

The two datasets are integrated by country and year.

For source URLs, extraction procedures, filters, coverage and provenance, see `docs/data_sources.md`.

## Data Preparation and Integration

The Python pipeline performs the following operations:

1. Imports and validates the Eurostat raw dataset.
2. Reshapes trade quantities and values into a country-year-partner-flow table.
3. Processes World Bank API responses and standardizes country identifiers.
4. Joins the datasets on country and year.
5. Calculates trade indicators and export market shares.
6. Produces analytical datasets and EDA figures.

### Data Grain

- Eurostat raw data: country × year × partner group × trade flow × indicator.
- Cleaned Eurostat data: country × year × partner group × trade flow.
- World Bank data: country × year.
- Integrated dataset: country × year × partner group × trade flow.
- Final KPI dataset: country × year.

### Integration Validation

| Check | Result |
|---|---|
| Raw Eurostat observations | 2,268 |
| Cleaned Eurostat observations | 1,134 |
| World Bank observations | 189 |
| Integrated observations | 1,134 |
| Country-year observations in KPI dataset | 189 |
| Countries covered | 27 |
| Years covered | 7 |
| Join match rate | 100% |
| Unmatched observations | 0 |
| Row multiplication | None |

The World Bank integration uses a many-to-one relationship and validates that no trade records are lost or duplicated during the join.

## Project Structure

```text
european-beer-trade/
├── README.md
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
├── run_pipeline.py
├── src/
│   └── european_beer_trade/
│       ├── __init__.py
│       ├── collect_worldbank.py
│       ├── collect_comtrade.py
│       ├── prepare_eurostat.py
│       ├── prepare_worldbank.py
│       ├── integrate_data.py
│       ├── calculate_kpis.py
│       └── create_figures.py
├── tests/
│   └── test_pipeline.py
├── data/
│   ├── raw/
│   │   ├── eurostat/
│   │   └── worldbank/
│   └── processed/
├── reports/
│   └── figures/
├── docs/
│   ├── data_sources.md
│   └── quality_note.md
└── tableau/
```

`collect_comtrade.py` is exploratory code from an initial data-collection attempt. UN Comtrade was not used as a source for the final analytical dataset.

## Environment Setup

The project uses Python 3.13 and `uv` for dependency management.

Clone the repository and navigate to the project directory:

```bash
git clone REPOSITORY_URL
cd european-beer-trade
```

Install the required dependencies:

```bash
uv sync
```

The `pyproject.toml` file defines the project dependencies, while `uv.lock` records the resolved dependency versions.

## Run the Data Pipeline

Rebuild the complete analytical dataset and figures from the saved raw data:

```bash
uv run python run_pipeline.py
```

Alternatively, use the installed project command:

```bash
uv run european-beer-trade
```

Both commands execute the preparation, integration, KPI calculation and visualization steps.

The pipeline can be executed offline using the frozen raw snapshots.

## Refresh World Bank Data

To retrieve fresh observations through the World Bank API:

```bash
uv run python src/european_beer_trade/collect_worldbank.py
```

The collection script uses paginated requests and saves raw API responses before processing.

After collecting fresh data, rebuild the analytical outputs:

```bash
uv run python run_pipeline.py
```

The Eurostat source is currently provided as a manually downloaded raw CSV. Its import and subsequent transformations are automated.

## Code Quality and Testing

Run the seven automated business-logic tests:

```bash
uv run pytest -q
```

Check the code with Ruff:

```bash
uv run ruff check src/european_beer_trade tests run_pipeline.py
```

Verify formatting:

```bash
uv run ruff format --check src/european_beer_trade tests run_pipeline.py
```

Run static type checking:

```bash
uv run mypy
```

Ruff checks the pipeline source code, tests and entrypoint. Mypy checks the Python package under `src/european_beer_trade`, as configured in `pyproject.toml`.

The automated tests cover duplicate-key detection, join integrity (including rejection of unmatched country-year records), export-share calculations, trade balance, per-capita exports, export unit value, undefined first-year growth and zero-export edge cases. Run them from the project root after `uv sync`.

## Main Findings

### Finding 1 — Changes in Export Shares

Ireland, Czechia and Spain increased their shares of combined worldwide beer exports reported by EU-27 countries between 2019 and 2025.

Over the same period, the Netherlands, France and Belgium experienced reductions in their respective shares.

These shares measure relative positions within the 27 reporting EU countries, not shares of worldwide beer exports from all countries.

### Finding 2 — Different Geographical Growth Patterns

The geographical composition of export growth differs across countries.

- Spain: extra-EU export volume increased by approximately 44.11%, while intra-EU exports declined by approximately 28.22%.
- Ireland: extra-EU export volume increased by approximately 17.96%, while intra-EU exports declined by approximately 20.15%.
- Czechia: intra-EU export volume increased by approximately 11.10%, while extra-EU exports declined by approximately 17.63%.

These patterns suggest different geographical export dynamics and do not by themselves establish their causes.

### Finding 3 — Declining Volume and Rising Unit Value

The combined beer export volume reported by EU-27 countries decreased by approximately 14.87% between 2019 and 2025.

Over the same period, the aggregate export unit value increased by approximately 15.41%.

This indicates a divergence between exported quantity and average declared value per kilogram. Changes in unit value should not automatically be interpreted as price increases for identical products.

## Business Recommendation

Export strategy managers should prioritize further investigation of countries gaining relative export share, particularly Ireland, Czechia and Spain.

However, geographical trends should guide the next analytical steps:

- Investigate extra-EU export opportunities and underlying destination markets for Spain and Ireland.
- Examine intra-EU market developments and competitive positioning for Czechia.
- Monitor volume declines and changes in export share among established exporters, including the Netherlands, Belgium and Germany.

These recommendations concern **further market assessment**, not immediate investment decisions. Bilateral trade flows, company-level costs, product mix and destination-market demand would be needed before making operational commitments.

## Outputs

The pipeline produces:

- `data/processed/beer_trade_clean.csv` — cleaned Eurostat trade data.
- `data/processed/worldbank_clean.csv` — cleaned World Bank indicators.
- `data/processed/beer_trade_integrated.csv` — integrated trade and economic data.
- `data/processed/beer_trade_kpis.csv` — final country-year trade KPIs.
- `reports/figures/01_export_trend.png` — aggregate export trends.
- `reports/figures/02_share_changes.png` — changes in export share.
- `reports/figures/03_geographic_growth.png` — intra-/extra-EU growth patterns.

## Tableau Dashboard

The Tableau dashboard will use the processed CSV outputs produced by the Python pipeline.

Main planned visualizations include:

1. EU-27 aggregate export-volume trend, 2019–2025.
2. Country-level export share changes.
3. Intra-EU versus extra-EU export patterns.


The packaged workbook is stored in `tableau/European_Beer_Trade_Dashboard.twbx`. It uses two processed CSV outputs of the pipeline: `beer_trade_kpis.csv` and `beer_trade_integrated.csv`.

See [`docs/tableau_guide.md`](docs/tableau_guide.md) for the calculated fields, the filters applied, and the steps to open or refresh the dashboard.

To refresh the dashboard, rerun the Python pipeline (`uv run python run_pipeline.py`), then refresh the CSV data sources in Tableau.

## Data Quality and Limitations

The analysis has the following limitations:

- Export shares refer to the total worldwide beer exports reported by the 27 EU countries, not the entire global export market.
- The Eurostat dataset contains aggregated partner groups rather than bilateral country-to-country trade flows.
- The analysis is descriptive and does not establish causal explanations for trade changes.
- The latest reporting year, 2025, may be subject to data revisions.
- Differences between reported export volume and value may reflect changes in product composition as well as prices.
- Aggregating exports reported by EU countries includes intra-EU movements and should not be interpreted as EU exports exclusively to third countries.

See `docs/quality_note.md` for detailed quality checks, methodological decisions and sensitivity analysis.

## Project Contributors

**Susanna Perotti and Titouan Perron**

This project is developed collaboratively as part of the Albert School Data Foundations Project.

Individual implementation contributions, feature branches and pull-request reviews will be documented after the collaborative GitHub workflow is completed.

## Submission

The final submission will include the Git repository URL and exact assessed commit hash, together with the reproducible Python project, frozen source data, quality documentation and packaged Tableau workbook.

The submission deadline is **4 November 2026 at 23:59**, followed by the oral defence on **5 November 2026**.

