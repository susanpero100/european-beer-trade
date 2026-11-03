import pandas as pd
import pytest

from european_beer_trade.calculate_kpis import calculate_kpis
from european_beer_trade.integrate_data import integrate_data
from european_beer_trade.prepare_eurostat import prepare_data


def test_eurostat_rejects_duplicate_observations():
    """Duplicate business keys must be rejected."""

    raw = pd.DataFrame(
        {
            "reporter": ["AT", "AT"],
            "TIME_PERIOD": [2024, 2024],
            "partner": ["WORLD", "WORLD"],
            "FLOW": ["EXPORT", "EXPORT"],
            "indicators": ["QUANTITY_KG", "QUANTITY_KG"],
            "OBS_VALUE": [100.0, 100.0],
        }
    )

    with pytest.raises(ValueError, match="Duplicate"):
        prepare_data(raw)


def test_integration_preserves_rows():
    """A valid many-to-one join must not multiply trade rows."""

    beer = pd.DataFrame(
        {
            "country": ["AT", "AT"],
            "year": [2024, 2024],
            "partner": ["WORLD", "WORLD"],
            "flow": ["EXPORT", "IMPORT"],
            "quantity_kg": [100.0, 50.0],
            "value_eur": [200.0, 80.0],
        }
    )

    worldbank = pd.DataFrame(
        {
            "country": ["AT"],
            "year": [2024],
            "population": [9_000_000],
            "gdp_per_capita_usd": [50_000.0],
        }
    )

    result = integrate_data(beer, worldbank)

    assert len(result) == 2
    assert result["population"].notna().all()


def test_export_shares_sum_to_100():
    """Country export shares must sum to 100% for each year."""

    rows = []

    for country, export_kg in [("AT", 100.0), ("BE", 300.0)]:
        for flow in ["EXPORT", "IMPORT"]:
            rows.append(
                {
                    "country": country,
                    "year": 2024,
                    "partner": "WORLD",
                    "flow": flow,
                    "quantity_kg": (export_kg if flow == "EXPORT" else 50.0),
                    "value_eur": 200.0,
                    "population": 1_000_000,
                    "gdp_per_capita_usd": 50_000.0,
                }
            )

    result = calculate_kpis(pd.DataFrame(rows))

    assert len(result) == 2
    assert result["export_share_pct"].sum() == pytest.approx(100.0)

    austria_share = result.loc[result["country"] == "AT", "export_share_pct"].iloc[0]

    assert austria_share == pytest.approx(25.0)


def _trade_rows(
    country,
    year,
    export_kg,
    import_kg=50.0,
    export_eur=200.0,
    import_eur=80.0,
    population=1_000_000,
):
    """Build one EXPORT row and one IMPORT row for a country-year."""
    base = {
        "country": country,
        "year": year,
        "partner": "WORLD",
        "population": population,
        "gdp_per_capita_usd": 50_000.0,
    }
    return [
        {**base, "flow": "EXPORT", "quantity_kg": export_kg, "value_eur": export_eur},
        {**base, "flow": "IMPORT", "quantity_kg": import_kg, "value_eur": import_eur},
    ]


def test_trade_balance_and_per_capita_kpis():
    """Trade balance and per-capita exports are computed correctly."""
    df = pd.DataFrame(_trade_rows("AT", 2024, export_kg=100.0))

    result = calculate_kpis(df)
    row = result.iloc[0]

    assert row["trade_balance_kg"] == pytest.approx(50.0)
    assert row["trade_balance_eur"] == pytest.approx(120.0)
    assert row["exports_per_capita_kg"] == pytest.approx(0.0001)
    assert row["export_unit_value_eur_per_kg"] == pytest.approx(2.0)


def test_export_growth_is_undefined_for_first_year():
    """Growth is NaN in the first year and correct afterwards."""
    rows = _trade_rows("AT", 2023, export_kg=100.0) + _trade_rows(
        "AT", 2024, export_kg=150.0
    )

    result = calculate_kpis(pd.DataFrame(rows))

    assert pd.isna(result.loc[result["year"] == 2023, "export_growth_pct"].iloc[0])
    assert result.loc[result["year"] == 2024, "export_growth_pct"].iloc[0] == (
        pytest.approx(50.0)
    )


def test_zero_exports_give_undefined_unit_value():
    """Zero exported quantity must give NaN, not infinity or an error."""
    df = pd.DataFrame(_trade_rows("AT", 2024, export_kg=0.0, export_eur=0.0))

    result = calculate_kpis(df)

    assert pd.isna(result["export_unit_value_eur_per_kg"].iloc[0])


def test_integration_rejects_unmatched_country_year():
    """A trade row with no World Bank match must stop the pipeline."""
    beer = pd.DataFrame(
        {
            "country": ["AT", "BE"],
            "year": [2024, 2024],
            "partner": ["WORLD", "WORLD"],
            "flow": ["EXPORT", "EXPORT"],
            "quantity_kg": [100.0, 200.0],
            "value_eur": [200.0, 400.0],
        }
    )
    worldbank = pd.DataFrame(
        {
            "country": ["AT"],
            "year": [2024],
            "population": [9_000_000],
            "gdp_per_capita_usd": [50_000.0],
        }
    )

    with pytest.raises(ValueError, match="Unmatched"):
        integrate_data(beer, worldbank)
