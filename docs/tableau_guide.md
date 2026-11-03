# Tableau Dashboard Guide

Workbook: `tableau/European_Beer_Trade_Dashboard.twbx`
Dashboard: **European Beer Trade Dashboard**

## Data sources

| Source | File | Used for |
|---|---|---|
| `beer_trade_kpis` | `data/processed/beer_trade_kpis.csv` | Country-year KPIs (export share, export volume) |
| `beer_trade_integrated` | `data/processed/beer_trade_integrated.csv` | Trade flows by partner (intra-EU vs extra-EU) |

Both files are produced by `uv run python run_pipeline.py`.

## Worksheets

1. **EU Export Share Map**
2. **EU-27 Beer Export Volume (2019–2025)**
3. **Export Share Winners & Losers**
4. **Intra-EU vs Extra-EU Export Growth**

## Calculated fields

| Field | Formula (simplified) | Meaning |
|---|---|---|
| Export Share Change (pp) | `{FIXED country: MAX(IF year=2025 THEN export_share_pct END)} - {FIXED country: MAX(IF year=2019 THEN export_share_pct END)}` | Change in a country's share of EU-27 export volume between 2019 and 2025, in percentage points |
| Export Volume 2019 | `{FIXED country, partner: SUM(IF year=2019 AND flow="EXPORT" THEN quantity_kg END)}` | Export quantity (kg) in 2019 |
| Export Volume 2025 | `{FIXED country, partner: SUM(IF year=2025 AND flow="EXPORT" THEN quantity_kg END)}` | Export quantity (kg) in 2025 |
| Export Growth 2019-2025 (%) | `IF Volume2019 != 0 THEN (Volume2025 - Volume2019) / Volume2019 * 100 END` | Export volume growth between 2019 and 2025; undefined if 2019 volume is zero |

The `FIXED` level-of-detail expressions compute values per country (and partner) independently of the filters in the view.

## Filters applied

Filters defined on the `beer_trade_integrated` source (worksheet **Intra-EU vs Extra-EU Export Growth**):

| Filter | Values kept | Reason |
|---|---|---|
| `flow` | `EXPORT` | The analysis focuses on exports |
| `partner` | `INT_EU27_2020` (intra-EU), `EXT_EU27_2020` (extra-EU) | Compares the two destination groups without `WORLD`, which would double count them |
| `country` | `CZ`, `ES`, `IE` | The three countries highlighted in the analysis (Czechia, Spain, Ireland) |

## Open the dashboard

1. Install Tableau Desktop (or Tableau Public Desktop).
2. Open `tableau/European_Beer_Trade_Dashboard.twbx` (double-click or File > Open).
3. Select the **European Beer Trade Dashboard** tab at the bottom.

## Refresh the dashboard

1. Rebuild the data from the project root:
   ```bash
   uv run python run_pipeline.py
   ```
2. Open the workbook in Tableau.
3. For each source (`beer_trade_kpis`, `beer_trade_integrated`): Data > source name > **Edit Data Source**, check that the file points to the regenerated CSV in `data/processed/`, then use Data > **Refresh Data Source**.
4. Save the workbook (a `.twbx` embeds a copy of the data, so it must be saved after refreshing).

## Known limitations

- The years 2019 and 2025 are written directly in the calculated fields. Changing the analysis period requires editing these formulas.
- The workbook stores the data path as `Data/processed` (capital D). This works on Windows but may fail on case-sensitive systems (macOS/Linux); re-point the source if Tableau reports a missing file.
- Export growth for 2019 is undefined in the KPI file (no 2018 data), consistent with `docs/quality_note.md`.