# Data Sources and Collection Methodology

## Project: European Beer Trade Dynamics

**Research question:** How have beer trade flows between European countries evolved, and which countries have gained or lost export market share over time?

**Geographical scope:** 27 European Union member states.

**Period:** 2019–2025.

**Product:** Beer made from malt, HS code 2203.

## 1. Eurostat — International Trade in Goods

**Source owner:** Eurostat, European Commission.

**Dataset:** International trade of EU and non-EU countries since 2002 by HS2-4-6.

**Dataset identifier:** DS-059341.

**Access method:** Manual download from Eurostat Data Browser, SDMX-CSV 2.0 format.

**Data extraction date:** 29 October 2026.

**Selected filters:**
- Frequency: Annual.
- Reporter: all 27 EU member states.
- Product: HS 2203 — Beer made from malt.
- Trade flows: Imports and exports.
- Partners: WORLD, INTRA-EU27 and EXTRA-EU27.
- Indicators: Trade value in EUR and quantity in KG.
- Years: 2019–2025.

**Original observations:** 2,268.

**Raw file:** `data/raw/eurostat/beer_trade_raw.csv`

**Grain:** Reporter country × year × partner group × trade flow × indicator.

**Main limitation:** Partner data consists of three aggregate categories. It does not identify individual destination countries or bilateral trade relationships.

**Reuse conditions:** Eurostat data may generally be reused free of charge with appropriate source attribution and indication of any modifications, subject to dataset-specific restrictions. Source: https://ec.europa.eu/eurostat/about-us/communicating-disseminating-statistics

**Attribution:** Source: Eurostat, International Trade in Goods, dataset DS-059341. Data filtered, reshaped and analysed by the project authors.

## 2. World Bank — World Development Indicators

**Source owner:** World Bank.

**Access method:** Automated API collection using Python and the `requests` library.

**API base URL:** https://api.worldbank.org/v2/country

**Indicators:**
- `SP.POP.TOTL` — Population, total.
- `NY.GDP.PCAP.CD` — GDP per capita, current US$.

**Selected filters:**
- Countries: 27 EU member states, identified using ISO3 codes.
- Years: 2019–2025.
- Response format: JSON.

**Collection procedure:** The script `src/european_beer_trade/collect_worldbank.py` requests the data through the World Bank API, handles pagination, retries failed requests and validates country-year coverage.

**Pagination:** Four pages per indicator using `per_page=50`.

**Expected coverage:** 189 observations per indicator (27 countries × 7 years).

**Raw files:**
- `data/raw/worldbank/population.json`
- `data/raw/worldbank/gdp_per_capita_usd.json`

**Grain:** Country × year × indicator.

**Data extraction date:** Recorded automatically in each JSON snapshot using `extracted_at`.

**Reuse conditions:** World Development Indicators is licensed under Creative Commons Attribution 4.0 (CC BY 4.0). Reuse requires attribution and indication of changes, subject to applicable dataset-specific conditions. Source: https://datacatalog.worldbank.org/search/dataset/0037712/world-development-indicators

**Attribution:** Source: World Bank, World Development Indicators (SP.POP.TOTL and NY.GDP.PCAP.CD). Data collected through the API and transformed by the project authors.

## 3. Data Integration

Eurostat and World Bank data are integrated using `country` and `year`.

World Bank ISO3 country codes are mapped to Eurostat ISO2 country codes before integration.

**Integration relationship:** Many-to-one, because Eurostat contains multiple trade observations per country-year, while the prepared World Bank dataset contains one observation per country-year.

**Integration quality checks:**
- Eurostat prepared observations: 1,134.
- World Bank prepared observations: 189.
- Integrated observations: 1,134.
- Match rate: 100%.
- Unmatched observations: 0.
- Unexpected row multiplication: 0.

The final integrated dataset is saved as:

`data/processed/beer_trade_integrated.csv`

## 4. Important Analytical Limitations

- Export market share refers to each EU country's share of the combined worldwide beer exports reported by the 27 EU member states. It is not a share of total global beer exports.
- Intra-EU and extra-EU figures are components of WORLD totals and must not be added to WORLD.
- Quantities are measured in kilograms, not litres.
- GDP per capita is expressed in current USD, whereas trade values are expressed in EUR.
- The 2025 observations may be revised in future source releases.
- Changes in export unit values do not necessarily represent price changes for identical products.
- This observational dataset does not establish why countries gained or lost export share.

## 5. Reproducibility

Rebuild the prepared datasets, integrated data, KPIs and Python figures using:

`uv run python run_pipeline.py`

Refresh World Bank raw snapshots using:

`uv run python src/european_beer_trade/collect_worldbank.py`

The main pipeline rebuilds outputs from stored raw files without requiring an internet connection.

