from pathlib import Path

import numpy as np
import pandas as pd
import pytest


@pytest.mark.parametrize("metric", ["quantity_kg", "value_eur"])
def test_eurostat_world_equals_intra_plus_extra(metric: str) -> None:
    """Check Eurostat partner-group reconciliation for every country-year-flow."""
    project_root = Path(__file__).resolve().parents[1]
    path = project_root / "data/processed/beer_trade_clean.csv"

    df = pd.read_csv(path)

    pivot = df.pivot(
        index=["country", "year", "flow"],
        columns="partner",
        values=metric,
    )

    required = ["WORLD", "INT_EU27_2020", "EXT_EU27_2020"]

    assert len(pivot) == 378
    assert pivot[required].notna().all().all()

    calculated_total = pivot["INT_EU27_2020"] + pivot["EXT_EU27_2020"]

    np.testing.assert_allclose(
        pivot["WORLD"],
        calculated_total,
        rtol=0,
        atol=1,
    )
