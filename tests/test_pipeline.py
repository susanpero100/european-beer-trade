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
